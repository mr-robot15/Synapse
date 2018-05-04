import discord
import datetime
from cogs.utils import checks
from discord.ext import commands

__spiced_up_by__ = "Young™#5484"
__author__ = "Neo#1375"

class Pm:
    """PM People Using The Bot"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    @checks.is_owner()
    async def whisper(self, ctx, user_id: str, *, msg: str):
        """Dm users."""
        user = await self.bot.get_user_info(user_id)
        try:
            e = discord.Embed(colour=discord.Colour.red())
            e.add_field(name="Message:", value=msg, inline=False)
            await self.bot.send_message(user, msg)
        except:
            await self.bot.say(':x: Failed to send message to user_id `{}`.'.format(user_id))
        else:
            await self.bot.say('Succesfully sent message to {}'.format(user_id))		

def setup(bot):
    bot.remove_command('whisper')
    n = Pm(bot)
    bot.add_cog(n)


