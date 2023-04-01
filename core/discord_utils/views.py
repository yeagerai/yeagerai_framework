import asyncio
import urllib

import discord

from core.discord_utils.modals import StepEditModal, AddCollaboratorsModal


class RetryView(discord.ui.View):
    def __init__(self) -> None:
        super().__init__()
        self.result_future: asyncio.Future = asyncio.Future()

    @discord.ui.button(label="Retry", style=discord.ButtonStyle.blurple)
    async def retry(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        await interaction.response.send_message(content="Retrying...")
        # await interaction.response.defer()
        self.result_future.set_result("retry")
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        await interaction.response.send_message(
            content="Canceling, and finishing the workflow creation..."
        )
        # await interaction.response.defer()
        self.result_future.set_result("cancel")
        self.stop()


class StepEditView(discord.ui.View):
    def __init__(self, original_embed: discord.Embed, step_dict: dict) -> None:
        super().__init__()

        self.embed = original_embed
        self.step_dict = step_dict
        self.updated_values: asyncio.Future = asyncio.Future()

    # Add the "Edit" button
    @discord.ui.button(label="Edit", style=discord.ButtonStyle.secondary, emoji="📝")
    async def edit_callback(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        modal = StepEditModal(self.step_dict, self.embed)
        await interaction.response.send_modal(modal)
        self.updated_values.set_result(await modal.new_step_dict)
        # await interaction.response.defer()
        await interaction.response.send_message(content="Editing...")
        self.stop()

    # Add the "Approve" button
    @discord.ui.button(label="Approve", style=discord.ButtonStyle.success, emoji="✅")
    async def approve_callback(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        # Send the original embed message
        self.updated_values.set_result(self.step_dict)
        # await interaction.response.defer()
        await interaction.response.send_message(content="Approving...")
        self.stop()


class TweetButton(discord.ui.View):
    def __init__(self, tweet_text: str) -> None:
        super().__init__()
        self.tweet_url = (
            f"https://twitter.com/intent/tweet?text={urllib.parse.quote(tweet_text)}"
        )
        # Add the tweet button
        self.add_item(discord.ui.Button(label="Tweet this!", url=self.tweet_url))

    async def callback(self, interaction: discord.Interaction) -> None:
        # This method is required for the view to work
        pass


class AddCollaboratorsView(discord.ui.View):
    def __init__(self) -> None:
        super().__init__()
        self.collaborators_names: asyncio.Future = asyncio.Future()

    # Add the "Edit" button
    @discord.ui.button(
        label="Add Collaborators", style=discord.ButtonStyle.secondary, emoji="👨‍💻"
    )
    async def edit_callback(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        modal = AddCollaboratorsModal()
        await interaction.response.send_modal(modal)
        self.collaborators_names.set_result(
            (await modal.collaborators_string).split("\n")
        )
        await interaction.followup.send(content="Adding collaborators...")
        self.stop()
