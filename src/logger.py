import logging
import os
import sys


class CustomFilter(logging.Filter):
    def filter(self, record):
        return record.levelno == logging.INFO


logger = logging.getLogger("watermarker")
logger.setLevel(logging.DEBUG)

# set file handler first (always on debug) so that verbosity flag issues can be logged
file_handler = logging.FileHandler("logs.log")
file_handler.setLevel(logging.DEBUG)
file_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_format)
logger.addHandler(file_handler)

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.DEBUG)
stream_format = logging.Formatter("%(message)s")
stream_handler.setFormatter(stream_format)

custom_filter = CustomFilter()
stream_handler.addFilter(custom_filter)

logger.addHandler(stream_handler)

verbosity = None
env_var_name = "WATERMARKER_VERBOSE"
try:
    # TODO - treat keyerror as normal (if verbose not set then it is normal for this env var to not exist)
    verbosity = eval(os.environ["WATERMARKER_VERBOSE"])
except (KeyError, SyntaxError, NameError, TypeError) as e:
    logger.exception(f"Could not read verbosity environment variable [{env_var_name}]. Defaulting to non-verbose", e)

if verbosity:
    # allow all levels to be logged
    stream_handler.removeFilter(custom_filter)
