
import asyncio
from collections import defaultdict
from typing import Optional, Any, Dict, Iterable, Awaitable, Callable, List

from .config import Nonce as No


class Event(dict):

    @staticmethod
    def from_payload(payload: Dict[str, Any]) -> 'Optional[Event]':
        try:
            resp = Event(payload)
            _ = resp.op, resp.e, resp.d

            # ! Ugly way, needs improvement
            if resp.d['nonce'] == No.IDENT:
                return None

            return resp
        except KeyError:
            return None

    def __getattr__(self, key) -> Optional[Any]:
        return self.get(key)

    def __setattr__(self, key, value):
        self[key] = value

    def __repr__(self) -> str:
        return f'<Event, {super().__repr__()}>'


class EventQueue:

    def __init__(self):
        self._subscribers = defaultdict(set)
        self._hooks_before = defaultdict(set)

    def subscribe(self, event: str, func: Callable) -> None:
        self._subscribers[event].add(func)

    def unsubscribe(self, event: str, func: Callable) -> None:
        if func in self._subscribers[event]:
            self._subscribers[event].remove(func)

    def hook_before(self, event: str, func: Callable) -> None:
        self._hooks_before[event].add(func)

    def unhook_before(self, event: str, func: Callable) -> None:
        if func in self._hooks_before[event]:
            self._hooks_before[event].remove(func)

    async def emit(self, event: str, *args, **kwargs) -> List[Any]:
        event_copy = event

        while True:
            await run_async_funcs(self._hooks_before[event], *args, **kwargs)
            event, *sub_event = event.rsplit('.', maxsplit=1)
            if not sub_event:
                break
        event = event_copy

        results = []
        while True:
            results += await run_async_funcs(self._subscribers[event],
                                             *args, **kwargs)
            event, *sub_event = event.rsplit('.', maxsplit=1)
            if not sub_event:
                break
        return results


async def run_async_funcs(funcs: Iterable[Callable[..., Awaitable[Any]]],
                          *args, **kwargs) -> List[Any]:
    results = []
    coros = []
    for f in funcs:
        coros.append(f(*args, **kwargs))
    if coros:
        results += await asyncio.gather(*coros)
    return results
