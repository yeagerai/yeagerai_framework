import random
import discord


class WorkflowEmbed(discord.Embed):
    def __init__(
        self,
        title: str,
        thread_ID: str,
        thread_url: str,
        description: str,
        initial_prompt: str,
        github_url: str,
    ) -> None:
        random_color = random.randint(0, 0xFFFFFF)
        super().__init__(color=random_color)

        self.title = title
        # self.description = description
        self.add_field(name="Initial Prompt", value=initial_prompt, inline=False)
        self.add_field(
            name="Discussion Thread", value=f"[{thread_ID}]({thread_url})", inline=False
        )
        self.add_field(
            name="GitHub Repository",
            value=f"[{github_url}]({github_url})",
            inline=False,
        )


class StepEmbed(discord.Embed):
    def __init__(
        self,
        title: str,
        description: str,
        step_dict: dict,
    ) -> None:
        random_color = discord.colour.Color.random()
        super().__init__(color=random_color)

        self.title = title
        self.description = description
        for key, value in step_dict.items():
            self.add_field(name=key, value=value[:1000] + "...", inline=False)
