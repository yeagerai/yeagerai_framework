import asyncio
import discord

from core.discord_utils.embeds import StepEmbed


class StepEditModal(
    discord.ui.Modal, title="Edit and Approve the following parameters"
):
    def __init__(self, step_dict: dict, embed: StepEmbed) -> None:
        super().__init__()
        self.embed = embed
        self.new_step_dict: asyncio.Future = asyncio.Future()

        for key, value in step_dict.items():
            self.add_item(
                discord.ui.TextInput(
                    label=key, default=value, style=discord.TextStyle.long
                )
            )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        new_step_dict = {}
        for index, field in enumerate(self.embed.fields):
            new_step_dict[field.name] = self.children[index].value
        new_embed = StepEmbed(self.embed.title, self.embed.description, new_step_dict)
        await interaction.response.edit_message(embed=new_embed)
        self.new_step_dict.set_result(new_step_dict)
        self.stop()


class AddCollaboratorsModal(
    discord.ui.Modal, title="Add yourself and others to the repository"
):
    def __init__(self) -> None:
        super().__init__()
        self.collaborators_string: asyncio.Future = asyncio.Future()

        self.add_item(
            discord.ui.TextInput(
                label="Add Collaborators one per line",
                placeholder="colaborator-github-username-1\ncolaborator-github-username-2\n",
                style=discord.TextStyle.long,
            )
        )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        self.collaborators_string.set_result(self.children[0].value)
        self.stop()
