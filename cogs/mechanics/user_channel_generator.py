import disnake
from disnake.ext import commands

from app.db_privates import CollectionActivePrivates
from app.db_privates import CollectionServers


class UserChannelGenerator(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot
        self.db_privates: CollectionActivePrivates = CollectionActivePrivates()
        self.db_servers: CollectionServers = CollectionServers()

    @commands.Cog.listener(name="on_voice_state_update")
    async def on_connect_creating_room(self, member: disnake.Member, before, after):
        """
        When a user is connected to "Create Channel":
        1. A new voice channel will be created for them
        2. They will be moved to that channel
        3. They will receive a notification that the channel has been created
        """
        # When user connect or reconnect to voice channel
        if (((after.channel is not None and before.channel is None) or
                (after.channel is not None and before.channel is not None)) and
                (after.channel.guild.id in self.db_servers.servers_id)):
            # Getting channel, that user has been connected
            connected_channel: disnake.VoiceChannel = after.channel
            # Getting "channel create"
            guild: disnake.Guild = after.channel.guild
            server_last_data = self.db_servers.get_server_data(server_id=guild.id)
            private_category: disnake.CategoryChannel = disnake.utils.get(
                guild.categories, id=server_last_data.get("category_id")
            )
            channel_creator: disnake.VoiceChannel = disnake.utils.get(
                private_category.channels, id=server_last_data.get("channel_id")
            )
            # If "create channel" is "connected channel"
            if channel_creator is connected_channel:
                # Creating new channel for user
                member_channel: disnake.VoiceChannel = await private_category.create_voice_channel(name=member.name)
                # Moving a user to his new channel
                await member.move_to(member_channel)
                # Adding channel with his owner into database
                self.db_privates.new_channel(guild_id=guild.id, channel_id=member_channel.id, owner_id=member.id)
                # Notification user that channel was created
                await member_channel.send(f"{member.mention} you have created a new private channel!",
                                          delete_after=30)


def setup(bot: commands.Bot):
    bot.add_cog(UserChannelGenerator(bot))
