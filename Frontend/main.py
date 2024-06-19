#!/usr/bin/env python3

import asyncio
import math
import httpx
from nicegui import app, events, ui
from fastapi import FastAPI
from Frontend.router import Router
import Backend.map_preparation.map_preparation as mp
import Backend.map_creation.map_creation as mc
import Backend.quality_check.quality_check as qc
import json
import os
from Frontend.preparation_parameters import Preparation_parameters
from Frontend.yaml_parameters import Yaml_parameters
from Frontend.tooltips import Tooltip_Enum
from Frontend.quality_parameters import Quality_parameters
import time 
from pydantic_yaml import to_yaml_str

# global variables
pgm_ii = any
ii = any
thickness = 3
visibility = True
start_point = tuple
end_point = tuple

yaml_parameters = Yaml_parameters()
preparation_parameters = Preparation_parameters()
tooltip = Tooltip_Enum()
clicked = asyncio.Event()
image_reload_timer = ui.timer(interval=1, callback=lambda: ui.notify('.'))
quality_parameters = Quality_parameters()

picture_name = 'uploaded_file'
complete_yaml = 'uploaded_file.yaml'
complete_picture = 'uploaded_file.jpg'
complete_pgm = 'uploaded_file.pgm'

UPLOAD_DIR = "uploaded_files"

FLAME_RED = '#CD2A23'
FLAME_ORANGE = '#EF7C23'
FLAME_YELLOW = '#F2E738'

os.makedirs(UPLOAD_DIR, exist_ok=True)
image_path = os.path.join(UPLOAD_DIR, complete_picture)
filled_image_path = os.path.join(UPLOAD_DIR, 'filled_image.jpg')
pgm_path = os.path.join(UPLOAD_DIR, complete_pgm)

# make directory with uploaded files accessible to frontend
app.add_static_files(url_path='/uploaded_files', local_directory='uploaded_files')
        
def init(fastapi_app: FastAPI) -> None: 
    # ui.page definiert frontend-Seite mit Route
    @ui.page('/')
    def show():
        router = Router()

        # Hochladen des Bilds ermöglichen
        @router.add('/')
        def show_upload():
            global picture_name
            global yaml_parameters
            ui.label('Upload').classes('text-2xl')
            ui.input('Enter name of Picture', placeholder=picture_name).bind_value_to(yaml_parameters, 'image').tooltip(tooltip.UPLOAD_NAME)
            ui.upload(on_upload=on_file_upload, label="Upload a picture").tooltip(tooltip.UPLOAD_IF)
            
        # Farbpalette zeigen, Hinzufügen
        @router.add('/pencil') 
        def show_pencil():
            ui.label('Pencil').classes('text-2xl')
            pencil()
            
        # Löschen von Inhalten aus Bild 
        @router.add('/eraser')
        def show_eraser():
            ui.label('Eraser').classes('text-2xl')
            eraser()
            # TODO: enable zoom
            
        @router.add('/parameter')
        def show_parameter():
            ui.label('Set YAML Parameters').classes('text-2xl')
            parameter_page_layout()
        
        @router.add('/download')
        def show_download():
            ui.label('Set Resolution and download').classes('text-2xl')
            download_page_layout()
            
        @router.add('/quality')
        def show_quality():
            ui.label('Quality parameters').classes('text-2xl')
            quality_page_layout()
            
        # adding some navigation buttons to switch between the different pages
        with ui.header(elevated=True).style(f'background-color: #3874c8').classes('items-center justify-between'):
            ui.button('Upload', on_click=lambda: router.open(show_upload)).classes('w-32').tooltip(tooltip.UPLOAD_BUTTON)
            ui.button('Pencil', on_click=lambda: router.open(show_pencil)).classes('w-32').tooltip(tooltip.PENCIL_BUTTON)
            ui.button('Eraser', on_click=lambda: router.open(show_eraser)).classes('w-32').tooltip(tooltip.ERASER_BUTTON)
            ui.button('Parameter', on_click=lambda: router.open(show_parameter)).classes('w-32').tooltip(tooltip.DOWNLOAD_BUTTON)
            ui.button('Download', on_click=lambda: router.open(show_download)).classes('w-32').tooltip(tooltip.DOWNLOAD_BUTTON)
            ui.button('Quality', on_click=lambda: router.open(show_quality)).classes('w-32').tooltip(tooltip.QUALITY_BUTTON)
            
        # this places the content which should be displayed
        router.frame().classes('w-full p-4 bg-gray-100')

    # mount path is homepage, secret is randomly chosen
    ui.run_with(fastapi_app, storage_secret='secret') 

