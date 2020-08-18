
import logging
import asyncio
from typing import Any, Dict, Optional, Callable, Awaitable, Union

from .api import AsyncApi
from .api_impl import HttpApi
from .event import Event, EventQueue, run_async_funcs
from .config import Op, E, O
from .plugin import Plugins
from .message import identify, to_message
from .exceptions import ResponseError, NetworkError, OperationError

import websockets as ws
from websockets import ConnectionClosed

try:
    import ujson as json
except ImportError:
    import json


class AioTomon(AsyncApi):

    SERVER_URI = 'wss://gateway.tomon.co'

    API_ROOT = 'https://beta.tomon.co/api/v1'

    def __init__(self, user_name: str = '',
                 password: str = '',
                 timeout_sec: int = 10,
                 plugins_dir: str = 'plugins',
                 token: Optional[str] = None):

        self._ws = None
        self._api = None
        self._bot_info = None
        self._bot_start_before = set()
        self._ws_start_before = set()
        self._send_before = set()

        self._queue = EventQueue()
        self._plugin = Plugins(plugins_dir)

        self._configure(
            api_root=self.API_ROOT,
            user_name=user_name,
            password=password,
            timeout_sec=timeout_sec,
            token=token
        )

    def _configure(self, api_root: str,
                   user_name: str,
                   password: str,
                   timeout_sec: Optional[int],
                   token: Optional[str]) -> None:
        self._api = HttpApi(api_root, user_name, password,
                            timeout_sec=timeout_sec, token=token)

    @property
    def log(self) -> logging.Logger:
        return self._api._log

    async def _get_token(self) -> None:
        await self.login()

    async def _single_recv(self, verif_code: int) -> Dict[str, Any]:
        resp = json.loads(await self._ws.recv())
        if resp['op'] != verif_code:
            raise ResponseError
        return resp

    async def _verif(self) -> None:
        auth = {'op': Op.IDENTIFY, 'd': {'token': self._api._token}}
        await self._ws.send(json.dumps(auth))
        resp = await self._single_recv(Op.IDENTIFY)
        self._bot_info = resp['d']

    async def _success(self) -> None:
        if not self._api._user_info:
            self._api._user_info = await self.get_user_info()
        user_info = self._api._user_info
        user_info = user_info['username'] + '#' + user_info['discriminator'] + '(' + \
            user_info['id'] + ')'
        self.log.info(f'当前用户：{user_info}')

    async def _initial(self) -> None:
        self.log.info('尝试与服务器通信...')
        await self._single_recv(Op.HELLO)
        self.log.info('已与服务器建立连接')

        if not self._api._token:
            self.log.info('正在请求 Token 令牌...')
            await self._get_token()
        else:
            self.log.info('已配置 Token 将直接尝试验证身份')

        self.log.info('开始验证身份...')
        await self._verif()
        self.log.info('身份验证成功！')
        await self._success()

    async def _on_load_plugins(self) -> None:
        '''
        Life cycle 2: loading plugins
        '''
        plugins = self._plugin.plugins_info
        for plugin in plugins:
            self.log.info(f'Life cycle [ on_load_plugin ]: {plugin} Loaded')

    async def _connect(self) -> None:

        await self._start()

        await self._on_load_plugins()

        self.log.info('正在开启 ws 连接...')

        while True:
            try:
                await self._ws_connect()
            except ConnectionResetError as e:
                self.log.error(e)
                self.log.warning('连接远程服务器失败，3 秒后尝试重连...')
                await asyncio.sleep(3)


    async def _ping(self) -> None:
        while True:
            try:
                self._ws.send(json.dumps({ 'op': Op.HEARTBEAT }))
                await asyncio.sleep(10)
            except:
                break


    async def _ws_connect(self) -> None:
        async with ws.connect(self.SERVER_URI) as websocket:
            while True:
                try:

                    self._ws = websocket
                    try:
                        await asyncio.wait_for(self._initial(), self._api._timeout_sec)
                    except asyncio.TimeoutError:
                        self.log.error('连接超时，初始化失败！')
                        self.log.warning(' 3 秒后尝试重新初始化')
                        await asyncio.sleep(3)
                        break

                    await self._ws_startup()

                    asyncio.create_task(self._ping())

                    await self._handle_ws_event()

                except ConnectionClosed as e:
                    self.log.error(f'远程 ws 断开（错误码  {e.code} ）')
                    self.log.warning(' 3 秒后尝试重连远程 ws ')
                    await asyncio.sleep(3)
                    break


    async def call_action(self, action: str, **params) -> Any:
        await run_async_funcs(self._send_before, **params)
        return await self._api.call_action(action=action, **params)

    def run(self) -> None:
        asyncio.get_event_loop().run_until_complete(self._connect())

    async def _handle_ws_event(self) -> None:
        while True:
            try:
                payload = json.loads(await self._ws.recv())
            except ValueError:
                payload = None

            if not isinstance(payload, dict):
                continue

            asyncio.create_task(self._handle_ws_event_response(payload))

    async def _handle_ws_event_response(self, payload: Dict[str, Any]) -> None:
        resp = Event.from_payload(payload)
        if not resp:
            return
        o, e = O.get(resp.op), E.get(resp.e)
        self.log.info(f'[ {o} ]：{e}')

        # TODO: More friendly information packaging
        ctx = to_message(resp.d)

        event_name = identify(ctx)

        if not event_name:
            return

        # TODO: Further processing of results
        results = list(filter(lambda r: r is not None,
                              await self._queue.emit(event_name, ctx)))

    def subscribe(self, event_name: str, func: Callable) -> None:
        self._queue.subscribe(event_name, self._ensure_async(func))

    def unsubscribe(self, event_name: str, func: Callable) -> None:
        self._queue.unsubscribe(event_name, func)

    def _ensure_async(self, func: Callable[..., Any]) -> Callable[..., Awaitable[Any]]:
        if asyncio.iscoroutinefunction(func):
            return func
        raise OperationError

    def on(self, *event_names: str) -> Callable:
        def deco(func: Callable) -> Callable:
            for name in event_names:
                self.subscribe(name, func)
            return func
        return deco

    def _deco_maker(deco_method: Callable, type_: str) -> Callable:
        def deco_deco(self, arg: Optional[Union[str, Callable]] = None,
                      *sub_event_names: str) -> Callable:
            def deco(func: Callable) -> Callable:
                if isinstance(arg, str):
                    e = [type_ + '.' + e for e in [arg] +
                         list(sub_event_names)]
                    deco_method(self, *e)(func)
                else:
                    deco_method(self, type_)(func)
                return func

            if callable(arg):
                return deco(arg)
            return deco

        return deco_deco

    on_message = _deco_maker(on, 'message')

    def hook_before(self, event_name: str, func: Callable) -> None:
        self._queue.hook_before(event_name, self._ensure_async(func))

    def unhook_before(self, event_name: str, func: Callable) -> None:
        self._queue.unhook_before(event_name, func)

    def before(self, *event_names: str) -> Callable:
        '''
        Life cycle 4: Before processing the message
        '''
        def deco(func: Callable) -> Callable:
            for name in event_names:
                self.hook_before(name, func)
            return func

        return deco

    before_message = _deco_maker(before, 'message')

    def on_startup(self, func: Callable) -> Callable:
        '''
        Life cycle 1: Before the bot starts
        '''
        self._bot_start_before.add(self._ensure_async(func))
        return func

    async def _start(self) -> None:
        if self._bot_start_before:
            self.log.info('Life cycle [ on_start ]: Begin execution')
            await run_async_funcs(self._bot_start_before)
            self.log.info('Life cycle [ on_start ]: Finished')

    def on_ws_startup(self, func: Callable) -> Callable:
        '''
        Life cycle 3: After the account is successfully logged in, 
                      before monitoring the ws report
        '''
        self._ws_start_before.add(self._ensure_async(func))
        return func

    async def _ws_startup(self) -> None:
        if self._ws_start_before:
            self.log.info('Life cycle [ on_ws_startup ]: Begin execution')
            await run_async_funcs(self._ws_start_before)
            self.log.info('Life cycle [ on_ws_startup ]: Finished')

    def on_send_before(self, func: Callable) -> None:
        '''
        Life cycle 5: before calling active api
        '''
        self._send_before.add(self._ensure_async(func))
        return func

    @property
    def plugin(self) -> Plugins:
        return self._plugin

    # TODO: Three ugly functions

    def auto_load_plugin(self) -> None:
        self._plugin.auto_load_plugins()

    def load_plugin(self, module_name: str) -> None:
        self._plugin.load_plugins(module_name)

    def not_load_plugin(self, module_name: str) -> None:
        self._plugin.not_load_plugins(module_name)
