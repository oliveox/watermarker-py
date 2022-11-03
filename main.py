import argparse

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

parser.parse_args()

# check input and watermark exist
