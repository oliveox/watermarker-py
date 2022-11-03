import argparse

parser = argparse.ArgumentParser(description='Add watermark to images and videos')
parser.add_argument("--i", "--input", help="Input media files directory path | [Required]")
parser.add_argument("--w", "--watermark", help="Watermark file path | [Required]")
parser.add_argument("--p", "--prefix",
                    help="Prefix of the new file. OutputFilename = {prefix}{InputFilename} | [Required]")
parser.add_argument("--o", "--output",
                    help="Output watermarked files drectory. If path doesn't exist, it will be created | [Optional]")

parser.parse_args()
"""
arguments

- input dir / input file (mandatory)
- watermark path (mandatory)
- prefix of new file (optiona;)
- output dir (optional)
- position of watermark (optional)
"""
