import disnake
from disnake.ext import commands
from app.db_privates import CollectionActivePrivates
from app.db_privates import CollectionServers


class LockUnclockUser(commands.Cog):
    # Конструкция (bot : commands) здесь, чтобы дать IDE представление о том, какой тип данных содержит аргумент.
    # Это не обязательно, но может быть полезно при разработке.
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.db_privates = CollectionActivePrivates()
        self.db_servers = CollectionServers()

    @commands.user_command(name="Give/Take access", guild_ids=CollectionServers().servers_id)
    async def lock_unlock_user(self, inter: disnake.GuildCommandInteraction, user: disnake.User):
        """
        Описание:
        Позволяет дать/забрать доступ для пользователя в канале
        """
        # Проверяем, что команда вызвана на сервере
        if inter.guild is None:
            await inter.send("Sorry, but this command is only available on servers.", ephemeral=True, delete_after=10)
            return
        else:
            if user == inter.bot.user:
                await inter.send("You cannot use this command on a bot!", ephemeral=True, delete_after=10)
            else:
                # Попытка получить канал в котором находится пользовать, если всё получается - срабатывает дальнейший
                # код
                try:
                    # Получение канала в котором находится пользователь
                    channel = inter.author.voice.channel
                    # Проверяется, чтобы канал в котором находится пользователь был в категории приватных каналов
                    guild = inter.guild
                    server_last_data = self.db_servers.get_server_data(server_id=guild.id)
                    category = disnake.utils.get(guild.categories, id=server_last_data.get("category_id"))
                    channel_create = disnake.utils.get(category.channels, id=server_last_data.get("channel_id"))
                    # Если пользователь не в категории "Приватных каналов" или канал явл. "Создать канал (+)",
                    # вызывается ошибка
                    if channel not in category.channels or channel == channel_create:
                        raise
                    # Проверяется, чтобы пользователь был владельцем комнаты
                    if inter.user.id == self.db_privates.get_owner_id(guild_id=guild.id,
                                                                      channel_id=inter.author.voice.channel.id):
                        # Получаются текущие разрешения для пользователя
                        permissions = channel.permissions_for(user)
                        # Если текущее разрешение позволяет подключаться к каналу
                        if permissions.connect:

                            # Пользователь выгоняется из комнаты
                            member = inter.guild.get_member(user.id)
                            # Пользователю запрещается присоединятся
                            await channel.set_permissions(user, connect=False)
                            await member.move_to(None)
                            # Пользователю отсылается ответ, о том что он был выгнан
                            await member.send(f"You were kicked out and banned from being in the channel "
                                              f"{channel.mention}",
                                              delete_after=10)
                            # Администратору комнаты отсылается ответ о том, что доступ был закрыт и пользователь был
                            # выгнан
                            await inter.send(
                                f"The room for user {user.mention} was closed and he was kicked out",
                                delete_after=10,
                                ephemeral=True)

                        # Если текущее разрешение не позволяет подключиться к голосовому каналу
                        else:
                            # Пользователю разрешается подключаться
                            await channel.set_permissions(user, connect=True)
                            # Пользователю отсылается ответ, о том что он был допущен в комнату
                            member = inter.guild.get_member(user.id)
                            await member.send(f"You are allowed to talk and be in the channel {channel.mention}",
                                              delete_after=10)
                            # Администратору комнаты отсылается ответ о том, что пользователь был допущен в комнату
                            await inter.send(f"A room for user {user.mention} has been opened",
                                             delete_after=10,
                                             ephemeral=True)
                    # Если пользователь не является владельцем комнаты
                    else:
                        await inter.send(f"You are not the owner of the room!",
                                         delete_after=10,
                                         ephemeral=True)
                # Срабатывает ошибка, т.к. пользователь не находится в категории или находится в канале "Создать
                # канал (+)"
                except:
                    await inter.send("You are not in the \"Private Channels\" group channel!",
                                     delete_after=10,
                                     ephemeral=True)
                    await inter.user.send("You are not in the \"Private Channels\" group channel!",
                                          delete_after=10)


def setup(bot: commands.Bot):
    bot.add_cog(LockUnclockUser(bot))
