import argparse
import os

try:
    parser = argparse.ArgumentParser(
        prog="watermarker", description="Add watermark to images and videos"
    )
    parser.add_argument(
        "--i",
        "--input",
        required=True,
        help="Input media files directory path",
        nargs="+",
        metavar="DIRECTORY/FILE PATH(S)",
    )
    parser.add_argument(
        "--w",
        "--watermark",
        required=True,
        help="Watermark file path",
        nargs=1,
        metavar="WATERMARK PATH",
        type=str,
    )
    parser.add_argument(
        "--p",
        "--prefix",
        required=True,
        help="Prefix of the new file. OutputFilename = {prefix}{InputFilename}",
        nargs=1,
        metavar="OUTPUT FILENAME PREFIX",
        type=str,
    )
    parser.add_argument(
        "--o",
        "--output",
        required=False,
        help="Output watermarked files drectory. If path doesn't exist, it will be created",
        nargs=1,
        metavar="OUTPUT FILE(S) PATH",
        type=str,
    )
    parser.add_argument(
        "--v",
        "--verbose",
        required=False,
        help="Set level of verbosity. 1 = Debug logs ; 2 = 1 + FFmpeg logs",
        nargs=1,
        metavar="VERBOSITY LEVEL",
        type=int,
    )

    args = parser.parse_args()

    input_paths = args.i
    watermark_path = args.w[0]
    prefix = args.p[0]
    output_path = args.o[0] if args.o else None
    verbosity_level = args.v[0]

    allowed_verbosity_values = [1, 2]
    if verbosity_level not in allowed_verbosity_values:
        print(f"Invalid verbosity value. Allowed values: {allowed_verbosity_values}")
        exit(os.EX_DATAERR)

    os.environ["WATERMARKER_VERBOSE"] = str(verbosity_level)

    # setup logging env var before importing other libraries
    from src.cli_validation import (valid_input_paths, valid_output_path,
                                    valid_prefix, valid_watermark_file)
    from src.config import config_manager
    from utils import get_valid_media_files, watermark_files

    if not valid_input_paths(input_paths):
        exit(os.EX_DATAERR)

    if not valid_watermark_file(watermark_path):
        exit(os.EX_DATAERR)

    if not valid_prefix(prefix):
        exit(os.EX_DATAERR)

    if output_path and not valid_output_path(output_path):
        exit(os.EX_DATAERR)

    config_manager.watermark_file_path = watermark_path
    config_manager.output_dir_path = output_path
    config_manager.output_file_prefix = prefix

    media_files = get_valid_media_files(input_paths)
    watermark_files(media_files)

    exit(os.EX_OK)
except Exception as e:
    print("Unexpected error occurred")
    print(e)
    exit(os.EX_SOFTWARE)
