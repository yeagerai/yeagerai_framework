import typing
from functools import partial
import re

import discord
from discord.ext import commands

from yeagerai.interfaces.discord.views import RetryView, AddCollaboratorsView
from yeagerai.interfaces.discord.embeds import StepEmbed, WorkflowEmbed
from yeagerai.interfaces.discord.views import StepEditView, TweetButton


async def send_message(
    bot: commands.Bot, ctx: typing.Any, thread: discord.Thread, message: str
) -> None:
    await thread.send(message)


async def retry_component(
    bot: commands.Bot, ctx: typing.Any, thread: discord.Thread, message: str
) -> str:
    view = RetryView()
    await thread.send(content=message, view=view)
    await view.wait()
    result = await view.result_future
    return result


async def edit_step(
    bot: commands.Bot,
    ctx: typing.Any,
    thread: discord.Thread,
    title: str,
    description: str,
    step_dict: dict,
) -> dict:
    step_embed = StepEmbed(title=title, description=description, step_dict=step_dict)
    step_view = StepEditView(step_embed, step_dict=step_dict)
    await thread.send(embed=step_embed, view=step_view)
    return await step_view.updated_values


async def add_collaborators(
    bot: commands.Bot,
    ctx: typing.Any,
    thread: discord.Thread,
) -> dict:
    message_content = "Add collaborators to your workflow. Invite yourself and others to the github repository!"
    add_collaborators_view = AddCollaboratorsView()
    await thread.send(message_content, view=add_collaborators_view)
    return await add_collaborators_view.collaborators_names


async def edit_channel_orig_embed(
    bot: commands.Bot,
    ctx: typing.Any,
    thread: discord.Thread,
    orig_message: discord.Message,
    title: str,
    description: str,
    github_url: str,
) -> None:
    mention_string = re.search(r"<@!?(\d+)>", orig_message.content).group(0)
    orig_embed = orig_message.embeds[0]
    initial_prompt = orig_embed.fields[0].value
    thread_ID = orig_embed.fields[1].value
    thread_url = orig_embed.fields[2].value

    wf_new_embed = WorkflowEmbed(
        title=title,
        description=description,
        thread_ID=thread_ID,
        thread_url=thread_url,
        github_url=github_url,
        initial_prompt=initial_prompt,
    )

    tweet_text = f"Check out this awesome workflow I created using Yeager! 🚀👨‍💻\n\n You can see the results on this GitHub link: {github_url}\n\n Don't forget to join our community: https://discord.gg/VpfmXEMN66\n\n @yeagerai #yeager #ai #community"
    updated_tweet_button = TweetButton(tweet_text=tweet_text)
    await orig_message.edit(
        content=mention_string, embed=wf_new_embed, view=updated_tweet_button
    )


## it can be generalized to parse all the file and doit in a for loop for every method
def wrap_callbacks(
    bot: commands.Bot, ctx: commands.Context, thread: discord.Thread
) -> dict:
    def custom_callback(callback: typing.Callable) -> typing.Callable:
        async def wrapper(*args: typing.Any, **kwargs: typing.Any) -> typing.Any:
            return await callback(bot, ctx, thread, *args, **kwargs)

        return partial(wrapper)

    wrapped_callback1 = custom_callback(partial(send_message))
    wrapped_callback2 = custom_callback(partial(retry_component))
    wrapped_callback3 = custom_callback(partial(edit_step))
    wrapped_callback4 = custom_callback(partial(edit_channel_orig_embed))
    wrapped_callback5 = custom_callback(partial(add_collaborators))

    callbacks = {
        "send_message": wrapped_callback1,
        "retry_component": wrapped_callback2,
        "edit_step": wrapped_callback3,
        "edit_channel_orig_embed": wrapped_callback4,
        "add_collaborators": wrapped_callback5,
    }

    return callbacks
