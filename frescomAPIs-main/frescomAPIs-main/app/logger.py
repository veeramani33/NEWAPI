import logging
import sys

# Get the root logger
logger = logging.getLogger()

# Create a formatter
formatter = logging.Formatter(
    fmt="[%(levelname)s] %(asctime)s : %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)

# Create a handler
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)

file_handler = logging.FileHandler("app.log")
file_handler.setFormatter(formatter)

# Add the handler to the root logger
logger.handlers = [stream_handler, file_handler]

# Set the logging level
logger.setLevel(logging.INFO)
