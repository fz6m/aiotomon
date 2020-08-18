<div align="center">
<img src = 'https://cdn.jsdelivr.net/gh/fz6m/Private-picgo@moe/img/20200815235527.png' width = '150px' />


# aiotomon

![Python](https://img.shields.io/badge/python-3.7%20%2B-informational)
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
![Version](https://img.shields.io/badge/version-1.3-orange)
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
![License](https://img.shields.io/github/license/fz6m/aiotomon)

</div>

## Install

```bash
    pip install git+https://github.com/fz6m/aiotomon.git@master
```

## Upgrade

```bash
    pip install --upgrade git+https://github.com/fz6m/aiotomon.git@master
```

## Plugin example

```python
    from aiotomon import get_bot

    bot = get_bot()

    @bot.on_message
    async def _(ctx):
        print(f'收到了来自 [{ctx.author.name}] 的消息：{ctx.content}')
        if ctx.channel_id == '156676532616687616':
            await bot.send_text(
                cid = ctx.channel_id, 
                content = 'Hello World !')
```

[完整 example](https://github.com/fz6m/aiotomon/tree/master/example)
