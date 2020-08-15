
import os
import aiofiles
from typing import Dict, Any

from .exceptions import FileTypeError


class FileIO:

    @staticmethod
    async def read_image(path: str) -> bytes:
        if not os.path.exists(path):
            raise IOError
        async with aiofiles.open(path, 'rb') as f:
            return await f.read()

    @staticmethod
    def get_file_info(file_path: str) -> Dict[str, str]:
        file_name = file_path.rsplit(
            '/', maxsplit=1)[-1] if '/' in file_path else file_path
        suffix = file_name.rsplit('.', maxsplit=1)[-1]
        if not any(i == suffix for i in {'jpg', 'png'}):
            raise FileTypeError
        return {
            'name': file_name,
            'content_type': 'image/jpeg' if suffix == 'jpg' else 'image/png'
        }


class Validate:

    @staticmethod
    def action(keys: set, params: Dict[str, Any]) -> bool:
        return all(i in params and i != '' for i in keys)
