import logging
import math
import random
from typing import Iterable, Union
import discord
from utils.multiple_choice import BotMultipleChoice


from discord import Embed, Message
from discord.ext import commands

log = logging.getLogger(__name__)


class CommandErrorHandler(commands.Cog, command_attrs={"hidden": True}):
    """A error handler for the Bot server. hidden """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @staticmethod
    def revert_cooldown_counter(command: commands.Command, message: Message) -> None:
        """Undoes the last cooldown counter for user-error cases."""
        if command._buckets.valid:
            bucket = command._buckets.get_bucket(message)
            bucket._tokens = min(bucket.rate, bucket._tokens + 1)
            logging.debug(
                "Cooldown counter reverted as the command was not used correctly."
            )

    @staticmethod
    def error_embed(message: str, title: Union[Iterable, str] = "NOPE") -> Embed:
        """Build a basic embed with red colour and either a random error title or a title provided."""
        embed = Embed(colour=0xFF0000)
        if isinstance(title, str):
            embed.title = title
        else:
            embed.title = random.choice(title)
        embed.description = message
        return embed

    @commands.Cog.listener()
    async def on_error(self, event , *args, **kwargs):
        me = await self.bot.fetch_user(355658987372281856)
        embed = Embed(title="ERROR", description=str(event), color=0xFF0000)
        embed.add_field(name='Args', value=str(args))
        embed.add_field(name='Kwargs', value=str(kwargs))
        await me.send(embed=embed)
        
    @commands.Cog.listener()
    async def on_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        """Activates when a command opens an error."""

        if hasattr(ctx.command, "on_error"):
            logging.debug(
                "A command error occurred but the command had it's own error handler."
            )
            return

        error = getattr(error, "original", error)
        logging.debug(
            f"Error Encountered: {type(error).__name__} - {str(error)}, "
            f"Command: {ctx.command}, "
            f"Author: {ctx.author}, "
            f"Channel: {ctx.channel}"
        )

        if isinstance(error, commands.CommandNotFound):  # Where the real magic happens
            all_commands_list = []
            commands_list = []
            for command in self.bot.commands:
                if command.name.startswith(ctx.invoked_with.lower()):
                    commands_list.append(command.name)
                all_commands_list.append(command.name)

            if len(commands_list) == 1:
                command = self.bot.get_command(commands_list[0])
                ctx.command = command
                await ctx.send(f"**Invoking command** - {command.name}")
                await self.bot.invoke(ctx)
                return
            if len(commands_list) == 0:

                return

            multiple_choice = BotMultipleChoice(
                ctx,
                commands_list,
                f"I was unable to find the command you meant. You probably "
                f"meant a command from these",
            )
            await multiple_choice.run()
            await multiple_choice.quit(multiple_choice.choice)
            user_answer = multiple_choice.choice
            if user_answer is None:
                return
            command = self.bot.get_command(user_answer)
            ctx.command = command
            await ctx.send(f"**Invoking command** - {command.name}")

            await self.bot.invoke(ctx)
            return

        if isinstance(error, discord.Forbidden):
            self.revert_cooldown_counter(ctx.command, ctx.message)
            embed = self.error_embed(
                f"Seems like I don't have perm to do one of that task. Invite me with this link to fix that - "
                f"https://discordapp.com/oauth2/authorize?client_id={self.bot.user.id}&scope=bot&permissions=8"
            )
            n = await ctx.send(embed=embed, delete_after=7.5)
            return

        if isinstance(error, commands.UserInputError):
            self.revert_cooldown_counter(ctx.command, ctx.message)
            embed = self.error_embed(
                f"Your input was invalid: {error}\n\nUsage:\n```{ctx.prefix}{ctx.command} {ctx.command.signature}```"
            )
            await ctx.send(embed=embed, delete_after=7.5)
            return

        if isinstance(error, commands.CommandOnCooldown):
            mins, secs = divmod(math.ceil(error.retry_after), 60)
            await ctx.send(
                f"This command is on cooldown:\nPlease retry in {mins} minutes {secs} seconds.",
                delete_after=7.5,
            )
            return

        if isinstance(error, commands.DisabledCommand):
            await ctx.send(
                embed=self.error_embed("This command has been disabled.", "NOPE"),
                delete_after=7.5,
            )
            return

        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send(
                embed=self.error_embed(
                    "This command can only be used in the server.", "NOPE"
                ),
                delete_after=7.5,
            )
            return

        if isinstance(error, commands.BadArgument):
            self.revert_cooldown_counter(ctx.command, ctx.message)
            embed = self.error_embed(
                "The argument you provided was invalid: "
                f"{error}\n\nUsage:\n```{ctx.prefix}{ctx.command} {ctx.command.signature}```"
            )
            await ctx.send(embed=embed, delete_after=7.5)
            return

        if isinstance(error, commands.CheckFailure):
            return

        await ctx.send(
            "Ahhhh. That was not supposed to happen. My developer got notified of this and will fix it."
        )
        raise error


def setup(bot: commands.Bot) -> None:
    """Error handler Cog load."""
    bot.add_cog(CommandErrorHandler(bot))
    print("Error_handler loaded")
