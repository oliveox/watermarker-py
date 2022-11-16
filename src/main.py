import argparse

from src.cli import (valid_input_paths, valid_output_path, valid_prefix,
                     valid_watermark_file)
from src.config import config_manager
from utils import process_paths

parser = argparse.ArgumentParser(
    prog="watermarker", description="Add watermark to images and videos"
)
parser.add_argument(
    "--i",
    "--input",
    required=True,
    help="Input media files directory path | [Required]",
    nargs="+",
    metavar="DIRECTORY/FILE PATH(S)",
)
parser.add_argument(
    "--w",
    "--watermark",
    required=True,
    help="Watermark file path | [Required]",
    nargs=1,
    metavar="WATERMARK PATH",
)
parser.add_argument(
    "--p",
    "--prefix",
    required=True,
    help="Prefix of the new file. OutputFilename = {prefix}{InputFilename} | [Required]",
    nargs=1,
    metavar="OUTPUT FILENAME PREFIX",
)
parser.add_argument(
    "--o",
    "--output",
    required=False,
    help="Output watermarked files drectory. If path doesn't exist, it will be created | [Optional]",
    nargs=1,
    metavar="OUTPUT FILE(S) PATH",
)
# TODO - maybe also support files for output (have to check if input is only one file)

args = parser.parse_args()

input_paths = args.i
watermark_path = args.w[0]
prefix = args.p[0]
output_path = args.o[0] if args.o else None

if not valid_input_paths(input_paths):
    exit(1)

if not valid_watermark_file(watermark_path):
    exit(1)

if not valid_prefix(prefix):
    exit(1)

if output_path and not valid_output_path(output_path):
    exit(1)

config_manager.set_watermark_file_path(watermark_path)
config_manager.set_output_dir_path(output_path)
process_paths(input_paths)

exit(0)
