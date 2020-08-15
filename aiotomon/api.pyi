
from typing import Awaitable, Any, Dict, Optional


class AsyncApi:

    def send_text(
        self, *,
        cid: str,
        content: str
    ) -> Awaitable[Dict[str, Any]]:
        '''
        发送频道文字消息

        :cid: 频道 ID ，应为字符串
        :content: 文字内容
        '''
        ...

    def send_image(
        self, *,
        cid: str,
        file_path: str,
        content: str = '',
        at_user: Optional[str] = None
    ) -> Awaitable[Dict[str, Any]]:
        '''
        发送频道图片消息

        :cid: 频道 ID ，应为字符串
        :file_path: 图片路径
        :content: 可选，附带文字内容
        :at_user: 可选，附带 at 的用户 id ，应为字符串
        '''
        ...

    def get_user_info(
        self
    ) -> Awaitable[Dict[str, Any]]:
        '''
        获取登录 bot 自身信息
        '''
        ...
