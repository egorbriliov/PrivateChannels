import disnake
from disnake.ext import commands

from app.db_privates import CollectionActivePrivates
from app.db_privates import CollectionServers


class KickUser(commands.Cog):
    # Конструкция (bot : commands) здесь, чтобы дать IDE представление о том, какой тип данных содержит аргумент.
    # Это не обязательно, но может быть полезно при разработке.
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.db_privates = CollectionActivePrivates()
        self.db_servers = CollectionServers()

    @commands.user_command(name="Kick out", guild_ids=CollectionServers().servers_id)
    @commands.guild_only()
    async def lock(self, inter: disnake.GuildCommandInteraction, user: disnake.User):
        """
        Описание:
        Позволяет выгнать пользователя из канала
        Должны выполниться условия:
        1. Использовавший должен находиться в [категории бота]
        2. Пользователь не должен находиться в голосовом канале [Создать канал (+)]
        3. Пользователь должен быть администратором комнаты
        4. Пользователь должен быть в канале, в котором применяется команда
        """
        if user == inter.bot.user:
            await inter.send("You cannot use this command on a bot!", ephemeral=True, delete_after=10)
        else:
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
                # Проверка, чтобы выбранный пользователь находился в созданном администратором приватном канале
                if user in channel.members:
                    # Проверяется, чтобы пользователь был владельцем комнаты
                    if inter.user.id == self.db_privates.get_owner_id(guild_id=guild.id,
                                                                      channel_id=inter.author.voice.channel.id):
                        # Пользователь выгоняется из комнаты
                        member = inter.guild.get_member(user.id)
                        await member.move_to(None)
                        await inter.send(f"User {member.mention} has been kicked out of the room!",
                                         ephemeral=True,
                                         delete_after=10)

                        await user.send(f"You were kicked out of the room {channel.mention}",
                                        delete_after=10)

                    # Если пользователь не основатель комнаты
                    else:
                        await inter.user.send(f"You are not the owner of the room!",
                                              delete_after=10)
                # Если выбранный пользователь не находился в созданном администратором приватном канале
                else:
                    # Администратору выводиться сообщение об ошибке
                    await inter.response.send_message(f"{user.mention} is not in the private area you created "
                                                      f"room!",
                                                      delete_after=10,
                                                      ephermal=True)
            # Срабатывает ошибка, т.к. пользователь не находится в категории или находится в канале "Создать канал (+)"
            except:
                await inter.user.send("You are not in the \"Private Channels\" group channel!",
                                      delete_after=10)


def setup(bot: commands.Bot):
    bot.add_cog(KickUser(bot))
