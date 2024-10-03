import disnake
from disnake.ext import commands

from app.db_privates import CollectionActivePrivates
from app.db_privates import CollectionServers


class MuteUnmuteUser(commands.Cog):
    # Конструкция (bot : commands) здесь, чтобы дать IDE представление о том, какой тип данных содержит аргумент.
    # Это не обязательно, но может быть полезно при разработке.
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.db_privates = CollectionActivePrivates()
        self.db_servers = CollectionServers()

    @commands.user_command(name="Allow/Disable speaking", guild_ids=CollectionServers().servers_id)
    async def lock(self, inter: disnake.GuildCommandInteraction, user: disnake.User):
        """
        Описание:
        Позволяет дать/забрать возможность говорить для пользователя в канале
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
                    # Проверка, чтобы выбранный пользователь находился в созданном администратором приватном канале
                    if user in channel.members:
                        # Проверяется, чтобы пользователь был владельцем комнаты
                        if inter.user.id == self.db_privates.get_owner_id(guild_id=guild.id,
                                                                          channel_id=inter.author.voice.channel.id):
                            # Получаются текущие разрешения для пользователя
                            permissions = channel.permissions_for(user)
                            # Если текущее разрешение позволяет говорить
                            if permissions.speak:
                                # Пользователю запрещается говорить
                                await channel.set_permissions(user, speak=False, connect=True)
                                # Пользователь перезапускается в канал, чтобы наложился мут
                                member = inter.guild.get_member(user.id)
                                await member.move_to(channel)
                                # Пользователю отсылается ответ, о том что он был замучен
                                await member.send(f"You are banned from talking in the channel {channel.mention}",
                                                  delete_after=10)
                                # Администратору комнаты отсылается ответ о том, что пользователь был замучен
                                await inter.send(f"You have banned the user {user.mention} говорить",
                                                 delete_after=10,
                                                 ephemeral=True)
                            # Если текущее разрешение не позволяет разговаривать
                            else:
                                # Пользователю разрешается говорить
                                await channel.set_permissions(user, speak=True, connect=True)
                                # Пользователь перезапускается в канал, чтобы снятся мут
                                member = inter.guild.get_member(user.id)
                                await member.move_to(channel)
                                # Пользователю отсылается ответ, о том что он был размучен
                                await member.send(f"You are allowed to talk in the channel {channel.mention}",
                                                  delete_after=10)
                                # Администратору комнаты отсылается ответ о том, что пользователь был размучен
                                await inter.send(f"You have allowed the user {user.mention} speak",
                                                 delete_after=10,
                                                 ephemeral=True)
                        # Если пользователь не является владельцем комнаты
                        else:
                            await inter.send(f"You are not the owner of the room!",
                                             delete_after=10,
                                             ephemeral=True)
                    # Если выбранный пользователь не находился в созданном администратором приватном канале
                    else:
                        # Администратору выводиться сообщение об ошибке
                        await inter.send(f"{user.mention} is not in the private room you created!",
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
    bot.add_cog(MuteUnmuteUser(bot))
