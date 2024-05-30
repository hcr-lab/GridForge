from typing import Callable, Optional

from nicegui.element import Element


class Zoom(Element, component='zoom_image.js'):

    def __init__(self) -> None:
        super().__init__()

    def zoomIn(self) -> None:
        self.run_method('zoomIn')
        
    def zoomOut(self) -> None:
        self.run_method('zoomOut')