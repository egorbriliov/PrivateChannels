import disnake
from disnake.ext import commands
from app.db_privates import CollectionActivePrivates
from app.db_privates import CollectionServers


class LockUnlockRoom(commands.Cog):
    # Конструкция (bot : commands) здесь, чтобы дать IDE представление о том, какой тип данных содержит аргумент.
    # Это не обязательно, но может быть полезно при разработке.
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.db_privates = CollectionActivePrivates()
        self.db_servers = CollectionServers()

    @commands.guild_only()
    @commands.user_command(name="Open/Close room", guild_ids=CollectionServers().servers_id)
    async def lock(self, inter: disnake.GuildCommandInteraction, user: disnake.User):
        """
        Описание:
        Позволяет открыть/закрыть канал
        """
        if user == inter.bot.user:
            await inter.send("", ephemeral=True, delete_after=10)
        else:
            # Попытка получить канал в котором находится пользовать, если всё получается - срабатывает дальнейший код
            try:

                # Получение канала в котором находится пользователь
                channel = inter.author.voice.channel

                # Проверяется, чтобы канал в котором находится пользователь был в категории приватных каналов
                guild = inter.guild
                server_last_data = self.db_servers.get_server_data(server_id=guild.id)
                category = disnake.utils.get(guild.categories, id=server_last_data.get("category_id"))
                channel_create = disnake.utils.get(category.channels, id=server_last_data.get("channel_id"))

                # Если пользователь не в категории "Приватных каналов" или канал явл. "Создать канал (+)", вызывается
                # ошибка
                if channel not in category.channels or channel == channel_create:
                    raise

                # Проверяется, чтобы пользователь был владельцем комнаты
                if inter.user.id == self.db_privates.get_owner_id(guild_id=guild.id,
                                                                  channel_id=inter.author.voice.channel.id):
                    # Получаются текущие разрешения для всех
                    permissions = channel.permissions_for(inter.guild.default_role)
                    # Если текущее разрешение позволяет подключаться
                    if permissions.connect:
                        # Администратору комнаты разрешается присоединятся
                        await channel.set_permissions(inter.user, connect=True)
                        # Боту разрешается присоединяться разрешается присоединятся
                        await channel.set_permissions(inter.bot.get_user(1256728930216575036), connect=True)
                        # Всем запрещается присоединятся
                        await channel.set_permissions(inter.guild.default_role, connect=False)
                        # Администратору комнаты отсылается ответ о том, что доступ для всех пользователей был закрыт
                        await inter.send(f"The room was closed to all users",
                                         ephemeral=True,
                                         delete_after=10)
                    # Если текущее разрешение не позволяет подключаться
                    else:
                        # Всем разрешается присоединятся
                        await channel.set_permissions(inter.guild.default_role, connect=True)
                        # Администратору комнаты отсылается ответ о том, что доступ для всех пользователей был открыт
                        await inter.send(f"The room was open to all users",
                                         ephemeral=True,
                                         delete_after=10)
                # Если пользователь не администратор комнаты
                else:
                    await inter.send(f"{inter.user.mention}, you are not the owner of the room!",
                                     ephemeral=True,
                                     delete_after=10)
            # Срабатывает ошибка, т.к. пользователь не находится в категории или находится в канале "Создать канал (+)"
            except:
                await inter.send("You are not in the \"Private Channels\" group channel!",
                                 ephemeral=True,
                                 delete_after=10)
                await inter.user.send("You are not in the \"Private Channels\" group channel!",
                                      delete_after=10)


def setup(bot: commands.Bot):
    bot.add_cog(LockUnlockRoom(bot))
