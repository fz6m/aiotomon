

from typing import Any, Dict, List, Union

from .config import Message as M


class Message(dict):

    __setattr__ = dict.__setitem__
    __getattr__ = dict.__getitem__


def to_message(result: Dict[str, Any]) -> List[Union[str, Message]]:
    if not isinstance(result, dict):
        return result
    d = Message()
    for k, v in result.items():
        d[k] = to_message(v)
    return d


# TODO: More message types
# TODO: Avoid ugly, use mapping
def identify(result: Message) -> str:
    if result.get('status'):
        return M.NOTICE_ONLINE
    elif result.get('content'):
        return M.MESSAGE_CHANNEL
    return M.OTHER


class MessageSegment:

    @staticmethod
    def at(user_id: str) -> str:
        return f'<@{user_id}>'
