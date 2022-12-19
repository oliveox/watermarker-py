import logging
import os
import sys

logger = None
verbosity = None


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
    file_handler = logging.FileHandler("logs.log")
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


_env_var_name = "WATERMARKER_VERBOSE"


def initialise_logger():
    global logger
    global verbosity
    global _stream_handler

    logger = create_logger()

    # set verbosity
    try:
        # TODO - treat keyerror as normal (if verbose not set then it is normal for this env var to not exist)
        verbosity = eval(os.environ["WATERMARKER_VERBOSE"])
        if verbosity:
            # allow all levels to be logged
            _stream_handler.removeFilter(_custom_filter)
    except (KeyError, SyntaxError, NameError, TypeError) as e:
        logger.exception(
            f"Could not read verbosity environment variable [{_env_var_name}]. Defaulting to non-verbose", e
        )
    except AttributeError:
        logger.exception("Stream handler is None. Cannot remove filter")

    logger.debug("Logger initialised")


initialise_logger()
