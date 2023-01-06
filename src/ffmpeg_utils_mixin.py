from functools import cache
from typing import Optional


class FFmpegUtilsMixin:
    @staticmethod
    def get_watermarking_command(
        input_file_path: str,
        watermark_path: str,
        output_file_path: str,
        overlay: str,
        watermark_scaling: str,
    ) -> list[str]:
        return [
            "ffmpeg",
            "-i",
            input_file_path,
            "-i",
            watermark_path,
            "-filter_complex",
            f"{watermark_scaling}{overlay}",
            output_file_path,
        ]

    @staticmethod
    @cache
    def get_overlay(
        position: str,
        margin_nord: Optional[int],
        margin_south: Optional[int],
        margin_east: Optional[int],
        margin_west: Optional[int],
    ) -> str:
        if not margin_nord:
            margin_nord = 0
        if not margin_south:
            margin_south = 0
        if not margin_east:
            margin_east = 0
        if not margin_west:
            margin_west = 0

        # W / H - main input width and height
        # w / h - watermark width and height
        overlays_by_position = {
            "NE": f"W-w-{margin_east}:{margin_nord}",
            "NC": f"W/2-w/2:{margin_nord}",
            "NW": f"{margin_west}:{margin_nord}",
            "CE": f"W-w-{margin_east}:H/2-h/2",
            "C": "W/2-w/2:H/2-h/2",
            "CW": f"{margin_west}:H/2-h/2",
            "SE": f"W-w-{margin_east}:H-h-{margin_south}",
            "SC": f"W/2-w/2:H-h-{margin_south}",
            "SW": f"{margin_west}:H-h-{margin_south}",
        }
        overlay = overlays_by_position[position]

        return f"overlay={overlay}"
