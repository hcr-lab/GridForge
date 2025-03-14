import os
import logging



# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

# Create a logger instance
logger = logging.getLogger(__name__)

UPLOAD_DIR = "uploaded_files"
FILENAME = "uploaded_file.jpg"
os.makedirs(UPLOAD_DIR, exist_ok=True)
image_path = os.path.join(UPLOAD_DIR, FILENAME)
cut_image_path = None

