
from typing import Optional, Any

from .bot import AioTomon


class Tomon(AioTomon):

    def __init__(self, config_object: Optional[Any] = None):
        if config_object is None:
            from . import default_config as config_object

        config_dict = {
            k: v
            for k, v in config_object.__dict__.items()
            if k.isupper() and not k.startswith('_')
        }

        super().__init__(**{k.lower(): v for k, v in config_dict.items()})


_bot: Optional[Tomon] = None


def init(config_object: Optional[Any] = None) -> None:
    global _bot
    _bot = Tomon(config_object)


def get_bot() -> Tomon:
    if _bot is None:
        raise ValueError('Tomon not yet initialized')
    return _bot
