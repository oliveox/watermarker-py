import os
from functools import cache

from filetype import filetype

from src.config import config_manager
from src.media_utils_mixin import MediaUtilsMixin
from src.types import FileType, MediaFileOrientation, WatermarkRelativeSize


class File(MediaUtilsMixin):
    def __init__(self, path: str) -> None:
        self._watermark_scaling = None
        self._output_file_path = None
        self.path = path

    @property
    @cache
    def type(self):
        kind = filetype.guess(self.path)
        if kind.mime.startswith("image"):
            return FileType.IMAGE
        elif kind.mime.startswith("video"):
            return FileType.VIDEO

    @property
    @cache
    def orientation(self):
        if self.type == FileType.IMAGE:
            return MediaUtilsMixin.get_image_orientation(self.path)
        elif self.type == FileType.VIDEO:
            return MediaUtilsMixin.get_video_orientation(self.path)

    @property
    @cache
    def output_file_path(self) -> str:
        output_dir_path = config_manager.output_dir_path
        prefix = config_manager.output_file_prefix
        basename = os.path.basename(self.path)

        if not prefix:
            prefix = "watermarked_"

        return os.path.join(output_dir_path, f"{prefix}{basename}")

    @property
    @cache
    def watermark_scaling(self):
        watermark_image_ratio = MediaUtilsMixin.get_ratio(
            config_manager.watermark_file_path
        )
        watermark_relative_sizes = config_manager.watermark_relative_size

        metadata = MediaUtilsMixin.get_width_height(self.path)
        if not metadata:
            raise

        width = metadata["width"]
        height = metadata["height"]

        if self.orientation == MediaFileOrientation.LANDSCAPE:
            watermark_height = (
                height
                * watermark_relative_sizes[
                    WatermarkRelativeSize.WATERMARK_TO_HEIGHT_RATIO
                ]
            )
            watermark_width = watermark_image_ratio * watermark_height
        elif self.orientation == MediaFileOrientation.PORTRAIT:
            watermark_width = (
                width
                * watermark_relative_sizes[
                    WatermarkRelativeSize.WATERMARK_TO_WIDTH_RATIO
                ]
            )
            watermark_height = watermark_width / watermark_image_ratio
        else:
            print(f"Invalid orientation: {self.orientation}")
            return

        return f"[1:v] scale={watermark_width}:{watermark_height} [wtrmrk];"
