import disnake
from disnake import MessageInteraction
from disnake.ext import commands

from app.db_privates import CollectionActivePrivates, CollectionServers


class NewRoomName(disnake.ui.Modal):
    """
    Отвечает за:
    1) Создание модульного окна для получения нового названия для пользователя
    2) Установку нового названия для комнаты
    """

    def __init__(self, inter):
        components = [
            disnake.ui.TextInput(label="New room name",
                                 placeholder="Enter the name of the new room",
                                 custom_id="NewName")
        ]
        super().__init__(title='New room name', components=components, custom_id='NewRoomName')
        self.inter = inter
        self.guild = inter.guild
        self.member = self.guild.get_member(inter.user.id)
        self.db_privates = CollectionActivePrivates()
        self.channel = self.member.voice.channel

    async def callback(self, interaction: disnake.ModalInteraction):
        # Устанавливает новое название для канала пользователя
        await self.channel.edit(name=interaction.text_values['NewName'])
        # Отправляется ответ на взаимодействие модульного окна
        await interaction.response.defer()
        await interaction.delete_original_message()
        await self.inter.send("The room name has been successfully changed!",  # Использовал Inter из предыдущего
                              # потому что
                              ephemeral=True,  # в ModalInteraction, не работает ephemeral
                              )


class UserValue(disnake.ui.Select):
    def __init__(self, inter, inter_to_delete):
        self.inter_to_delete = inter_to_delete
        self.inter = inter
        self.guild = inter.guild
        self.bot = inter.bot
        options = [
            disnake.SelectOption(label="1", value="1"),
            disnake.SelectOption(label="2", value="2"),
            disnake.SelectOption(label="3", value="3"),
            disnake.SelectOption(label="5", value="5"),
            disnake.SelectOption(label="10", value="10"),
            disnake.SelectOption(label="unlimited", value="0")]
        super().__init__(placeholder="Select value", options=options, custom_id="UserValue",
                         min_values=1, max_values=1)

    async def callback(self, interaction: MessageInteraction):

        value = int(interaction.values[0])
        guild = self.guild
        member = guild.get_member(interaction.user.id)
        channel = member.voice.channel
        try:
            await channel.edit(user_limit=value)
        except Exception as E:
            print("Exception:\n", E)
        await self.inter_to_delete.delete_original_message()
        await interaction.send("The number of allowed users per room has been changed!",
                               delete_after=10,
                               ephemeral=True)


class NewAdministrator(disnake.ui.Select):
    def __init__(self, inter, inter_to_delete):
        self.inter_to_delete = inter_to_delete
        self.bot = inter.bot
        self.guild = inter.guild
        self.member = self.guild.get_member(inter.user.id)
        self.db_privates = CollectionActivePrivates()
        self.channel = self.member.voice.channel
        options = [disnake.SelectOption(label=member.name, value=member.id)
                   for member in self.channel.members
                   if member != self.member]

        super().__init__(placeholder="Select value", options=options, custom_id="UserValue",
                         min_values=1, max_values=1)

    async def callback(self, interaction: MessageInteraction):
        self.db_privates.new_data_channel(guild_id=self.guild.id,
                                          channel_id=self.channel.id,
                                          owner_id=int(interaction.values[0]))
        await self.inter_to_delete.delete_original_message()
        await interaction.send(f"The new Room Administrator was installed <@{int(interaction.values[0])}>",
                               delete_after=10,
                               ephemeral=True)


class SelectSetting(disnake.ui.Select):
    def __init__(self, inter):
        self.inter = inter
        self.bot = inter.bot
        self.guild = inter.guild
        self.member = self.guild.get_member(inter.user.id)
        self.db_privates = CollectionActivePrivates()
        self.channel = self.member.voice.channel
        options = [
            disnake.SelectOption(label="Change room name", value="change_room_name"),
            disnake.SelectOption(label="Change number of users", value="change_user_value"),
            disnake.SelectOption(label="Change room administrator", value="change_room_administrator")]
        super().__init__(placeholder="Select a setting option", options=options, custom_id="SelectSettings",
                         min_values=1, max_values=1)

    async def callback(self, interaction: MessageInteraction):

        if "change_room_name" in interaction.values:
            await interaction.response.send_modal(NewRoomName(self.inter))
            await self.inter.delete_original_response()
        elif "change_user_value" in interaction.values:
            view = disnake.ui.View(timeout=None)
            view.add_item(UserValue(self.inter, inter_to_delete=interaction))
            await interaction.send("Select the quantity you need:",
                                   view=view,
                                   ephemeral=True)
            await self.inter.delete_original_response()
        elif "change_room_administrator" in interaction.values:
            if len(self.channel.members) > 1:
                view = disnake.ui.View(timeout=None)
                view.add_item(NewAdministrator(self.inter, inter_to_delete=interaction))
                await interaction.send("Choose who will become the new room Administrator: ",
                                       view=view,
                                       ephemeral=True)
            else:
                await interaction.send("At the moment, only you are in the voice channel!",
                                       ephemeral=True,
                                       delete_after=10)
            await self.inter.delete_original_response()


class NewOwner(commands.Cog):
    # Конструкция (bot : commands) здесь, чтобы дать IDE представление о том, какой тип данных содержит аргумент.
    # Это не обязательно, но может быть полезно при разработке.
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.db_privates = CollectionActivePrivates()

    @commands.user_command(name="Settings", guild_ids=CollectionServers().servers_id)
    async def lock(self, inter: disnake.GuildCommandInteraction, user: disnake.User):
        if user == inter.bot.user:
            await inter.send("You cannot use this command on a bot!", ephemeral=True, delete_after=10)
        else:
            view = disnake.ui.View(timeout=None)
            view.add_item(SelectSetting(inter))
            try:
                self.db_privates.new_data_channel(guild_id=inter.guild.id,
                                                  channel_id=inter.author.voice.channel.id,
                                                  owner_id=user.id)
                await inter.send(f"{inter.user.mention}, what would you like to configure?", view=view, ephemeral=True)
            except:
                await inter.send("You are not in the room!", delete_after=20, ephemeral=True)


def setup(bot: commands.Bot):
    bot.add_cog(NewOwner(bot))
