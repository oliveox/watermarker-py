import logging
import os
import sys

logger = logging.getLogger("watermarker")

# set file handler first (always on debug) so that verbosity flag issues can be logged
file_handler = logging.FileHandler("logs.log")
file_handler.setLevel(logging.DEBUG)
file_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_format)

logger.addHandler(file_handler)

verbosity = None
try:
    verbosity = eval(os.environ["WATERMARKER_VERBOSE"])
except (KeyError, SyntaxError, NameError, TypeError) as e:
    logger.exception("Invalid verbosity level value. Defaulting to non-verbose", e)

logging_level = logging.DEBUG if verbosity else logging.INFO
logger.setLevel(logging_level)

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging_level)
stream_format = logging.Formatter("%(message)s")
stream_handler.setFormatter(stream_format)

logger.addHandler(stream_handler)
