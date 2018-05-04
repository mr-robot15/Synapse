import discord
from discord.ext import commands
from random import choice as randchoice

class coinbet:

    def __init__(self, bot):
        self.bot = bot
        self.list_allowed_words = ["heads","h","tails","t"]
        self.list_heads = ["heads","h"]
        self.list_tails = ["tails","t"]

    @commands.command(pass_context="True")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def bet(self, ctx, number : int, choice):
        choice = choice.lower()
        user = ctx.message.author
        bank = self.bot.get_cog("Economy").bank
        account = bank.get_account(user)

        if number <= 0:
            await self.bot.say("You need to pick a number higher than 0")

        elif number > 10000:
            await self.bot.say("Slow down there money bags! Bet a little less!")

        elif not bank.can_spend(user, number):
            await self.bot.say("You do not have enough money to bet!")

        elif choice in self.list_allowed_words:
            result = randchoice(["HEADS!*", "TAILS!*"])
            await self.bot.say("*flips a coin and... " + result)

            if result == "HEADS!*" and choice in self.list_heads:
                await self.bot.say("You won, " + user.display_name + "!")
                await self.bot.say("You doubled your bet!")
                amount = number 
                bank.deposit_credits(user, amount)

            elif result == "HEADS!*" and choice not in self.list_heads:
                await self.bot.say("Oh no..." + user.display_name + ".")
                await self.bot.say("You lost your bet. ):")
                amount = number
                bank.withdraw_credits(user, amount)

            elif result == "TAILS!*" and choice in self.list_tails:
                await self.bot.say("You won, " + user.display_name + "!")
                await self.bot.say("You doubled your bet!")
                amount = number 
                bank.deposit_credits(user, amount)

            elif result == "TAILS!*" and choice not in self.list_tails:
                await self.bot.say("Oh no..." + user.display_name + ".")
                await self.bot.say("You lost your bet. ):")
                amount = number
                bank.withdraw_credits(user, amount)



def setup(bot):
    bot.add_cog(coinbet(bot))
