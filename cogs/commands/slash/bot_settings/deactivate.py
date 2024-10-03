import disnake
from disnake.ext import commands

from app.db_privates import CollectionActivePrivates
from app.db_privates import CollectionServers
import app


class DeactivateServer(commands.Cog):
    # Конструкция (bot : commands) здесь, чтобы дать IDE представление о том, какой тип данных содержит аргумент.
    # Это не обязательно, но может быть полезно при разработке.

    def __init__(self, bot: commands.InteractionBot) -> None:
        """
        Метод инициализирует, бота, чтобы был доступ к боту
        """
        self.bot = bot
        self.db_privates = CollectionActivePrivates()
        # self.bags = DbBags()
        self.db_servers = CollectionServers()
        print(f"Новый список для работы deactivate: {CollectionServers().servers_id}")

    """
    Команды
    """
    print(CollectionServers().servers_id)

    @commands.guild_only()
    @commands.slash_command(name="deactivate",
                            description="Activate/Deactivate bot",
                            guild_ids=CollectionServers().servers_id)
    async def deactivate(self, inter: disnake.GuildCommandInteraction):
        """
        Срабатывает на: использование.
        -----------------------------
        Отвечает за: деактивация бота на сервере
        """
        if inter.user.id == inter.guild.owner.id:
            # Проверяется, чтобы сервер не был зарегистрирован
            server = self.db_servers.get_server_data(inter.guild.id)
            # Если сервер зарегистрирован
            if server:
                # Получается категория
                server_data = self.db_servers.get_server_data(inter.guild.id)
                category = disnake.utils.get(inter.guild.categories, id=server_data.get("category_id"))
                # Из категории удаляются все каналы
                for channel in category.channels:
                    await channel.delete()
                # Удаляется сама категория
                await category.delete()
                # Сервер удаляется из БД
                self.db_servers.delete_server(inter.guild.id)
                # Отсылается ответ об успешном удалении
                await inter.send("Thank you for using me, if you ever need me again, use me"
                                 "/activate ",
                                 ephemeral=True,
                                 delete_after=10)



            # Если сервер ещё не зарегистрирован
            else:
                # Отсылается ответ об ошибке
                await inter.send("Your server is not registered yet!", ephemeral=True, delete_after=10)
        else:
            await inter.send(f"Unfortunately, you are not the founder of the server, to interact on this server",
                             ephemeral=True,
                             delete_after=10)
        #
        # for cog in app.tree.cogs_list():
        #     self.bot.reload_extension(cog)
        self.bot.reload_extension("cogs.commands.user.channel.lock_unlock")
        self.bot.reload_extension("cogs.commands.slash.bot_settings.deactivate")


def setup(bot: commands.InteractionBot):
    bot.add_cog(DeactivateServer(bot))
