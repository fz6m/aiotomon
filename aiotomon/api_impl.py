

import logging
import functools
import aiohttp
from aiohttp import FormData
from typing import Any, Dict, Optional, Union

from .api import AsyncApi
from .api_func import ChannelApi
from .utils import FileIO, Validate
from .config import Channel, Nonce as No
from .message import MessageSegment as Ms
from .exceptions import HttpFailed, NetworkError

try:
    import ujson as json
except ImportError:
    import json


class HttpApi(AsyncApi):

    def __init__(self, api_root: str,
                 user_name: str,
                 password: str, *,
                 timeout_sec: int,
                 token: Optional[str],
                 user_info: Optional[Dict[str, Any]] = None):

        self._api_root = api_root
        self._user_name = user_name
        self._password = password
        self._timeout_sec = timeout_sec
        self._token = token
        self._user_info = user_info

        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S')
        self._log = logging.getLogger(__name__)

    async def call_action(self, action: str, **kwargs) -> Any:

        mapping = {
            ChannelApi.login: self._action_login,
            # POST
            ChannelApi.send_image: self._action_send_image,
            ChannelApi.send_text: self._post(Channel.SEND_TEXT.format(channelId=kwargs.get('cid'))),
            # GET
            ChannelApi.get_user_info: self._get(Channel.GET_USER_INFO)
        }

        try:
            return await mapping[action](**kwargs)
        except aiohttp.InvalidURL:
            raise NetworkError('Api parsing error, please check the root URL')
        except aiohttp.ClientError:
            raise NetworkError('aiohttp connection error')

    async def _action_login(self, **params) -> Dict[str, Any]:

        self._log.info('开始登陆......')

        login_info = {
            'full_name': self._user_name,
            'password': self._password
        }
        self._user_info = await self._post_data(Channel.LOGIN, json=login_info)
        self._token = self._user_info['token']

        self._log.info('登陆成功！')

        return self._user_info

    async def _action_send_image(self, **params) -> Union[Dict[str, Any], None]:
        if not Validate.action({'cid', 'file_path'}, params):
            return None

        async def _post_file_image(self, file_path: str,
                                   cid: str,
                                   content: str = '',
                                   at_user: Optional[str] = None) -> Dict[str, Any]:
            url_path = Channel.SEND_IMAGE.format(channelId=cid)
            file_info = FileIO.get_file_info(file_path)
            data = FormData()
            data.add_field('files', await FileIO.read_image(file_path),
                           content_type=file_info['content_type'],
                           filename=file_info['name'])
            payload_json = {'nonce': No.IDENT,
                            'content': Ms.at(at_user) + content if at_user else content}
            data.add_field('payload_json', json.dumps(payload_json))

            return await self._post_data(url_path, data=data)

        return await _post_file_image(self, **params)

    @property
    def _header(self):
        headers = {}
        if self._token:
            headers['Authorization'] = 'Bearer ' + self._token
            return headers

    async def _post_data(self, url_path: str, *,
                         data: Optional[Any] = None,
                         json: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        async with aiohttp.ClientSession() as session:
            async with session.post(self._api_root + url_path,
                                    data=data,
                                    json=json, headers=(self._header or None),
                                    timeout=self._timeout_sec) as res:
                if 200 <= res.status < 300:
                    return await res.json()
                raise HttpFailed(res.status)

    async def _action_general(self, url_path: str, **params) -> Dict[str, Any]:
        '''
        POST: General json format parameters
        '''
        # params.pop('cid')  # Extra parameters don’t matter
        params['nonce'] = No.IDENT
        return await self._post_data(url_path, json=params)

    def _post(self, url_path: str) -> Any:
        '''
        Magic method of matching mapping
        '''
        return functools.partial(self._action_general, url_path)

    async def _get_data(self, url_path: str,
                        params: Dict[str, Any] = None) -> Dict[str, Any]:
        async with aiohttp.ClientSession() as session:
            async with session.get(self._api_root + url_path,
                                   params=params,
                                   headers=(self._header or None),
                                   timeout=self._timeout_sec) as res:
                if 200 <= res.status < 300:
                    return await res.json()
                raise HttpFailed(res.status)

    def _get(self, url_path: str) -> Any:
        return functools.partial(self._get_data, url_path)
