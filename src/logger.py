import logging
import os
import sys

logger = None
verbosity = None
VERBOSITY_ENV_VAR_NAME = "WATERMARKER_VERBOSE"


class _CustomFilter(logging.Filter):
    def filter(self, record):
        return record.levelno == logging.INFO


_stream_handler = None
_custom_filter = _CustomFilter()


def create_logger():
    global logger
    global _stream_handler

    logger = logging.getLogger("watermarker")
    logger.setLevel(logging.DEBUG)

    # set file handler first (always on debug) so that verbosity flag issues can be logged
    file_handler = logging.FileHandler("logs.log", "w")
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(file_format)

    logger.addHandler(file_handler)

    _stream_handler = logging.StreamHandler(sys.stdout)
    _stream_handler.setLevel(logging.DEBUG)
    _stream_format = logging.Formatter("%(message)s")
    _stream_handler.setFormatter(_stream_format)

    _stream_handler.addFilter(_custom_filter)

    logger.addHandler(_stream_handler)

    return logger


def initialise_logger():
    global logger
    global verbosity
    global _stream_handler

    logger = create_logger()

    # set verbosity
    try:
        # TODO - treat keyerror as normal (if verbose not set then it is normal for this env var to not exist)
        verbosity = eval(os.environ[VERBOSITY_ENV_VAR_NAME])
        if verbosity:
            # allow all levels to be logged
            _stream_handler.removeFilter(_custom_filter)
    except (KeyError, SyntaxError, NameError, TypeError):
        logger.exception("Could not read verbosity environment variable [{_env_var_name}]. Defaulting to non-verbose")
    except AttributeError:
        logger.exception("Stream handler is None. Cannot remove filter")

    logger.debug("Logger initialised")


initialise_logger()
