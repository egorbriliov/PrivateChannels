import disnake
from disnake.ext import commands

from app.db_privates import CollectionActivePrivates
from app.db_privates import CollectionServers


class ChangingCreateChannelName(commands.Cog):
    # Конструкция (bot : commands) здесь, чтобы дать IDE представление о том, какой тип данных содержит аргумент.
    # Это не обязательно, но может быть полезно при разработке.

    def __init__(self, bot: commands.Bot) -> None:
        """
        Метод инициализирует, бота, чтобы был доступ к боту
        """
        self.bot = bot
        self.db_privates = CollectionActivePrivates()
        self.db_servers = CollectionServers()

    """
    Команды
    """

    @commands.slash_command(name="change", description="Activate bot")
    async def change(self, inter: disnake.GuildCommandInteraction):
        """
        Срабатывает на: использование.
        -----------------------------
        Отвечает за: активацию бота на сервере
        """
        pass

    @change.sub_command_group(name="name")
    async def name(self, inter: disnake.ApplicationCommandInteraction):
        pass

    @commands.guild_only()
    @name.sub_command(name="category", description="Changes the name of the category managed by the bot")
    async def category(self, inter: disnake.ApplicationCommandInteraction, new_name: str):
        if inter.user.id == inter.guild.owner.id:
            server_data = self.db_servers.get_server_data(inter.guild.id)
            category = disnake.utils.get(inter.guild.categories, id=server_data.get("category_id"))
            await category.edit(name=new_name)
            await inter.send(f"A new name has been set for the category {new_name}", ephemeral=True,
                             delete_after=10)
        else:
            await inter.send(f"Unfortunately, you are not the founder of the server, to interact on this server",
                             ephemeral=True,
                             delete_after=10)

    @commands.guild_only()
    @name.sub_command(name="room", description="Changes the name of the room controlled by the bot")
    async def room(self, inter: disnake.ApplicationCommandInteraction, new_name: str):
        if inter.user.id == inter.guild.owner.id:
            server_data = self.db_servers.get_server_data(inter.guild.id)
            channel = disnake.utils.get(inter.guild.channels, id=server_data.get("channel_id"))
            await channel.edit(name=new_name)
            await inter.send(f"A new name has been set for the room {new_name}", ephemeral=True,
                             delete_after=10)
        else:
            await inter.send(f"Unfortunately, you are not the founder of the server, to interact on this server",
                             ephemeral=True,
                             delete_after=10)


def setup(bot: commands.Bot):
    bot.add_cog(ChangingCreateChannelName(bot))
