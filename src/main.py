import argparse
import os

try:
    parser = argparse.ArgumentParser(prog="watermarker", description="Add watermark to images and videos")
    parser.add_argument(
        "--i",
        "--input",
        required=True,
        help="Input media files directory path",
        nargs="+",
    )
    parser.add_argument(
        "--w",
        "--watermark",
        required=True,
        help="Watermark file path",
        nargs=1,
        type=str,
    )
    parser.add_argument(
        "--p",
        "--prefix",
        required=True,
        help="Prefix of the new file. OutputFilename = {prefix}{InputFilename}",
        nargs=1,
        type=str,
    )
    parser.add_argument(
        "--o",
        "--output",
        required=False,
        help="Output watermarked files drectory. If path doesn't exist, it will be created",
        nargs=1,
        type=str,
    )
    parser.add_argument(
        "--v",
        "--verbose",
        required=False,
        help="Set level of verbosity. 1 = Debug logs ; 2 = 1 + FFmpeg logs",
        nargs=1,
        choices=[1, 2],
        type=int,
    )
    parser.add_argument(
        "--k",
        "--keep_output_tree",
        required=False,
        help="Keep the same directory tree for output as the input files",
    )
    parser.add_argument(
        "--ow",
        "--overwrite",
        required=False,
        help="Overwrite output file if it already exists",
        action="store_true",
    )

    args = parser.parse_args()

    input_paths = args.i
    watermark_path = args.w[0]
    prefix = args.p[0]
    output_path = args.o[0] if args.o else None
    verbosity_level = args.v[0] if args.v else None
    keep_output_tree = args.k
    overwrite = args.ow

    # TODO - need file for constants - can't import contant from logger here (triggers initialisation)
    # from logger import VERBOSITY_ENV_VAR_NAME
    if verbosity_level:
        os.environ["WATERMARKER_VERBOSE"] = str(verbosity_level)

    # setup logging env var before importing other libraries
    from src.cli_configuration import cli_configuration
    from src.cli_validation import (valid_input_paths, valid_output_path,
                                    valid_prefix, valid_watermark_file)
    from utils import get_valid_media_files, watermark_files

    if not valid_input_paths(input_paths):
        exit(os.EX_DATAERR)

    if not valid_watermark_file(watermark_path):
        exit(os.EX_DATAERR)

    if not valid_prefix(prefix):
        exit(os.EX_DATAERR)

    if output_path and not valid_output_path(output_path):
        exit(os.EX_DATAERR)

    cli_configuration.watermark_file_path = watermark_path
    cli_configuration.output_dir_path = output_path
    cli_configuration.output_file_prefix = prefix
    cli_configuration.keep_output_tree = keep_output_tree
    cli_configuration.overwrite = overwrite

    media_files = get_valid_media_files(paths=input_paths, root_iteration=True)
    watermark_files(media_files)

    exit(os.EX_OK)
except Exception as e:
    import logging

    logger = logging.getLogger("watermarker")

    logger.info("Unexpected error occurred")
    logger.exception(e)

    exit(os.EX_SOFTWARE)
