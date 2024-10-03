import disnake
from disnake.ext import commands

import app.tree
from app.db_privates import CollectionActivePrivates
from app.db_privates import CollectionServers


class ActivateServer(commands.Cog):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.db_privates = CollectionActivePrivates()
        # self.bags = DbBags()
        self.db_servers = CollectionServers()
        print(f"Новый список для работы activate: {CollectionServers().servers_id}")

    async def check_bot_permissions(self, guild: disnake.Guild) -> list:
        """
        Проверяет разрешения бота на сервере и возвращает список недостающих разрешений.
        """
        missing_permissions = []
        bot_member = guild.get_member(self.bot.user.id)
        if not bot_member.guild_permissions.view_channel:
            missing_permissions.append("view_channel")
        if not bot_member.guild_permissions.manage_channels:
            missing_permissions.append("manage_channels")
        if not bot_member.guild_permissions.manage_roles:
            missing_permissions.append("manage_roles")
        if not bot_member.guild_permissions.kick_members:
            missing_permissions.append("kick_members")
        if not bot_member.guild_permissions.send_messages:
            missing_permissions.append("send_messages")
        if not bot_member.guild_permissions.send_messages_in_threads:
            missing_permissions.append("send_messages_in_threads")
        if not bot_member.guild_permissions.create_public_threads:
            missing_permissions.append("create_public_threads")
        if not bot_member.guild_permissions.manage_messages:
            missing_permissions.append("manage_messages")
        if not bot_member.guild_permissions.manage_threads:
            missing_permissions.append("manage_threads")
        if not bot_member.guild_permissions.read_message_history:
            missing_permissions.append("read_message_history")
        if not bot_member.guild_permissions.mute_members:
            missing_permissions.append("mute_members")
        if not bot_member.guild_permissions.deafen_members:
            missing_permissions.append("deafen_members")
        if not bot_member.guild_permissions.move_members:
            missing_permissions.append("move_members")

        return missing_permissions

    @commands.slash_command(name="activate",
                            description="Activate bot")
    async def activate_deactivate(self, inter: disnake.GuildCommandInteraction):
        """
        Срабатывает на: использование.
        -----------------------------
        Отвечает за: активацию бота на сервере
        """

        if inter.user.id == inter.guild.owner.id:
            # Получается список недостающих разрешений для правильной работы бота
            missing_permissions = await self.check_bot_permissions(inter.guild)
            # Если есть не достающие права
            if missing_permissions:
                # Выводиться ответ с недостающими правами для бота
                text = ""
                for index, permission in enumerate(missing_permissions):
                    text += "\n" + str(index) + ". " + permission
                await inter.send(f"**For the bot to work correctly, it must be given the necessary rights**\n"
                                 f"*The bot does not have enough rights: ({len(missing_permissions)})*" + text,
                                 ephemeral=True,
                                 delete_after=10)
            # Если всех прав хватает
            else:
                # Проверяется, чтобы сервер не был зарегистрирован
                server = self.db_servers.get_server_data(inter.guild.id)
                if not server:
                    # Создаётся категория
                    category = await inter.guild.create_category("Private channels")
                    # В категории создаётся канал
                    create_channel = await category.create_voice_channel(name="Create a channel (+)",
                                                                         user_limit=1
                                                                         )
                    # В БД добавляется новый сервер
                    self.db_servers.add_new_server(server_id=inter.guild.id,
                                                   category_id=category.id,
                                                   channel_id=create_channel.id)
                    # Использовавшему отсылается ответ
                    await inter.send("The bot was successfully registered for this server!\n"
                                     "*If you haven't already hidden the /activate and /deactivate commands "
                                     "from everyone except,"
                                     "you then this could be your next step*",
                                     ephemeral=True,
                                     delete_after=10)
                    print("zxczxc")
                    for cog in app.tree.cogs_list():
                        print("Reloaded: ", cog)
                        self.bot.reload_extension(cog)

                # Если сервер зарегистрирован
                else:
                    # Отсылается ошибка при регистрации, потому что бот уже на сервере
                    await inter.send("The bot is already registered for this server!", ephemeral=True,
                                     delete_after=10)
        else:
            await inter.send(f'Unfortunately, you are not the founder of the server, to interact on '
                             f'this server',
                             ephemeral=True,
                             delete_after=10)


def setup(bot: commands.Bot):
    """
    Авторизует бота в когах
    """
    bot.add_cog(ActivateServer(bot))
