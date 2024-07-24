# GridForge

## Introduction

GridForge is a tool to change site or floor plans and convert them to 2D occupancy grid maps. The output is a yaml-file and a pgm-file which are directly usable for navigation tasks for mobile robots. It was created by me and is the topic of my master thesis. If you use GridForge, please cite me, a citation will follow once the thesis is published. 
GridForge is based upon Nicegui, a python-based frontend framework from Zauberzeug. Credits to them for their nice work! 

## How to start

Install the dependencies, maybe in an virtual environment, with 

```bash
pip install -r requirements.txt
```

Start the server with 

```bash
uvicorn Backend.main:app --reload --log-level debug --port 8000
```

It is currently running only locally. Frontend and backend are split because running it separately and achieving the communication with APIs is intended but not yet implemented. 

Access GridForge under `localhost:8000`

## How to use

A small tutorial is implemented. Reach it by clicking on the Tutorial-button on the right side in the header. 

## Next steps

API implementation
adding tests 
UI improvements like zoom and multi language support
Improved algorithms for automated image processing 
Connection to robots to see their position on the map
... 