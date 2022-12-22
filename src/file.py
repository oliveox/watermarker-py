import os
from functools import cache
from typing import Optional

from filetype import filetype

from src.config import config_manager
from src.custom_types import (FileType, MediaFileOrientation,
                              WatermarkRelativeSize)
from src.media_utils_mixin import MediaUtilsMixin


class File(MediaUtilsMixin):
    def __init__(self, path: str, output_subdir: str = "") -> None:
        self._watermark_scaling = None
        self._output_file_path = None

        self.path = path
        self._output_subdir = output_subdir

    @property
    def output_subdir(self) -> str:
        return self._output_subdir

    @output_subdir.setter
    def output_subdir(self, value: str) -> None:
        self._output_subdir = value

    @property
    @cache
    def type(self) -> FileType | None:
        kind = filetype.guess(self.path)
        if kind.mime.startswith("image"):
            return FileType.IMAGE
        elif kind.mime.startswith("video"):
            return FileType.VIDEO

        return None

    @property
    @cache
    def orientation(self) -> Optional[str]:
        if self.type == FileType.IMAGE:
            return MediaUtilsMixin.get_image_orientation(self.path)
        elif self.type == FileType.VIDEO:
            return MediaUtilsMixin.get_video_orientation(self.path)

        return None

    @property
    @cache
    def output_file_path(self) -> str:
        prefix = config_manager.output_file_prefix
        if not prefix:
            raise ValueError("Output file prefix is not set")

        output_dir_path = config_manager.output_dir_path
        basename = os.path.basename(self.path)

        return os.path.join(output_dir_path, self.output_subdir, f"{prefix}{basename}")

    @property
    @cache
    def watermark_scaling(self) -> str:
        watermark_relative_sizes = config_manager.watermark_relative_size

        width_height = MediaUtilsMixin.get_width_height(self.path)
        if not width_height:
            raise Exception("Cannot get width and height for media file", self.path)
        width = width_height["width"]
        height = width_height["height"]
        media_file_ratio = width / height

        if self.orientation == MediaFileOrientation.LANDSCAPE:
            watermark_height = height * watermark_relative_sizes[WatermarkRelativeSize.WATERMARK_TO_HEIGHT_RATIO]
            watermark_width = media_file_ratio * watermark_height
        elif self.orientation == MediaFileOrientation.PORTRAIT:
            watermark_width = width * watermark_relative_sizes[WatermarkRelativeSize.WATERMARK_TO_WIDTH_RATIO]
            watermark_height = watermark_width / media_file_ratio
        else:
            raise Exception(f"Unknown orientation: {self.orientation}")

        return f"[1:v] scale={watermark_width}:{watermark_height} [wtrmrk];"

    def __repr__(self):
        return f"{self.__class__.__name__}(path={self.path}, type={self.type}, orientation={self.orientation}, output_file_path={self.output_file_path}, output_subdir={self.output_subdir})"
