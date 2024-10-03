import disnake
from disnake.ext import commands

from app.db_privates import CollectionActivePrivates
from app.db_privates import CollectionServers


class UserChannelLeave(commands.Cog):
    """
    Класс отвечает за:
    1) Передача владения каналом при выходе администратора канала
    2) Удаление канала при выходе всех пользователей
    """

    def __init__(self, bot: commands.Bot) -> None:
        # Initializing bot
        self.bot: commands.Bot = bot
        # Initializing database
        self.db_privates: CollectionActivePrivates = CollectionActivePrivates()
        self.db_servers: CollectionServers = CollectionServers()

    @commands.Cog.listener(name="on_voice_state_update")
    async def on_connect_creating_room(self, member: disnake.Member, before, after):
        """
        When the owner of a closed channel leaves the channel:
        1) If there are still users in the room, the next user gets access
        2) If there are no users in the room, the room is deleted
        """
        # If user leave to channel or connect to another on registered server
        if (((before.channel is not None and after.channel is None) or
             (before.channel is not None and after.channel is not None)) and
                (before.channel.guild.id in self.db_servers.servers_id)):
            guild: disnake.Guild = before.channel.guild
            server_last_data = self.db_servers.get_server_data(server_id=guild.id)
            private_category: disnake.CategoryChannel = disnake.utils.get(
                guild.categories, id=server_last_data.get("category_id")
            )
            channel_creator: disnake.VoiceChannel = disnake.utils.get(
                private_category.channels, id=server_last_data.get("channel_id")
            )
            # If voice channel that user connected to is in category channels and is not "create channel"
            if before.channel in private_category.channels and before.channel != channel_creator:
                # If there are no more users in the room
                if len(before.channel.members) == 0:
                    # The channel is being deleted
                    await before.channel.delete()
                    # The channel data is being removed from database
                    self.db_privates.delete_channel(guild_id=guild.id, channel_id=before.channel.id)
                # If there are users in the room
                else:
                    # If member that has been leaved from room is room owner
                    if member.id == self.db_privates.get_owner_id(guild_id=guild.id, channel_id=before.channel.id):
                        # Getting first member from channel
                        new_member: disnake.Member = before.channel.members[0]
                        # Notification new room owner
                        await before.channel.send(f"Administrator rights from {member.mention} to {new_member.mention} "
                                                  f"have been transferred", delete_after=15)
                        # Register new user in database
                        self.db_privates.new_data_channel(guild_id=before.channel.guild.id,
                                                          channel_id=before.channel.id,
                                                          owner_id=new_member.id)


def setup(bot: commands.Bot):
    bot.add_cog(UserChannelLeave(bot))
