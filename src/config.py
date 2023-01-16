import configparser
import logging
from functools import cache

from src.custom_types import WatermarkRelativeSize
from src.ffmpeg_utils_mixin import FFmpegUtilsMixin
from src.media_utils_mixin import MediaUtilsMixin

logger = logging.getLogger("watermarker")


class IncorrectWatermarkConfigurationError(Exception):
    pass


class _ConfigManager(MediaUtilsMixin, FFmpegUtilsMixin):
    configuration_file_path = "config.ini"
    WATERMARK_POSITIONS = ["NE", "NC", "NW", "SE", "SC", "SW", "C", "CE", "CW"]
    MARGINS_BY_POSITION = {
        "NE": ["margin_east", "margin_nord"],
        "NC": ["margin_nord"],
        "NW": ["margin_west", "margin_nord"],
        "CE": ["margin_east"],
        "C": [],
        "CW": ["margin_west"],
        "SE": ["margin_east", "margin_south"],
        "SC": ["margin_south"],
        "SW": ["margin_west", "margin_south"],
    }

    def __init__(self) -> None:
        self.config = configparser.ConfigParser()
        self.config.read(_ConfigManager.configuration_file_path)

    def get(self, section: str, key: str) -> str:
        return self.config.get(section, key)

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
                raise IncorrectWatermarkConfigurationError(
                    "Watermark width and height ratio must be numeric percentage and between 0 and 100. E.g. 50%%"
                )

            return {
                WatermarkRelativeSize.WATERMARK_HEIGHT_RATIO: int(height_percentage),
                WatermarkRelativeSize.WATERMARK_WIDTH_RATIO: int(width_percentage),
            }
        else:
            raise IncorrectWatermarkConfigurationError("Watermark relative size must be in %")

    @property
    def watermark_position(self) -> str:
        position = self.config.get("WATERMARK_POSITION", "position")
        if position not in self.WATERMARK_POSITIONS:
            raise IncorrectWatermarkConfigurationError(
                f"Invalid watermark position: [{position}]. Possible values {self.WATERMARK_POSITIONS}"
            )

        return position

    @property
    @cache
    def watermark_margins(self) -> dict[str, str]:
        margins = self.config["WATERMARK_MARGINS"]
        for option in margins:
            try:
                value: str = margins.get(option)
            except configparser.InterpolationSyntaxError as e:
                raise IncorrectWatermarkConfigurationError(f"Invalid value for watermark margin [{option}]. {e}")
            if value.endswith("%"):
                percentage = value[:-1]
                if not percentage.isnumeric() or int(percentage) < 0 or int(percentage) > 100:
                    raise IncorrectWatermarkConfigurationError(f"Invalid watermark margin percentage: [{value}]")
            elif value.endswith("px"):
                pixels = value[:-2]
                if not pixels.isnumeric() or int(pixels) < 0:
                    raise IncorrectWatermarkConfigurationError(f"Invalid watermark margin pixels: [{value}]")
            else:
                raise IncorrectWatermarkConfigurationError(f"Invalid watermark margin: [{value}]")

        return dict(margins)

    @cache
    def watermark_overlay(self, file_path: str, width: int, height: int) -> str:
        margins_in_pixels = self._get_margins_in_pixels(width, height)

        # warn if watermark margins bigger than media file size
        # TODO - skip comparison if position relevant margins are given in percentage
        self._compare_margins_to_file_size(margins_in_pixels, file_path, width, height)

        overlay = FFmpegUtilsMixin.get_overlay(position=self.watermark_position, **margins_in_pixels)
        return f"[0:v][wtrmrk]{overlay}"

    def _compare_margins_to_file_size(self, watermark_pixel_margins, file_path, file_width, file_height):
        for margin_name in self.MARGINS_BY_POSITION[self.watermark_position]:
            margin_value = watermark_pixel_margins[margin_name]
            if margin_name in ["margin_nord", "margin_south"] and margin_value > file_height:
                logger.warning(
                    f"Watermark will be cropped. Watermark margin [name: {margin_name}, value: {margin_value}px] "
                    f"is bigger than file height [file path: {file_path}, file_height: {file_height}px]"
                )
            if margin_name in ["margin_east", "margin_west"] and margin_value > file_width:
                logger.warning(
                    f"Watermark will be cropped. Watermark margin [name: {margin_name}, value: {margin_value}px] "
                    f"is bigger than file width [file path: {file_path}, file_height: {file_height}px]"
                )

    @cache
    def _get_margins_in_pixels(self, width: int, height: int) -> dict[str, int]:
        # convert config watermark percentage margins in pixels
        margins_in_pixels = {}
        margins = self.watermark_margins

        for margin in margins:
            value = margins[margin]
            if value.endswith("%"):
                percentage = int(value[:-1])
                if margin in ["margin_nord", "margin_south"]:
                    margins_in_pixels[margin] = int(percentage * height / 100)
                elif margin in ["margin_east", "margin_west"]:
                    margins_in_pixels[margin] = int(percentage * width / 100)
                else:
                    raise IncorrectWatermarkConfigurationError(f"Invalid margin name: {margin}")
            else:
                # already in pixels
                margins_in_pixels[margin] = int(margins[margin][:-2])  # remove the 'px' at the end

        return margins_in_pixels


config_manager = _ConfigManager()
