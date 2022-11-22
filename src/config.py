import configparser

from src.media_processing import get_media_file_ratio, get_overlay
from src.types import MediaFileOrientation, WatermarkRelativeSize


class _ConfigManager:
    configuration_file_path = "config.ini"

    def __init__(self):
        self._watermark_relative_size = {}
        self._watermark_image_ratio = None
        self._watermark_position = None
        self._watermark_margins = None
        self._image_watermark_overlay = {}
        self._video_watermark_overlay = None
        self.output_file_prefix = None
        self.watermark_file_path = None
        self.output_dir_path = None

        self.config = configparser.ConfigParser()
        self.config.read(_ConfigManager.configuration_file_path)

    def get(self, section, key):
        return self.config.get(section, key)

    def get_watermark_relative_size(self):
        if self._watermark_relative_size:
            return self._watermark_relative_size

        self._watermark_relative_size = {
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

        return self._watermark_relative_size

    def get_watermark_position(self):
        if self._watermark_position:
            return self._watermark_position

        self._watermark_position = self.config.get("WATERMARK_POSITION", "position")
        return self._watermark_position

    def get_watermark_margins(self) -> dict:
        if self._watermark_margins:
            return self._watermark_margins

        items = {}
        for option in self.config["WATERMARK_MARGINS"]:
            value = self.config.get("WATERMARK_MARGINS", option)

            # parse value to int if possible
            if not value:
                value = 0
            else:
                try:
                    value = int(value)
                except ValueError:
                    print(f"Failed to parse {option} to int. Value: {value}")

            items[option] = value

        _watermark_margins = items
        return _watermark_margins

    def set_output_dir_path(self, dir_path):
        self.output_dir_path = dir_path

    def get_output_dir_path(self):
        return self.output_dir_path

    def set_watermark_file_path(self, file_path):
        self.watermark_file_path = file_path

    def get_watermark_file_path(self):
        return self.watermark_file_path

    def set_output_file_prefix(self, prefix):
        self.output_file_prefix = prefix

    def get_output_file_prefix(self):
        return self.output_file_prefix

    def get_image_watermark_overlay(self, file_orientation: MediaFileOrientation):
        if self._image_watermark_overlay.get(file_orientation):
            return self._image_watermark_overlay[file_orientation]

        watermark_margins = self.get_watermark_margins()
        watermark_position = self.get_watermark_position()

        if file_orientation == MediaFileOrientation.LANDSCAPE:
            self._image_watermark_overlay[
                file_orientation
            ] = f"[0:v][wtrmrk]{get_overlay(position=watermark_position, **watermark_margins)}"
        elif file_orientation == MediaFileOrientation.PORTRAIT:
            self._image_watermark_overlay[
                file_orientation
            ] = f"[mediaFile][wtrmrk]{get_overlay(position=watermark_position, **watermark_margins)}"

        return self._image_watermark_overlay[file_orientation]

    def get_video_watermark_overlay(self):
        if self._video_watermark_overlay:
            return self._video_watermark_overlay

        watermark_margins = self.get_watermark_margins()
        watermark_position = self.get_watermark_position()

        self._video_watermark_overlay = f"[0:v][wtrmrk]{get_overlay(position=watermark_position, **watermark_margins)}"
        return self._video_watermark_overlay

    def get_video_transpose(self):
        return ""

    def get_image_transpose(self, orientation: MediaFileOrientation):
        if orientation == MediaFileOrientation.LANDSCAPE:
            return ""
        elif orientation == MediaFileOrientation.PORTRAIT:
            return "[0:v]transpose=2 [mediaFile],"

    def get_watermark_image_ratio(self):
        if self._watermark_image_ratio:
            return self._watermark_image_ratio

        metadata = get_media_file_ratio(config_manager.watermark_file_path)
        if not metadata:
            return

        height = metadata["height"]
        width = metadata["width"]
        self._watermark_image_ratio = width / height

        return self._watermark_image_ratio


config_manager = _ConfigManager()
