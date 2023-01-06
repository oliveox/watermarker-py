import os
from functools import cache
from typing import Optional

from filetype import filetype

from logger import logger
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
    def dimensions(self) -> dict[str, int]:
        medial_file_width_height = MediaUtilsMixin.get_media_file_width_height(self.path)
        if not medial_file_width_height:
            raise Exception("Cannot get width and height for media file", self.path)

        return {
            "width": medial_file_width_height["width"],
            "height": medial_file_width_height["height"],
        }

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

        watermark_width_height = MediaUtilsMixin.get_media_file_width_height(config_manager.watermark_file_path)
        if not watermark_width_height:
            raise Exception("Cannot get width and height for watermark file", config_manager.watermark_file_path)
        watermark_width = watermark_width_height["width"]
        watermark_height = watermark_width_height["height"]
        watermark_ratio = watermark_width / watermark_height

        media_file_width = self.dimensions["width"]
        media_file_height = self.dimensions["height"]

        # compute the watermark scaling based on the smallest media file side, which depends on the orientation
        if self.orientation == MediaFileOrientation.LANDSCAPE:
            watermark_scaled_height = (
                watermark_relative_sizes[WatermarkRelativeSize.WATERMARK_HEIGHT_RATIO] * media_file_height / 100
            )
            watermark_scaled_width = watermark_ratio * watermark_scaled_height
        elif self.orientation == MediaFileOrientation.PORTRAIT:
            watermark_scaled_width = (
                watermark_relative_sizes[WatermarkRelativeSize.WATERMARK_WIDTH_RATIO] * media_file_width / 100
            )
            watermark_scaled_height = watermark_scaled_width / watermark_ratio
        else:
            raise Exception(f"Unknown orientation: {self.orientation}")

        rounded_watermark_scaled_width = round(watermark_scaled_width, 2)
        rounded_watermark_scaled_height = round(watermark_scaled_height, 2)

        logger.debug(
            f"Dimensions(WxH). File: {media_file_width} x {media_file_height}."
            f" Watermark: {rounded_watermark_scaled_width} x {rounded_watermark_scaled_height}"
        )

        return f"[1:v] scale={rounded_watermark_scaled_width}:{rounded_watermark_scaled_height} [wtrmrk];"

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(path={self.path}, type={self.type}, orientation={self.orientation},"
            f" output_file_path={self.output_file_path}, output_subdir={self.output_subdir})"
        )


# 680x383.gif
