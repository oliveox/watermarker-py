import configparser


class _ConfigManager:

    def __init__(self):
        self.watermark_file_path = None
        self.output_dir_path = None
        self.config = configparser.ConfigParser()
        self.config.read("../config.ini")

    def get(self, section, key):
        return self.config.get(section, key)

    def get_watermark_positioning_configs(self):
        items = {}
        for option in self.config["WATERMARK_POSITIONING"]:
            value = self.config.get("WATERMARK_POSITIONING", option)

            # parse value to int if possible
            if not value:
                value = 0
            else:
                try:
                    value = int(value)
                except ValueError:
                    print(f"Failed to parse {option} to int. Value: {value}")

            items[option] = value
        return items

    def set_output_dir_path(self, dir_path):
        self.output_dir_path = dir_path

    def get_output_dir_path(self):
        return self.output_dir_path

    def set_watermark_file_path(self, file_path):
        self.watermark_file_path = file_path

    def get_watermark_file_path(self):
        return self.watermark_file_path


config_manager = _ConfigManager()