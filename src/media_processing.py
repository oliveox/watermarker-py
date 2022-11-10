from PIL import Image
import ffmpeg
from src.constants import constants


def get_overlay(position, margin_nord, margin_south, margin_east, margin_west):
    overlay = ""
    if position not in ['NE', 'NC', 'NW', 'SE', 'SC', 'SW', 'C', 'CE', 'CW']:
        print(f"Invalid watermark position: {position}")

    if not margin_nord:
        margin_nord = 0
    if not margin_south:
        margin_south = 0
    if not margin_east:
        margin_east = 0
    if not margin_west:
        margin_west = 0

    def get_sign(value, inverse):
        if value > 0:
            sign = '-' if inverse else '+'
        else:
            sign = '+' if inverse else '-'

        return f"{sign}{abs(value)}"

    def get_horizontal_margins(east, west):
        return f"{get_sign(east, False)}{get_sign(west, True)}"

    def get_vertical_margins(nord, south):
        return f"{get_sign(nord, False)}{get_sign(south, True)}"

    if position == 'NE':
        overlay = f"0{get_horizontal_margins(margin_east, margin_west)}:0{get_vertical_margins(margin_nord, margin_south)}"
    elif position == 'NC':
        overlay = f"(main_w/2-overlay_w/2{get_horizontal_margins(margin_east, margin_west)}:0{get_vertical_margins(margin_nord, margin_south)}"
    elif position == 'NW':
        overlay = f"main_w-overlay_w{get_horizontal_margins(margin_east, margin_west)}:0{get_vertical_margins(margin_nord, margin_south)}"
    elif position == 'SE':
        overlay = f"0{get_horizontal_margins(margin_east, margin_west)}:main_h-overlay_h{get_vertical_margins(margin_nord, margin_south)}"
    elif position == 'SC':
        overlay = f"(main_w/2-overlay_w/2{get_horizontal_margins(margin_east, margin_west)}:main_h-overlay_h{get_vertical_margins(margin_nord, margin_south)}"
    elif position == 'SW':
        overlay = f"main_w-overlay_w{get_horizontal_margins(margin_east, margin_west)}:main_h-overlay_h{get_vertical_margins(margin_nord, margin_south)}"
    elif position == 'C':
        overlay = f"(main_w/2-overlay_w/2{get_horizontal_margins(margin_east, margin_west)}:(main_h/2-overlay_h/2{get_vertical_margins(margin_nord, margin_south)})"
    elif position == 'CE':
        overlay = f"0{get_horizontal_margins(margin_east, margin_west)}:(main_h/2-overlay_h/2{get_vertical_margins(margin_nord, margin_south)})"
    elif position == 'CW':
        overlay = f"main_w-overlay_w{get_horizontal_margins(margin_east, margin_west)}:(main_h/2-overlay_h/2{get_vertical_margins(margin_nord, margin_south)})"
    else:
        print(f"Invalid watermark position: {position}")

    return f"overlay={overlay}"


def get_image_orientation(path):
    image = Image.open(path)
    exif = image.getexif()
    orientation = exif.get(274, None)
    if isinstance(orientation, bytes):
        orientation = orientation.decode()
    # docs - will assume landscape if orientation == None (no available metadata)
    return constants.PORTRAIT if orientation in [5, 6, 7, 8] else constants.LANDSCAPE


def get_video_orientation(path):
    # ffprobe needs to be installed as a package on the client OS
    metadata = ffmpeg.probe(path)
    try:
        rotation = metadata['streams'][0]['tags']['rotate']
        # TODO - find video with rotate data
    except IndexError:
        # TODO - decide on logging format
        print(f"No video stream found in file: [{path}]")
    except KeyError:
        print(f"No rotation metadata found in file: [{path}]")

    # docs - will assume landscape if orientation == None (no available metadata)
    return constants.LANDSCAPE


def get_watermarking_command(input_file_path, watermark_path, output_file_path, transpose, overlay, watermark_scaling):
    return f'ffmpeg -y -i {input_file_path} -i {watermark_path} -filter_complex "{transpose}{watermark_scaling}{overlay}" "{output_file_path}"'


def get_watermark_scaling(path, orientation, watermark_image_ratio):
    watermark_to_height_ratio = 0.05
    watermark_to_width_ratio = 0.2

    metadata = get_media_file_size(path)
    if not metadata:
        return

    width = metadata['width']
    height = metadata['height']

    if orientation == constants.LANDSCAPE:
        watermark_height = height * watermark_to_height_ratio
        watermark_width = watermark_image_ratio * watermark_height
    elif orientation == constants.PORTRAIT:
        watermark_width = width * watermark_to_width_ratio
        watermark_height = watermark_width / watermark_image_ratio
    else:
        print(f"Invalid orientation: {orientation}")
        return

    return f"[1:v] scale={watermark_width}:{watermark_height} [wtrmrk];"


def get_watermark_image_ratio(path):
    metadata = get_media_file_size(path)
    if not metadata:
        return

    width = metadata['width']
    height = metadata['height']
    return width / height


def get_media_file_size(file_path):
    metadata = ffmpeg.probe(file_path)

    # TODO - create a mediaFile class for each file
    # modularize metadata extraction
    try:
        if not metadata or not metadata['streams'][0]['height'] or not metadata['streams'][0]['width']:
            print(f"No metadata found in file: [{path}]")
            return
    except IndexError:
        # TODO - decide on logging format
        print(f"No video stream found in file: [{path}]")
        return
    except KeyError:
        print(f"No rotation metadata found in file: [{path}]")
        return

    width = metadata['streams'][0]['width']
    height = metadata['streams'][0]['height']

    return {
        'width': width,
        'height': height
    }
