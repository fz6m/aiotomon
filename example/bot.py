
import aiotomon

import config


def main():

    aiotomon.init(config)

    bot = aiotomon.get_bot()

    bot.auto_load_plugin()

    bot.run()


if __name__ == "__main__":
    main()