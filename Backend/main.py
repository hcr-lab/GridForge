#!/usr/bin/env python3
import Frontend.main as frontend
from fastapi import FastAPI
from Backend.map_preparation.map_preparation import show_text

app = FastAPI()

frontend.init(app)

def handle_get(text: str):
    print('method reached')
    show_text(text)
    
if __name__ == '__main__':
    print('Please start the app with the "uvicorn" command as shown in the start.sh script')