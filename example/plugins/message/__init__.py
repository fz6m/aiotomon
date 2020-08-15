
from aiotomon import get_bot

from .config import RESOURCE_BASE_PATH

bot = get_bot()

# 等价于订阅 @bot.on('message')
@bot.on_message
async def _(ctx):
    print(f'收到了来自 [{ctx.author.name}] 的消息：{ctx.content}')
    # 只在指定的频道生效
    if ctx.channel_id == '156676532616687616':
        await bot.send_text(
            cid = ctx.channel_id, 
            content = 'Hello World !')


# 等价于订阅 @bot.on('message.channel')
@bot.on_message('channel')
async def _(ctx):
    # 允许用点和字典方式取值
    if ctx['channel_id'] == '156676532616687616' and ctx['content'] == '你懂的':
        await bot.send_image(
            cid = ctx['channel_id'],
            file_path = f'{RESOURCE_BASE_PATH}/fubuki.jpg',
            at_user = ctx['author']['id']
        )
