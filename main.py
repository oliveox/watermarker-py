import argparse
import os

from utils import valid_watermark, valid_prefix

parser = argparse.ArgumentParser(prog='watermarker', description='Add watermark to images and videos')
parser.add_argument("--i", "--input", required=True, help="Input media files directory path | [Required]", nargs="+",
                    metavar="DIRECTORY/FILE PATH(S)")
parser.add_argument("--w", "--watermark", required=True, help="Watermark file path | [Required]", nargs=1,
                    metavar="WATERMARK PATH")
parser.add_argument("--p", "--prefix",
                    required=True, help="Prefix of the new file. OutputFilename = {prefix}{InputFilename} | [Required]",
                    nargs=1, metavar="OUTPUT FILENAME PREFIX")
parser.add_argument("--o", "--output",
                    required=False,
                    help="Output watermarked files drectory. If path doesn't exist, it will be created | [Optional]",
                    nargs=1, metavar="OUTPUT FILE(S) PATH")

args = parser.parse_args()

watermark_path = args.w[0]
prefix = args.p[0]

if not all(os.path.exists(i) for i in args.i):
    print("Input contains a path that doesn't exist")
    exit(1)

if not valid_watermark(watermark_path):
    exit(1)

if not valid_prefix(prefix):
    exit(1)

if args.o:
    if os.path.exists(args.o) and not os.path.isdir(args.o):
        print("Specified output path already exists and is not a directory")
        exit(1)

    if not os.path.exists(args.o):
        print("Output directory path doesn't exist. Creating it.")

        try:
            os.makedirs(args.o)
        except Exception as e:
            print(f"Failed to create output directory. Error: {e}")
            exit(1)
