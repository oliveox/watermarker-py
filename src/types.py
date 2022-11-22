from typing import TypedDict


class MediaFileSize(TypedDict):
    width: int
    height: int


class FileType:
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    UNKNOWN = "unknown"


class MediaFileOrientation:
    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"


class WatermarkRelativeSize:
    WATERMARK_TO_HEIGHT_RATIO = "WATERMARK_TO_HEIGHT_RATIO"
    WATERMARK_TO_WIDTH_RATIO = "WATERMARK_TO_WIDTH_RATIO"
