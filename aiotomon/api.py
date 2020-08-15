
import abc
import functools
from typing import Callable, Any, Union, Awaitable


class Api:

    @abc.abstractmethod
    async def call_action(self, action: str, **params) -> Union[Awaitable[Any], Any]:
        pass

    def __getattr__(self, item: str) -> Callable[..., Union[Awaitable[Any], Any]]:
        return functools.partial(self.call_action, item)


class AsyncApi(Api):

    @abc.abstractmethod
    async def call_action(self, action: str, **params) -> Any:
        pass
