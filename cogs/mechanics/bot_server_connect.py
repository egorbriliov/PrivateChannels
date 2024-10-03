import disnake
from disnake.ext import commands


class SeverConnect(commands.Cog):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener(name="on_guild_join")
    async def category(self, guild: disnake.Guild) -> None:
        """
        Method thanks the administrator when connect to new server
        """
        guild_owner: guild.owner = guild.owner

        embed: disnake.Embed = disnake.Embed(
            title="Thank you for choosing to use me!",
            description="\nTo take advantage of my functionality, you should use /activate"
                        "\nto activate the category in which I will work."
        )

        await guild_owner.send(embed=embed, delete_after=60)


def setup(bot: commands.Bot):
    bot.add_cog(SeverConnect(bot))
