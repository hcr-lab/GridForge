#!/usr/bin/env python3

import asyncio
import httpx
from nicegui import app, events, ui
from fastapi import FastAPI
from Frontend.router import Router
import Backend.map_preparation.map_preparation as mp
import Backend.map_creation.map_creation as mc
import json
import os
from Frontend.preparation_parameters import Preparation_parameters
from Frontend.yaml_parameters import Yaml_parameters
import time 
from pydantic_yaml import to_yaml_str

# global variables
site_plan = any
ii = any
processed_image = any
thickness = 3
visibility = True
origin = None
yaml_parameters = Yaml_parameters()
preparation_parameters = Preparation_parameters()
picture_name = 'uploaded_file'
complete_yaml = 'uploaded_file.yaml'
complete_picture = 'uploaded_file.jpg'
complete_pgm = 'uploaded_file.pgm'
start_point = tuple
end_point = tuple
clicked = asyncio.Event()

UPLOAD_DIR = "uploaded_files"

FLAME_RED = '#CD2A23'
FLAME_ORANGE = '#EF7C23'
FLAME_YELLOW = '#F2E738'

os.makedirs(UPLOAD_DIR, exist_ok=True)
image_path = os.path.join(UPLOAD_DIR, complete_picture)

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
            ui.input('Enter name of Picture', placeholder=picture_name).bind_value_to(yaml_parameters, 'image')
            ui.upload(on_upload=on_file_upload, label="Upload a picture")
            
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
            
        @router.add('/download')
        def show_download():
            ui.label('Set YAML Parameters').classes('text-2xl')
            download_page_layout()

        @router.add('/quality')
        def show_quality():
            ui.label('Quality parameters').classes('text-2xl')
            quality_page_layout()
            
        # adding some navigation buttons to switch between the different pages
        with ui.header(elevated=True).style(f'background-color: #3874c8').classes('items-center justify-between'):
            ui.button('Upload', on_click=lambda: router.open(show_upload)).classes('w-32')
            ui.button('Pencil', on_click=lambda: router.open(show_pencil)).classes('w-32')
            ui.button('Eraser', on_click=lambda: router.open(show_eraser)).classes('w-32')
            ui.button('Download', on_click=lambda: router.open(show_download)).classes('w-32')
            ui.button('Quality', on_click=lambda: router.open(show_quality)).classes('w-32')
            
        # this places the content which should be displayed
        router.frame().classes('w-full p-4 bg-gray-100')

    # mount path is homepage, secret is randomly chosen
    ui.run_with(fastapi_app, storage_secret='secret') 

def quality_page_layout():
    pass

def process_image_name(e: events.UploadEventArguments):
    global complete_yaml, complete_pgm, complete_picture, image_path

    # get the file extension from the uploaded picture and save the file extension to 
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
        return True
    
def download_page_layout(): 
    global yaml_parameters
    if visibility:
        with ui.column():
            ui.label('Resolution').classes('text-xl')
            resolution = ui.slider(min=0.01, max=0.5, step=0.01).bind_value(yaml_parameters, 'resolution')
            ui.label().bind_text_from(resolution, 'value')

            ui.label('Origin').classes('text-xl')
            ui.number('Origin: x', value=0.0, format='%.2f', step=0.5).bind_value(yaml_parameters, 'origin_x')
            ui.number('Origin: y', value=0.0, format='%.2f', step=0.5).bind_value(yaml_parameters, 'origin_y')
            ui.number('Origin: yaw', value=0.0, format='%.2f', step=0.5).bind_value(yaml_parameters, 'origin_yaw')

            ui.checkbox('Negate').bind_value(yaml_parameters, 'negate')
            
            ui.label('Occupied threshold').classes('text-xl')
            occupied_thresh = ui.slider(min=0.001, max=1, step=0.01).bind_value(yaml_parameters, 'occupied_thresh')
            ui.label().bind_text_from(occupied_thresh, 'value')
            ui.number('Occopied threshold', value=yaml_parameters.occupied_thresh, format ='%.2f', step = 0.1).bind_value(yaml_parameters, 'occupied_thresh')
            
            ui.label('Free threshold').classes('text-xl')
            free_thresh = ui.slider(min=0.001, max=1, step=0.01).bind_value(yaml_parameters, 'free_thresh')
            ui.label().bind_text_from(free_thresh, 'value')
            ui.number('Free threshold', value=yaml_parameters.free_thresh, format ='%.2f', step = 0.1).bind_value(yaml_parameters, 'free_thresh')

            ui.label('Mode').classes('text-xl')
            ui.select(['trinary', 'scale', 'raw']).bind_value(yaml_parameters, 'mode')

            ui.button('Confirm Values and download map files', on_click=download_map_files)
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
    
