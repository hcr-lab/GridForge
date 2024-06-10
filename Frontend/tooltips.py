
# TODO: Check tooltip validity
class Tooltip_Enum():
    RESOLUTION = 'Set the resolution of the pgm map in metter per pixel. 0.05 means that one pixel represent 5 centimeter in the real world. Default is 0.05 m/px for smaller maps'
    ORIGIN = 'Sets the origin of the map with regard to the pixels with the coordinates (0, 0). Consists of the x and y coordinates and the yaw angle'
    ORIGIN_X = 'Set the x-coordinate of the origin in meters. Default is 0.0'
    ORIGIN_Y = 'Sets the y-coordinate of the origin in meters. Default is 0.0'
    ORIGIN_YAW = 'Sets the yaw angle of the origin in rad. Default is 0.0'
    NEGATE = 'Negates the color of black and white in the map representation. Default is False'
    OCCUPIED_THRESH = 'The percentage after which a cell is detected as occupied. Default is 0.7'
    FREE_THRESH = 'The percentage under which a cell is detected as free. Default is 0.2'
    MODE = 'The mode in which the values in the cells are processed. ... explain ... Default is trinary'
    DOWNLOAD_FILES = 'Save all values and download both yaml and pgm file with the set name and parameters'
    
    THICKNESS = 'This sets the thickness of the lines in Pixels'
    PENCIL = 'With this button, the processing mode can be changed. \n Point = a black dot with set thickness is drawn at the location of the click \n Line = a black line with the set thickness is drawn between the point where the mouse goes down and the point where the mouse goes up \n Rectangle = a filled black rectangle is drawn between the point where the mouse goes down and the point where the mouse goes up.\n These modes add obstacles to the site plan'

    ERASER = 'With this button, the processing mode can be changed. \n Point = a white dot with set thickness is drawn at the location of the click \n Line = a white line with the set thickness is drawn between the point where the mouse goes down and the point where the mouse goes up \n Rectangle = a filled black white is drawn between the point where the mouse goes down and the point where the mouse goes up \n These modes effectively erase things on the site plan'
 
    UPLOAD_IF = 'Click here to choose a file on your pc. Only choose ONE file of type png, jpg or pgm. After choosing the image, click on the cloud symbol to upload it to the system'
    UPLOAD_NAME = 'Enter the name of the picture here, but without file extension'
    
    UPLOAD_BUTTON = 'Click here to switch to the Upload page where you choose the site plan picture'
    PENCIL_BUTTON = 'Click here to switch to the pencil page where you can draw points, lines and rectangles onto your picture'
    ERASER_BUTTON = 'Click here to switch to the Eraser page where you can delete something out of your site plan'
    DOWNLOAD_BUTTON = 'Click here to switch to the Download page where you can set your parameters for the yaml file as well as downloading both yaml and pgm files for deployment on your robot'
    QUALITY_BUTTON = 'Click here to switch to the Quality page where you can view quality metrics as well as the pgm file of your map which is used for deployment on your robot'