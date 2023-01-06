import configparser
from functools import cache
from typing import Optional

from src.custom_types import WatermarkRelativeSize
from src.ffmpeg_utils_mixin import FFmpegUtilsMixin
from src.media_utils_mixin import MediaUtilsMixin


class _ConfigManager(MediaUtilsMixin, FFmpegUtilsMixin):
    configuration_file_path = "config.ini"
    WATERMARK_POSITIONS = ["NE", "NC", "NW", "SE", "SC", "SW", "C", "CE", "CW"]

    def __init__(self) -> None:
        self._keep_output_tree = None
        self._overwrite: Optional[bool] = None
        self._output_file_prefix: Optional[str] = None
        self._watermark_file_path: Optional[str] = None
        self._output_dir_path: Optional[str] = None

        self.config = configparser.ConfigParser()
        self.config.read(_ConfigManager.configuration_file_path)

    def get(self, section: str, key: str) -> str:
        return self.config.get(section, key)

    @property
    def keep_output_tree(self) -> Optional[bool]:
        return self._keep_output_tree

    @keep_output_tree.setter
    def keep_output_tree(self, keep_output_tree: bool) -> None:
        self._keep_output_tree = keep_output_tree

    @property
    def overwrite(self) -> Optional[bool]:
        return self._overwrite

    @overwrite.setter
    def overwrite(self, overwrite: bool) -> None:
        self._overwrite = overwrite

    @property
    def output_file_prefix(self) -> Optional[str]:
        return self._output_file_prefix

    @output_file_prefix.setter
    def output_file_prefix(self, prefix: str) -> None:
        self._output_file_prefix = prefix

    @property
    def output_dir_path(self) -> Optional[str]:
        return self._output_dir_path

    @output_dir_path.setter
    def output_dir_path(self, dir_path: str) -> None:
        self._output_dir_path = dir_path

    @property
    def watermark_file_path(self) -> Optional[str]:
        return self._watermark_file_path

    @watermark_file_path.setter
    def watermark_file_path(self, file_path: str) -> None:
        self._watermark_file_path = file_path

    @property
    @cache
    def watermark_relative_size(self) -> dict[str, float]:
        watermark_height_ratio = self.config.get(
            "WATERMARK_RELATIVE_SIZE",
            WatermarkRelativeSize.WATERMARK_HEIGHT_RATIO,
        )
        watermark_width_ratio = self.config.get(
            "WATERMARK_RELATIVE_SIZE",
            WatermarkRelativeSize.WATERMARK_WIDTH_RATIO,
        )

        if watermark_width_ratio.endswith("%") and watermark_height_ratio.endswith("%"):
            width_percentage = watermark_width_ratio[:-1]
            height_percentage = watermark_height_ratio[:-1]

            if (
                not width_percentage.isnumeric()
                or not height_percentage.isnumeric()
                or int(width_percentage) < 0
                or int(width_percentage) > 100
                or int(height_percentage) < 0
                or int(height_percentage) > 100
            ):
                raise ValueError("Watermark width and height ratio must be numeric and between 0 and 100")

            return {
                WatermarkRelativeSize.WATERMARK_HEIGHT_RATIO: int(height_percentage),
                WatermarkRelativeSize.WATERMARK_WIDTH_RATIO: int(width_percentage),
            }
        else:
            raise ValueError("Watermark relative size must be in %")

    @property
    def watermark_position(self) -> str:
        position = self.config.get("WATERMARK_POSITION", "position")
        if position not in self.WATERMARK_POSITIONS:
            raise ValueError(f"Invalid watermark position: [{position}]. Possible values {self.WATERMARK_POSITIONS}")

        return position

    @property
    @cache
    def watermark_margins(self) -> dict[str, str]:
        margins = self.config["WATERMARK_MARGINS"]
        for option in margins:
            value: str = margins.get(option)
            if value.endswith("%"):
                percentage = value[:-1]
                if not percentage.isnumeric() or int(percentage) < 0 or int(percentage) > 100:
                    raise ValueError(f"Invalid watermark margin percentage: [{value}]")
            elif value.endswith("px"):
                pixels = value[:-2]
                if not pixels.isnumeric() or int(pixels) < 0:
                    raise ValueError(f"Invalid watermark margin pixels: [{value}]")
            else:
                raise ValueError(f"Invalid watermark margin: [{value}]")

        return dict(margins)

    @cache
    def watermark_overlay(self, width: int, height: int) -> str:
        margins_in_pixels = self._get_margins_in_pixels(width, height)
        overlay = FFmpegUtilsMixin.get_overlay(position=self.watermark_position, **margins_in_pixels)
        return f"[0:v][wtrmrk]{overlay}"

    @cache
    def _get_margins_in_pixels(self, width: int, height: int) -> dict[str, int]:
        # convert config watermark percentage margins in pixels
        margins_in_pixels = {}

        for margin in self.watermark_margins:
            value = self.watermark_margins[margin]
            if value.endswith("%"):
                percentage = int(value[:-1])
                if margin in ["margin_nord", "margin_south"]:
                    margins_in_pixels[margin] = int(percentage * height / 100)
                elif margin in ["margin_east", "margin_west"]:
                    margins_in_pixels[margin] = int(percentage * width / 100)
                else:
                    raise ValueError(f"Invalid margin: {margin}")
            else:
                margins_in_pixels[margin] = self.watermark_margins[margin]

        return margins_in_pixels


config_manager = _ConfigManager()