# TODO: write only one function and give on mouse handler as a parameter
def pencil() -> None:
    global ii, preparation_parameters, image_path
    if visibility:
        # TODO: use quasar classes to fix content to directly below the header
        with ui.grid(columns = '200px auto'):
            ui.label('Thickness').classes('text-xl').classes('border p-1')
            thickness = ui.slider(min=1, max=20, step=1).bind_value(preparation_parameters, 'thickness').classes('border p-1')
            
            ui.label('Thickness set to: ').classes('text-xl').classes('border p-1')
            ui.label().bind_text_from(thickness, 'value').classes('text-xl').classes('border p-1')
            
            ui.label('Type of processing').classes('text-xl').classes('border p-1')
            ui.toggle(['point', 'line', 'square']).bind_value(preparation_parameters, 'preparation_type').classes('border p-1')
        
        ii = ui.interactive_image(image_path, on_mouse=handle_pencil, events=['mousedown', 'mouseup'],cross='red')
        reload_image(ii)
    else:
        no_pic

def eraser() -> None:
    global ii, preparation_parameters, image_path
    if visibility:
        with ui.grid(columns = '200px auto'):
            ui.label('Thickness').classes('text-xl').classes('border p-1')
            thickness = ui.slider(min=1, max=20, step=1).bind_value(preparation_parameters, 'thickness').classes('border p-1')
            
            ui.label('Thickness set to: ').classes('text-xl').classes('border p-1')
            ui.label().bind_text_from(thickness, 'value').classes('text-xl').classes('border p-1')
            
            ui.label('Type of processing').classes('text-xl').classes('border p-1')
            ui.toggle(['point', 'line', 'square']).bind_value(preparation_parameters, 'preparation_type').classes('border p-1')
        
        ii = ui.interactive_image(image_path, on_mouse=handle_eraser, events=['mousedown', 'mouseup'], cross='red')
        reload_image(ii)
    else:
        no_pic()    
    
# TODO: File type check
async def on_file_upload(e: events.UploadEventArguments):
    global visibility, yaml_parameters
    
    # check if correct image type was uploaded
    if process_image_name(e):
    # access events via the event.Eventtype stuff and send content of the event to backend
        response = await mp.save_file(e.content.read(), e.name)
        if response.status_code == 200:
            try:
                response_body = response.body  # Get the response body as a string
                response_body_dict = json.loads(response_body)  # Parse the JSON string into a dictionary
                if isinstance(response_body_dict, dict):  # Ensure it's a dictionary
                    ui.notify(f"File uploaded: {response_body_dict.get('message', 'No message provided')} at {response_body_dict['location']}")
                    print(response_body_dict)  # Print the dictionary of the JSON response
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

# clicked.set needs to be called, else clicked.wait() blocks the routine and mp.addPoint is not reached    
async def handle_pencil(e: events.MouseEventArguments):
    if preparation_parameters.preparation_type == 'line':
        await pencil_line(e)
    elif preparation_parameters.preparation_type == 'point':
        await pencil_point(e)
    elif preparation_parameters.preparation_type == 'square':
        await pencil_square(e)    
    else:
        ui.notify(f'no preparation type chosen')
            
async def handle_eraser(e: events.MouseEventArguments):
    if preparation_parameters.preparation_type == 'line':
        await erase_line(e)
    elif preparation_parameters.preparation_type == 'point':
        await erase_point(e)
    elif preparation_parameters.preparation_type == 'square':
        await erase_square(e)    
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
def reload_image(ii):
    global image_path
    ui.timer(interval=0.3, callback=lambda: ii.set_source(f'{image_path}?{time.time()}'))