def compute_resolution():
    global yaml_parameters
    yaml_parameters.resolution = (preparation_parameters.length/preparation_parameters.pixels).__round__(4)
    
    
def download_page_layout() -> None:
    global ii, image_reload_timer
    ui.label('pgm creation threshold').classes('text-xl cols-span-full').tooltip(tooltip.RESOLUTION)
    pgm_thresh = ui.slider(min=0, max=255, step=1).bind_value(preparation_parameters, 'pgm_threshold').classes('col-span-full').tooltip(tooltip.RESOLUTION)
    ui.label().bind_text_from(pgm_thresh, 'value').classes('col-span-4').tooltip(tooltip.RESOLUTION)
    
    ui.button('Create pgm with set threshold', on_click=create_pgm)
    
    ui.label('Length of the drawn line').classes('text-xl cols-span-full').tooltip(tooltip.RESOLUTION)
    ui.number('Length of the drawn line [m]', value=1.0, format='%.2f', step=0.5).bind_value(preparation_parameters, 'length').classes('col-span-5').tooltip(tooltip.ORIGIN_X)
    ui.notify(f'length set to {preparation_parameters.length}')
    
    ui.label('Pixel length of the drawn line').classes('text-xl') 
    ui.label().bind_text(preparation_parameters, 'pixels')
        
    ui.timer(interval=1.0, callback = compute_resolution)
    ui.label('Resolution [m/px] based on the given length and pixel span of the line drawn').classes('text-xl') 
    ui.label().bind_text(yaml_parameters, 'resolution')

    ui.button('Confirm Values and download map files', on_click=download_map_files).classes('col-span-full').tooltip(tooltip.DOWNLOAD_BUTTON)

    if os.path.exists(image_path):
        with ui.row():
            ii = ui.interactive_image(image_path, on_mouse=handle_length, events=['mousedown', 'mouseup'],cross='red')
        image_reload_timer.cancel()
        image_reload_timer = ui.timer(interval=0.3, callback=lambda: ii.set_source(f'{image_path}'))

async def create_pgm():
    thresh = preparation_parameters.pgm_threshold
    yaml_string = to_yaml_str(yaml_parameters)
    await mc.convert_to_pgm(thresh, yaml_string)
    ui.notify(f'pgm created with threshold set to {thresh}, check file {pgm_path} before downloading')

async def handle_length(e: events.MouseEventArguments):
    global start_point, end_point, clicked, preparation_parameters
    color = 'red' 
    if e.type == 'mousedown':
        start_point = (e.image_x, e.image_y)
        clicked.clear()
    elif e.type == 'mouseup':
        end_point = (e.image_x, e.image_y)
        clicked.set()
    await clicked.wait()
    if start_point and end_point:
        # set empty content to allow only one line present in the picture
        ii.set_content("")
        ii.content += f'<line x1="{start_point[0]}" y1="{start_point[1]}" x2="{end_point[0]}" y2="{end_point[1]}" style="stroke:{color};stroke-width:2" />'
        preparation_parameters.pixels = euclidean_distance(start_point, end_point)
        ui.notify(f'pixel length set to {preparation_parameters.pixels}')
    else:
        ui.notify('start and endpoint not set correctly')

