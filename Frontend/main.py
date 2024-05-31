#!/usr/bin/env python3

from numbers import Number
import httpx
from nicegui import app, events, ui
from fastapi import FastAPI
from Frontend.router import Router
import uuid
import Backend.map_preparation.map_preparation as mp
import Backend.map_creation.map_creation as mc
import json
import os
from Frontend.zoom_image import Zoom
from Frontend.yaml_parameters import Yaml_parameters, Origin
import time 
from pydantic_yaml import to_yaml_str, to_yaml_file

# global variables
site_plan = any
ii = any
processed_image = any
visibility = True
origin = None
yaml_parameters = Yaml_parameters()

UPLOAD_DIR = "uploaded_files"
PICTURE_NAME = "uploaded_file.jpg"
YAML_NAME = "uploaded_file.yaml"
os.makedirs(UPLOAD_DIR, exist_ok=True)
IMAGE_PATH = os.path.join(UPLOAD_DIR, PICTURE_NAME)
YAML_PATH = os.path.join(UPLOAD_DIR, YAML_NAME)

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
            ui.label('Upload').classes('text-2xl')
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
            # TODO: provide different buttons for different thicknesses
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
        with ui.row():
            ui.button('Upload', on_click=lambda: router.open(show_upload)).classes('w-32')
            ui.button('Pencil', on_click=lambda: router.open(show_pencil)).classes('w-32')
            ui.button('Rubber', on_click=lambda: router.open(show_eraser)).classes('w-32')
            ui.button('Download', on_click=lambda: router.open(show_download)).classes('w-32')
            ui.button('Quality', on_click=lambda: router.open(show_quality)).classes('w-32')
            
        # this places the content which should be displayed
        router.frame().classes('w-full p-4 bg-gray-100')

    # mount path is homepage, secret is randomly chosen
    ui.run_with(fastapi_app, storage_secret='secret') 

def quality_page_layout():
    pass

# TODO: enable possibility to change file names
def download_page_layout(): 
    global yaml_parameters
    if visibility:
        set_image_name_for_yaml()
        with ui.column():
            # slider for thickness of lines, possible solution
            ui.label('Resolution').classes('text-xl')
            resolution = ui.slider(min=0.01, max=0.5, step=0.01).bind_value(yaml_parameters, 'resolution')
            ui.label().bind_text_from(resolution, 'value')

            ui.label('Origin').classes('text-xl')
            ui.number('Origin: x', value=0.0, format='%.2f', step=0.5).bind_value(yaml_parameters, 'origin_x')
            ui.number('Origin: y', value=0.0, format='%.2f', step=0.5).bind_value(yaml_parameters, 'origin_y')
            ui.number('Origin: yaw', value=0.0, format='%.2f', step=0.5).bind_value(yaml_parameters, 'origin_yaw')

            ui.checkbox('Negate').bind_value(yaml_parameters, 'negate')
            
            ui.label('Occupied threshold').classes('text-xl')
            occupied_thresh = ui.slider(min=0.001, max=1, step=0.001).bind_value(yaml_parameters, 'occupied_thresh')
            ui.label().bind_text_from(occupied_thresh, 'value')
            
            ui.label('Free threshold').classes('text-xl')
            free_thresh = ui.slider(min=0.001, max=1, step=0.001).bind_value(yaml_parameters, 'free_thresh')
            ui.label().bind_text_from(free_thresh, 'value')
            
            ui.label('Mode').classes('text-xl')
            ui.select(['trinary', 'scale', 'raw']).bind_value(yaml_parameters, 'mode')

            ui.button('Confirm Values and download map files', on_click=download_map_files)
    else:
        no_pic()
        
async def download_map_files() -> None:
    global yaml_parameters
    yaml_string = to_yaml_str(yaml_parameters)
    ui.notify(yaml_string)
    response = await mc.download_yaml(yaml_string)
    
    if response.status_code == 200:
            try:
                response_body = response.body  # Get the response body as a string
                response_body_dict = json.loads(response_body)  # Parse the JSON string into a dictionary
                if isinstance(response_body_dict, dict):  # Ensure it's a dictionary
                    ui.notify(f"File uploaded: {response_body_dict.get('message', 'No message provided')} at {response_body_dict['location']}")
                    print(response_body_dict)  # Print the dictionary of the JSON response
                    ui.download(f'{UPLOAD_DIR}/{PICTURE_NAME}?{time.time()}')
                    ui.download(f'{UPLOAD_DIR}/{YAML_NAME}')
                else:
                    ui.notify("Error: Response is not a dictionary")
            except json.JSONDecodeError:
                ui.notify("Error: Failed to decode JSON response")
    else:
        ui.notify(f"Error: {response_body}")
    
# TODO: set name for yaml correctly
def set_image_name_for_yaml():
    pass

def no_pic():
    ui.notify("No picture uploaded, please go to Upload and upload a file")

# TODO: write only one function and give on mouse handler as a parameter
# TODO: allow dragging of mouse to multiple locations 
def pencil() -> None:
    global ii
    if visibility:
        ii = ui.interactive_image(IMAGE_PATH, on_mouse=handle_pencil, events=['mousedown'], cross='red')
        reload_image(ii)
    else:
        no_pic

def eraser() -> None:
    global ii
    if visibility:
        ii = ui.interactive_image(IMAGE_PATH, on_mouse=handle_eraser, events=['mousedown'], cross='red')
        reload_image(ii)
    else:
        no_pic()    
    
# TODO: File type check
async def on_file_upload(e: events.UploadEventArguments):
    global visibility
    # access events via the event.Eventtype stuff and send content of the event to backend
    response = await mp.save_file(e.content.read())
    
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
            with open(IMAGE_PATH, "wb") as f:
                f.write(response.content)
            return IMAGE_PATH
        else:
            ui.notify("Failed to load image")

async def handle_pencil(e: events.MouseEventArguments):
    x = e.image_x
    y = e.image_y
    await mp.addPoint(x,y)
    # reload_image()
    
async def handle_eraser(e: events.MouseEventArguments):
    x = e.image_x
    y = e.image_y
    await mp.erasePoint(x,y)
    # reload_image()

def reload_image(ii):
    ui.timer(interval=0.3, callback=lambda: ii.set_source(f'{IMAGE_PATH}?{time.time()}'))

