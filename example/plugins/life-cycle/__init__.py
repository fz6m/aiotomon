
from aiotomon import get_bot

bot = get_bot()


@bot.on_startup
async def _():
    bot.log.info('----- bot.on_startup -----')
    print('启动 bot 前的钩子触发了')


@bot.on_ws_startup
async def _():
    bot.log.info('----- bot.on_ws_startup -----')
    print('正式开始 ws 通信前的钩子触发了')


@bot.before
async def _(ctx):
    bot.log.info('----- bot.before -----')
    print(f'在处理 [{ctx.author.name}] 消息前的钩子触发了')


@bot.on_send_before
async def _(**params):
    bot.log.info('----- bot.on_send_before -----')
    print('调用主动 api 之前的钩子被触发了')
    print(f'调用 api 参数：{params}')