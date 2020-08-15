
from aiotomon import get_bot

bot = get_bot()


@bot.on('notice.online')
async def _(ctx):
    print(f'注意：[{ctx.user.name}] 上线了！')