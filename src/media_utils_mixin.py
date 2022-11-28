from functools import cache
from typing import Optional

import ffmpeg
from PIL import Image

from src.types import MediaFileOrientation, WidthHeight


class MediaUtilsMixin:
    @staticmethod
    @cache
    def get_image_orientation(file_path: str) -> str:
        image = Image.open(file_path)
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

    @staticmethod
    @cache
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

    @classmethod
    @cache
    def get_ratio(cls, file_path: str):
        metadata = cls.get_width_height(file_path)

        height = metadata["height"]
        width = metadata["width"]

        return width / height

    @staticmethod
    @cache
    def get_width_height(file_path: str) -> Optional[WidthHeight]:
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
