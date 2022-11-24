import os

from filetype import filetype

from src.config import config_manager
from src.media_utils_mixin import MediaUtilsMixin
from src.types import FileType, MediaFileOrientation, WatermarkRelativeSize


class File(MediaUtilsMixin):
    def __init__(self, path: str) -> None:
        self._watermark_scaling = None
        self._output_file_path = None
        self._watermark_overlay = None
        self._type = None
        self._orientation = None
        self.path = path

    def get_type(self):
        if self._type:
            return self._type

        kind = filetype.guess(self.path)

        if kind.mime.startswith("image"):
            self._type = FileType.IMAGE
        elif kind.mime.startswith("video"):
            self._type = FileType.VIDEO

        return self._type

    def get_orientation(self):
        if self._orientation:
            return self._orientation

        if self.get_type() == FileType.IMAGE:
            self._orientation = MediaUtilsMixin.get_image_orientation(self.path)
        elif self.get_type() == FileType.VIDEO:
            self._orientation = MediaUtilsMixin.get_video_orientation(self.path)

        return self._orientation

    def get_output_file_path(self) -> str:
        if self._output_file_path:
            return self._output_file_path

        output_dir_path = config_manager.get_output_dir_path()
        prefix = config_manager.get_output_file_prefix()
        basename = os.path.basename(self.path)

        if not prefix:
            prefix = "watermarked_"

        self._output_file_path = os.path.join(output_dir_path, f"{prefix}{basename}")
        return self._output_file_path

    def get_watermark_scaling(self):
        if self._watermark_scaling:
            return self._watermark_scaling

        watermark_image_ratio = MediaUtilsMixin.get_ratio(
            config_manager.watermark_file_path
        )
        watermark_relative_sizes = config_manager.get_watermark_relative_size()

        metadata = MediaUtilsMixin.get_width_height(self.path)
        if not metadata:
            raise

        width = metadata["width"]
        height = metadata["height"]

        if self._orientation == MediaFileOrientation.LANDSCAPE:
            watermark_height = (
                height
                * watermark_relative_sizes[
                    WatermarkRelativeSize.WATERMARK_TO_HEIGHT_RATIO
                ]
            )
            watermark_width = watermark_image_ratio * watermark_height
        elif self._orientation == MediaFileOrientation.PORTRAIT:
            watermark_width = (
                width
                * watermark_relative_sizes[
                    WatermarkRelativeSize.WATERMARK_TO_WIDTH_RATIO
                ]
            )
            watermark_height = watermark_width / watermark_image_ratio
        else:
            print(f"Invalid orientation: {self._orientation}")
            return

        self._watermark_scaling = (
            f"[1:v] scale={watermark_width}:{watermark_height} [wtrmrk];"
        )
        return self._watermark_scaling
