import disnake
from disnake.ext import commands

import app.tree
from app.env_get import get_env

intents: disnake.Intents = disnake.Intents.all()

activity: disnake.Activity = disnake.Activity(
    type=disnake.ActivityType.competing,
    state="in the number of minutes of loneliness")

bot: commands.InteractionBot = commands.InteractionBot(
    intents=intents,
    reload=True,
    activity=activity,
    status=disnake.Status.idle,
 )

@bot.event
async def on_ready():
    print(f'\033[3;32mBot \033[0m\033[35;1m{bot.user.name}\033[0m\033[3;32m is connected and ready to work!\033[0m')


COGS_LIST = app.tree.cogs_list()

for cog in COGS_LIST:
    bot.load_extension(cog)

bot.run(get_env(name="TOKEN"))

stroke = "zxc"

