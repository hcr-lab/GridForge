#!/usr/bin/env python3
import Frontend.main as frontend
from Backend.global_variables import app
import Backend.map_creation.webservice_map_creation as map_creation
import Backend.map_preparation.webservice_map_preparation as map_preparation
import Backend.quality_check.webservice_quality_check as quality_check

frontend.init(app)
    
if __name__ == '__main__':
    print('Please start the app with the "uvicorn" command as shown in the start.sh script')