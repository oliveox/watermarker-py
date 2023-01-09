from typing import Optional


class _CLIConfiguration:
    def __init__(self) -> None:
        self._keep_output_tree = None
        self._overwrite: Optional[bool] = None
        self._output_file_prefix: Optional[str] = None
        self._watermark_file_path: Optional[str] = None
        self._output_dir_path: Optional[str] = None

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


cli_configuration = _CLIConfiguration()
