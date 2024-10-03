import disnake
from disnake.ext import commands

from app.db_privates import CollectionActivePrivates
from app.db_privates import CollectionServers


class GenerateCategory(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot
        self.db_privates: CollectionActivePrivates = CollectionActivePrivates()
        self.db_servers: CollectionServers = CollectionServers()

    @commands.Cog.listener(name="on_ready")
    async def category(self):
        """
        Clean private categories on servers when bot has been started.
        A new category and voice channel "Create a room (+)" will also be created if it does not exist.
        """
        # When bot has been started his will delete all data about private rooms of guilds
        self.db_privates.delete_all_data()
        # Enumerate the list of guilds
        for guild in self.bot.guilds:
            # Getting all data about guild from local database by guild id
            server: int = self.db_servers.get_server_data(guild.id)
            # If server has been registered
            if server:
                # Getting all data from guild by guild.id
                server_last_data: dict = self.db_servers.get_server_data(server_id=guild.id)
                # Getting category by category id from database
                category: disnake.CategoryChannel = disnake.utils.get(guild.categories,
                                                                      id=server_last_data.get("category_id"))
                # Getting channel by channel id from database
                channel_create: disnake.CategoryChannel = disnake.utils.get(category.channels,
                                                                            id=server_last_data.get("channel_id"))
                # If category on server
                if category:
                    # Iterate channels and remove unnecessary ones
                    for channel in category.channels:
                        # If the channel has a name other than "Create Channel (+)", it will be deleted
                        if channel == channel_create:
                            continue
                        # If the channel has a different name it will be deleted
                        else:
                            await channel.delete()
                # If category not on guild
                else:
                    # Creating category
                    category: disnake.CategoryChannel = await guild.create_category("Private channels")
                    # In category creating new channel with name "Create channel (+)"
                    create_channel: disnake.VoiceChannel = await category.create_voice_channel(
                        name="Create channel (+)",
                        user_limit=1
                        )
                    # Updating new data about guild
                    self.db_servers.new_server_data(server_id=guild.id,
                                                    category_id=category.id,
                                                    channel_id=create_channel.id)


def setup(bot: commands.Bot):
    bot.add_cog(GenerateCategory(bot))
