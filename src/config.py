import configparser
from functools import cache
from typing import Optional

from src.custom_types import MediaFileOrientation, WatermarkRelativeSize
from src.ffmpeg_utils_mixin import FFmpegUtilsMixin
from src.media_utils_mixin import MediaUtilsMixin


class _ConfigManager(MediaUtilsMixin, FFmpegUtilsMixin):
    configuration_file_path = "config.ini"
    video_transpose = ""

    def __init__(self) -> None:
        self._output_file_prefix: Optional[str] = None
        self._watermark_file_path: Optional[str] = None
        self._output_dir_path: Optional[str] = None

        self.config = configparser.ConfigParser()
        self.config.read(_ConfigManager.configuration_file_path)

    def get(self, section: str, key: str) -> str:
        return self.config.get(section, key)

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
    def watermark_relative_size(self) -> dict[str, float]:
        return {
            WatermarkRelativeSize.WATERMARK_TO_HEIGHT_RATIO: float(
                self.config.get(
                    "WATERMARK_RELATIVE_SIZE",
                    WatermarkRelativeSize.WATERMARK_TO_HEIGHT_RATIO,
                )
            ),
            WatermarkRelativeSize.WATERMARK_TO_WIDTH_RATIO: float(
                self.config.get(
                    "WATERMARK_RELATIVE_SIZE",
                    WatermarkRelativeSize.WATERMARK_TO_WIDTH_RATIO,
                )
            ),
        }

    @property
    def watermark_position(self) -> str:
        return self.config.get("WATERMARK_POSITION", "position")

    @property
    def watermark_margins(self) -> dict[str, int]:
        items = {}
        for option in self.config["WATERMARK_MARGINS"]:
            value: str = self.config.get("WATERMARK_MARGINS", option)

            int_value: int
            if not value:
                int_value = 0
            else:
                try:
                    int_value = int(value)
                except ValueError:
                    raise ValueError(
                        f"Failed to parse watermark margin {option} to int. Value: {value}"
                    )

            items[option] = int_value

        return items

    @cache
    def get_image_watermark_overlay(
        self, file_orientation: MediaFileOrientation
    ) -> str:
        overlay = FFmpegUtilsMixin.get_overlay(
            position=self.watermark_position, **self.watermark_margins
        )
        if file_orientation == MediaFileOrientation.LANDSCAPE:
            return f"[0:v][wtrmrk]{overlay}"
        elif file_orientation == MediaFileOrientation.PORTRAIT:
            return f"[mediaFile][wtrmrk]{overlay}"
        else:
            raise ValueError(f"Invalid orientation: {file_orientation}")

    @property
    def video_watermark_overlay(self) -> str:
        overlay = FFmpegUtilsMixin.get_overlay(
            position=self.watermark_position, **self.watermark_margins
        )

        return f"[0:v][wtrmrk]{overlay}"

    @staticmethod
    def get_image_transpose(orientation: MediaFileOrientation) -> str:
        if orientation == MediaFileOrientation.LANDSCAPE:
            return ""
        elif orientation == MediaFileOrientation.PORTRAIT:
            return "[0:v]transpose=2 [mediaFile],"
        else:
            raise ValueError(f"Invalid orientation: {orientation}")


config_manager = _ConfigManager()
