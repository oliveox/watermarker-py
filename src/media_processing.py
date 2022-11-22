from typing import Optional

import ffmpeg
from filetype import filetype
from PIL import Image

from src.types import MediaFileOrientation, MediaFileSize


def get_overlay(
    position: str,
    margin_nord: Optional[int],
    margin_south: Optional[int],
    margin_east: Optional[int],
    margin_west: Optional[int],
) -> str:
    overlay = ""
    if position not in ["NE", "NC", "NW", "SE", "SC", "SW", "C", "CE", "CW"]:
        print(f"Invalid watermark position: {position}")

    if not margin_nord:
        margin_nord = 0
    if not margin_south:
        margin_south = 0
    if not margin_east:
        margin_east = 0
    if not margin_west:
        margin_west = 0

    def get_sign(value: int, inverse: bool) -> str:
        if value > 0:
            sign = "-" if inverse else "+"
        else:
            sign = "+" if inverse else "-"

        return f"{sign}{abs(value)}"

    def get_horizontal_margins(east: int, west: int) -> str:
        return f"{get_sign(east, False)}{get_sign(west, True)}"

    def get_vertical_margins(nord: int, south: int) -> str:
        return f"{get_sign(nord, False)}{get_sign(south, True)}"

    if position == "NE":
        overlay = (
            f"0{get_horizontal_margins(margin_east, margin_west)}"
            f":0{get_vertical_margins(margin_nord, margin_south)}"
        )
    elif position == "NC":
        overlay = (
            f"(main_w/2-overlay_w/2{get_horizontal_margins(margin_east, margin_west)}"
            f":0{get_vertical_margins(margin_nord, margin_south)}"
        )
    elif position == "NW":
        overlay = (
            f"main_w-overlay_w{get_horizontal_margins(margin_east, margin_west)}"
            f":0{get_vertical_margins(margin_nord, margin_south)}"
        )
    elif position == "SE":
        overlay = (
            f"0{get_horizontal_margins(margin_east, margin_west)}"
            f":main_h-overlay_h{get_vertical_margins(margin_nord, margin_south)}"
        )
    elif position == "SC":
        overlay = (
            f"(main_w/2-overlay_w/2{get_horizontal_margins(margin_east, margin_west)}"
            f":main_h-overlay_h{get_vertical_margins(margin_nord, margin_south)}"
        )
    elif position == "SW":
        overlay = (
            f"main_w-overlay_w{get_horizontal_margins(margin_east, margin_west)}"
            f":main_h-overlay_h{get_vertical_margins(margin_nord, margin_south)}"
        )
    elif position == "C":
        overlay = (
            f"(main_w/2-overlay_w/2{get_horizontal_margins(margin_east, margin_west)}"
            f":(main_h/2-overlay_h/2{get_vertical_margins(margin_nord, margin_south)})"
        )
    elif position == "CE":
        overlay = (
            f"0{get_horizontal_margins(margin_east, margin_west)}"
            f":(main_h/2-overlay_h/2{get_vertical_margins(margin_nord, margin_south)})"
        )
    elif position == "CW":
        overlay = (
            f"main_w-overlay_w{get_horizontal_margins(margin_east, margin_west)}"
            f":(main_h/2-overlay_h/2{get_vertical_margins(margin_nord, margin_south)})"
        )
    else:
        print(f"Invalid watermark position: {position}")

    return f"overlay={overlay}"


def get_image_orientation(path: str) -> str:
    image = Image.open(path)
    exif = image.getexif()
    orientation = exif.get(274, None)
    if isinstance(orientation, bytes):
        orientation = orientation.decode()
    # docs - will assume landscape if orientation == None (no available metadata)
    return (
        MediaFileOrientation.PORTRAIT
        if orientation in [5, 6, 7, 8]
        else MediaFileOrientation.LANDSCAPE
    )


def get_video_orientation(path: str) -> str:
    # ffprobe needs to be installed as a package on the client OS
    metadata = ffmpeg.probe(path)
    try:
        rotation = metadata["streams"][0]["tags"]["rotate"]  # noqa: F841
        # TODO - find video with rotate data
    except IndexError:
        # TODO - decide on logging format
        print(f"No video stream found in file: [{path}]")
    except KeyError:
        print(f"No rotation metadata found in file: [{path}]")

    # docs - will assume landscape if orientation == None (no available metadata)
    return MediaFileOrientation.LANDSCAPE


def get_watermarking_command(
    input_file_path: str,
    watermark_path: str,
    output_file_path: str,
    transpose: str,
    overlay: str,
    watermark_scaling: str,
) -> str:
    return (
        f"ffmpeg -y -i {input_file_path} -i {watermark_path} "
        f'-filter_complex "{transpose}{watermark_scaling}{overlay}" "{output_file_path}"'
    )


def get_watermark_image_ratio(path: str) -> float | None:
    metadata = get_media_file_ratio(path)
    if not metadata:
        return

    height = metadata["height"]
    width = metadata["width"]
    return width / height


def get_media_file_ratio(file_path: str) -> Optional[MediaFileSize]:
    metadata = ffmpeg.probe(file_path)

    # TODO - create a mediaFile class for each file
    # modularize metadata extraction
    try:
        if (
            not metadata
            or not metadata["streams"][0]["height"]
            or not metadata["streams"][0]["width"]
        ):
            print(f"No metadata found in file: [{file_path}]")
            return
    except IndexError:
        # TODO - decide on logging format
        print(f"No video stream found in file: [{file_path}]")
        return
    except KeyError:
        print(f"No rotation metadata found in file: [{file_path}]")
        return

    width = metadata["streams"][0]["width"]
    height = metadata["streams"][0]["height"]

    return {"width": width, "height": height}


def valid_media_file(path: str) -> bool:
    kind = filetype.guess(path)
    if kind is None:
        print(f"Cannot guess file type for: {path}")
        return False

    if not kind.mime.startswith("image") and not kind.mime.startswith("video"):
        print(f"Invalid media file: [{path}]. Mime: [{kind.mime}]")
        return False

    return True
