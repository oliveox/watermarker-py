from enum import Enum
from typing import TypedDict


class WidthHeight(TypedDict):
    width: int
    height: int


class FileType(Enum):
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    UNKNOWN = "unknown"


class MediaFileOrientation(Enum):
    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"


class WatermarkRelativeSize:
    WATERMARK_TO_HEIGHT_RATIO: str = "WATERMARK_TO_HEIGHT_RATIO"
    WATERMARK_TO_WIDTH_RATIO: str = "WATERMARK_TO_WIDTH_RATIO"