def euclidean_distance(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return distance

# don't forget the tooltips
def quality_page_layout():
    ui.timer(interval=5.0, callback=update_quality_parameter)
    
    ui.label('Percentage of the area reachable by the robot, defined through the filled area').classes('text-xl')
    ui.linear_progress(size='40px', color=FLAME_RED).bind_value_from(quality_parameters, 'percentage_filled_area')
    ui.label().bind_text(quality_parameters, 'percentage_filled_area')
    
    ui.label('area in m² reachable by the robot, defined through the filled area').classes('text-xl')
    ui.label().bind_text(quality_parameters, 'filled_area')
    
    ui.label('Percentage of the walls').classes('text-xl')
    ui.linear_progress(size='40px', color=FLAME_ORANGE).bind_value_from(quality_parameters, 'percentage_walls')
    ui.label().bind_text(quality_parameters, 'percentage_walls')
    
    ui.label('area in m² which is obstructed by walls').classes('text-xl')
    ui.label().bind_text(quality_parameters, 'wall_area')

async def update_quality_parameter():
    await compute_filled_percentage()
    await compute_wall_percentage()
    quality_parameters.filled_area = (quality_parameters.filled_pixels * yaml_parameters.resolution).__round__(1)
    quality_parameters.wall_area = (quality_parameters.black_pixels * yaml_parameters.resolution).__round__(1)
    
async def compute_filled_percentage():
    global quality_parameters
    filled_area_response = await qc.computeFilledAreaPercentage()
    if filled_area_response.status_code == 200:
        try:
                filled_response_dict = json.loads(filled_area_response.body)  # Parse the JSON string into a dictionary
                if isinstance(filled_response_dict, dict):  # Ensure it's a dictionary
                    quality_parameters.percentage_filled_area = filled_response_dict.get('filled_area_ratio')
                    quality_parameters.percentage_filled_area = quality_parameters.percentage_filled_area.__round__(4)
                    quality_parameters.raw_image_size = filled_response_dict.get('raw_image_size')
                    quality_parameters.filled_pixels = filled_response_dict.get('filled_pixels')
                else:
                    ui.notify("Error: Response is not a dictionary")
        except json.JSONDecodeError:
                ui.notify("Error: Failed to decode JSON response")
    elif filled_area_response.status_code == 400:
        ui.notify('Fill-function was never called, the filled area thus cannot be computed')
    else:    
        ui.notify(f"Error: {filled_area_response.body}")

async def compute_wall_percentage():
    global quality_parameters
    filled_wall_response = await qc.computePercentageWalls()
    if filled_wall_response.status_code == 200:
        try:
                wall_response_dict = json.loads(filled_wall_response.body)  # Parse the JSON string into a dictionary
                if isinstance(wall_response_dict, dict):  # Ensure it's a dictionary
                    quality_parameters.percentage_walls = wall_response_dict.get('wall_ratio')
                    quality_parameters.percentage_walls = quality_parameters.percentage_walls.__round__(4)
                    quality_parameters.pgm_image_size = wall_response_dict.get('pgm_image_size')
                    quality_parameters.black_pixels = wall_response_dict.get('black_pixels')
                else:
                    ui.notify("Error: Response is not a dictionary")
        except json.JSONDecodeError:
                ui.notify("Error: Failed to decode JSON response")
    elif filled_wall_response.status_code == (400 or 404):
        ui.notify('A pgm image was never created, the percentage of the wall thus cannot be computed')
    else:    
        ui.notify(f"Error: {filled_wall_response.body}")


def process_image_name(e: events.UploadEventArguments):
    global complete_yaml, complete_pgm, complete_picture, image_path, filled_image_path

    # get the file extension from the uploaded picture and save the file extension 
    _, file_extension = os.path.splitext(e.name)
    # file type check
    if file_extension not in ('.jpg', '.png', '.pgm'):
        ui.notify('wrong filetype, please enter only jpg, png or pgm files')
        return False
    else:
        # if something is typed into textbox, use it for both picture and yaml
        if len(yaml_parameters.image) > 0:
            complete_picture = "".join([yaml_parameters.image, file_extension])
            complete_yaml = "".join([yaml_parameters.image, '.yaml'])
            complete_pgm = "".join([yaml_parameters.image, '.pgm'])
            
            yaml_parameters.image = complete_picture
            e.name = complete_picture
            image_path = os.path.join(UPLOAD_DIR, complete_picture)
        # else use default picture name for both
        else:
            complete_picture = "".join([picture_name, file_extension]) 
            complete_yaml = "".join([picture_name, '.yaml'])
            complete_pgm = "".join([picture_name, '.pgm'])
            yaml_parameters.image = complete_picture
            e.name = complete_picture
            image_path = os.path.join(UPLOAD_DIR, complete_picture)
        # create filled image path with respect to file extension to avoid conversion issues
        complete_filled = "".join(['filled_image', file_extension])
        filled_image_path = os.path.join(UPLOAD_DIR, complete_filled)
        return True
    
def parameter_page_layout(): 
    global yaml_parameters
    if visibility:
        with ui.grid(columns=16).classes('w-full gap-0'):
            ui.label('Origin').classes('text-xl').classes('border p-1').classes('col-span-full').tooltip(tooltip.ORIGIN)
            ui.number('Origin: x [m]', value=0.0, format='%.2f', step=0.5).bind_value(yaml_parameters, 'origin_x').classes('col-span-5').tooltip(tooltip.ORIGIN_X)
            ui.number('Origin: y [m]', value=0.0, format='%.2f', step=0.5).bind_value(yaml_parameters, 'origin_y').classes('col-span-5').tooltip(tooltip.ORIGIN_Y)
            ui.number('Origin: yaw [rad]', value=0.0, format='%.2f', step=0.5).bind_value(yaml_parameters, 'origin_yaw').classes('col-span-6').tooltip(tooltip.ORIGIN_YAW)

            ui.checkbox('Negate').bind_value(yaml_parameters, 'negate').classes('border p-1 col-span-full').tooltip(tooltip.NEGATE)
            
            ui.label('Occupied threshold').classes('text-xl col-span-full').tooltip(tooltip.OCCUPIED_THRESH)
            occupied_thresh = ui.slider(min=0.001, max=1, step=0.01).bind_value(yaml_parameters, 'occupied_thresh').classes('col-span-8 vertical-bottom').tooltip(tooltip.OCCUPIED_THRESH)
            ui.number('Occopied threshold', value=yaml_parameters.occupied_thresh, format ='%.2f', step = 0.1).bind_value(yaml_parameters, 'occupied_thresh').classes('col-span-5').tooltip(tooltip.OCCUPIED_THRESH)
            ui.label().bind_text_from(occupied_thresh, 'value').classes('col-span-3').tooltip(tooltip.OCCUPIED_THRESH)
            
            ui.label('Free threshold').classes('text-xl col-span-full border p-4').tooltip(tooltip.FREE_THRESH)
            free_thresh = ui.slider(min=0.001, max=1, step=0.01).bind_value(yaml_parameters, 'free_thresh').classes('col-span-8').tooltip(tooltip.FREE_THRESH)
            ui.number('Free threshold', value=yaml_parameters.free_thresh, format ='%.2f', step = 0.1).bind_value(yaml_parameters, 'free_thresh').classes('col-span-5').tooltip(tooltip.FREE_THRESH)
            ui.label().bind_text_from(free_thresh, 'value').classes('col-span-3').tooltip(tooltip.FREE_THRESH)

            ui.label('Mode').classes('text-xl').classes('col-span-4').tooltip(tooltip.MODE)
            ui.select(['trinary', 'scale', 'raw']).bind_value(yaml_parameters, 'mode').classes('col-span-12').tooltip(tooltip.MODE)
    else:
        no_pic()
        
async def download_map_files() -> None:
    global yaml_parameters, complete_yaml, complete_picture
    
    yaml_string = to_yaml_str(yaml_parameters)
    ui.notify(yaml_string)
    response = await mc.download_files(yaml_string)
    
    if response.status_code == 200:
            try:
                response_body = response.body  # Get the response body as a string
                response_body_dict = json.loads(response_body)  # Parse the JSON string into a dictionary
                if isinstance(response_body_dict, dict):  # Ensure it's a dictionary
                    ui.notify(f"File uploaded: {response_body_dict.get('message', 'No message provided')} at {response_body_dict['location']}")
                    print(response_body_dict)  # Print the dictionary of the JSON response
                    ui.download(f'{UPLOAD_DIR}/{complete_pgm}')
                    ui.download(f'{UPLOAD_DIR}/{complete_yaml}')
                else:
                    ui.notify("Error: Response is not a dictionary")
            except json.JSONDecodeError:
                ui.notify("Error: Failed to decode JSON response")
    else:
        ui.notify(f"Error: {response_body}")

def no_pic():
    ui.notify("No picture uploaded, please go to Upload and upload a file")
    
def pencil() -> None:
    global ii, preparation_parameters, image_path
    if visibility:
        # TODO: use quasar classes to fix content to directly below the header
        with ui.grid(columns = '200px auto'):
            ui.label('Thickness').classes('text-xl').classes('border p-1').tooltip(tooltip.THICKNESS)
            thickness = ui.slider(min=1, max=20, step=1).bind_value(preparation_parameters, 'thickness').classes('border p-1').tooltip(tooltip.THICKNESS)
            
            ui.label('Thickness set to: ').classes('text-xl').classes('border p-1')
            ui.label().bind_text_from(thickness, 'value').classes('text-xl').classes('border p-1')
            
            ui.label('Type of processing').classes('text-xl').classes('border p-1').tooltip(tooltip.PENCIL)
            ui.toggle(['point', 'line', 'square', 'fill'], on_change=reload_image).bind_value(preparation_parameters, 'preparation_type').classes('border p-1').tooltip(tooltip.PENCIL)
        ii = ui.interactive_image(image_path, on_mouse=handle_pencil, events=['mousedown', 'mouseup'],cross='red')
    else:
        no_pic

def eraser() -> None:
    global ii, preparation_parameters, image_path
    if visibility:
        with ui.grid(columns = '200px auto'):
            ui.label('Thickness').classes('text-xl').classes('border p-1').tooltip(tooltip.THICKNESS)
            thickness = ui.slider(min=1, max=20, step=1).bind_value(preparation_parameters, 'thickness').classes('border p-1').tooltip(tooltip.THICKNESS)
            
            ui.label('Thickness set to: ').classes('text-xl').classes('border p-1')
            ui.label().bind_text_from(thickness, 'value').classes('text-xl').classes('border p-1')
            
            ui.label('Type of processing').classes('text-xl').classes('border p-1').tooltip(tooltip.ERASER)
            ui.toggle(['point', 'line', 'square', 'fill'], on_change=reload_image).bind_value(preparation_parameters, 'preparation_type').classes('border p-1').tooltip(tooltip.ERASER)
        
        ii = ui.interactive_image(image_path, on_mouse=handle_eraser, events=['mousedown', 'mouseup'],cross='red')
    else:
        no_pic()    
    
async def on_file_upload(e: events.UploadEventArguments):
    global visibility, yaml_parameters
    
    if process_image_name(e):
    # access events via the event.Eventtype stuff and send content of the event to backend
        response = await mp.save_file(e.content.read(), e.name)
        if response.status_code == 200:
            try:
                response_body = response.body  # Get the response body as a string
                response_body_dict = json.loads(response_body)  # Parse the JSON string into a dictionary
                if isinstance(response_body_dict, dict):  # Ensure it's a dictionary
                    ui.notify(f"File uploaded: {response_body_dict.get('message', 'No message provided')} at {response_body_dict['location']}")
                    visibility = True
                else:
                    ui.notify("Error: Response is not a dictionary")
                    visibility = False
            except json.JSONDecodeError:
                ui.notify("Error: Failed to decode JSON response")
                visibility = False
        else:
            ui.notify(f"Error: {response_body}")
            visibility = False

async def fetch_image():
    async with httpx.AsyncClient() as client:
        response = await client.get('http://127.0.0.1:8000/image')
        if response.status_code == 200:
            with open(complete_picture, "wb") as f:
                f.write(response.content)
            return complete_picture
        else:
            ui.notify("Failed to load image")

async def pencil_line(e: events.MouseEventArguments):
    global start_point, end_point, clicked
    if e.type == 'mousedown':
        start_point = (e.image_x, e.image_y)
        clicked.clear()
    elif e.type == 'mouseup':
        end_point = (e.image_x, e.image_y)
        clicked.set()
    await clicked.wait()
    if start_point and end_point:
        thickness = preparation_parameters.thickness
        await mp.addLine(start_point, end_point, thickness)
    else:
        ui.notify('start and endpoint not set correctly')

async def pencil_point(e: events.MouseEventArguments):
    # only listens to mousedown to prevent to many dots from spawning
    if e.type == 'mousedown':
        x = e.image_x
        y = e.image_y
        thickness = preparation_parameters.thickness
        await mp.addPoint(x,y, thickness)

async def pencil_square(e: events.MouseEventArguments):
    global start_point, end_point, clicked
    if e.type == 'mousedown':
        start_point = (e.image_x, e.image_y)
        clicked.clear()
    elif e.type == 'mouseup':
        end_point = (e.image_x, e.image_y)
        clicked.set()
    await clicked.wait()
    if start_point and end_point:
        await mp.drawSquare(start_point, end_point)
    else:
        ui.notify('start and endpoint not set correctly')

async def fill_area(e: events.MouseEventArguments):
    # only listens to mousedown to prevent to many dots from spawning
    if e.type == 'mousedown':
        x = e.image_x
        y = e.image_y
        await mp.fillArea(x,y)

# clicked.set needs to be called, else clicked.wait() blocks the routine and mp.addPoint is not reached    
async def handle_pencil(e: events.MouseEventArguments):
    if preparation_parameters.preparation_type == 'line':
        await pencil_line(e)
    elif preparation_parameters.preparation_type == 'point':
        await pencil_point(e)
    elif preparation_parameters.preparation_type == 'square':
        await pencil_square(e)    
    elif preparation_parameters.preparation_type == 'fill':
        await fill_area(e)     
    else:
        ui.notify(f'no preparation type chosen')
            
async def handle_eraser(e: events.MouseEventArguments):
    if preparation_parameters.preparation_type == 'line':
        await erase_line(e)
    elif preparation_parameters.preparation_type == 'point':
        await erase_point(e)
    elif preparation_parameters.preparation_type == 'square':
        await erase_square(e)    
    elif preparation_parameters.preparation_type == 'fill':
        await fill_area(e)  
    else:
        ui.notify(f'no preparation type chosen')

async def erase_line(e: events.MouseEventArguments):
    global start_point, end_point, clicked
    if e.type == 'mousedown':
        start_point = (e.image_x, e.image_y)
        clicked.clear()
    elif e.type == 'mouseup':
        end_point = (e.image_x, e.image_y)
        clicked.set()
    await clicked.wait()
    if start_point and end_point:
        thickness = preparation_parameters.thickness
        await mp.eraseLine(start_point, end_point, thickness)
    else:
        ui.notify('start and endpoint not set correctly')
      
async def erase_point(e: events.MouseEventArguments):
    # only listens to mousedown to prevent to many dots from spawning
    if e.type == 'mousedown':
        x = e.image_x
        y = e.image_y
        thickness = preparation_parameters.thickness
        await mp.erasePoint(x,y, thickness)

async def erase_square(e: events.MouseEventArguments):
    global start_point, end_point, clicked
    if e.type == 'mousedown':
        start_point = (e.image_x, e.image_y)
        clicked.clear()
    elif e.type == 'mouseup':
        end_point = (e.image_x, e.image_y)
        clicked.set()
    await clicked.wait()
    if start_point and end_point:
        await mp.eraseSquare(start_point, end_point)
    else:
        ui.notify('start and endpoint not set correctly')

# to avoid caching issues, each URL must be unique to allow the browser to reload the image
# and to avoid flickering images due to heavy switching, the timer needs to be canceld and re-inizialized again 
def reload_image():
    global image_reload_timer
    if preparation_parameters.preparation_type != 'fill':
        image_reload_timer.cancel()
        image_reload_timer = ui.timer(interval=0.3, callback=lambda: ii.set_source(f'{image_path}?{time.time()}'))
    elif preparation_parameters.preparation_type == 'fill':
        if os.path.exists(filled_image_path):
            image_reload_timer.cancel()
            image_reload_timer = ui.timer(interval=0.3, callback=lambda: ii.set_source(f'{filled_image_path}?{time.time()}'))
    else: 
        ui.notify('No picture chosen or picture deleted, please start by uploading a picture')
