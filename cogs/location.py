import discord
from discord.ext import commands
from cogs.utils import checks
from __main__ import send_cmd_help, settings
import re
import os
import datetime
import csv
from .utils.dataIO import dataIO

try:
    import pycountry
except:
    pycountry = None
    
try:
    import plotly.plotly as py
    import plotly
except:
    plotly = None

class Location:

    def __init__(self, bot):
        self.countries = dataIO.load_json("data/countrycode/countries.json")
        self.subregions = dataIO.load_json("data/countrycode/subregions.json")
        self.settings = dataIO.load_json("data/countrycode/settings.json")
        self.cooldown = datetime.datetime.now()
        self.lastlink = ""
        self.bot = bot
        
    @commands.group(pass_context=True, no_pm=True)
    @checks.admin_or_permissions(ban_members=True)
    async def location_settings(self, ctx):
        """Manages settings for the location cog."""
        if ctx.invoked_subcommand is None:
            server = ctx.message.server
            await send_cmd_help(ctx)
            
    @location_settings.command(name="plotly", pass_context=True)
    async def _plotly(self, ctx, username:str, api_key:str):
        """Setting for plotly api."""
        self.settings["plotly"]={}
        self.settings["plotly"]["username"]= username
        self.settings["plotly"]["api_key"] = api_key
        dataIO.save_json("data/countrycode/settings.json", self.settings)
        await self.bot.say("Plotly set!")

    @commands.command(pass_context=True, no_pm=True)
    async def locate(self, ctx, user: discord.Member):
        """Example: [p]locate @Nop0x
            Requires Mention or Name"""
        msg = user.name + " has the following countries set: ```"
        self.countries = dataIO.load_json("data/countrycode/countries.json")
        self.subregions = dataIO.load_json("data/countrycode/subregions.json")
        for country in self.countries:
            if user.id in self.countries[country]:
                msg += "•" + country + "\n"
        msg += "```"
        if msg == user.name + " has the following countries set: ``````":
            await self.bot.say(user.name + " has no country set :(")
            return
        await self.bot.say(msg)

    @commands.command(pass_context=True, no_pm=True)
    async def location(self, ctx, country: str):
        """Example: [p]location GB"""
        self.countries = dataIO.load_json("data/countrycode/countries.json")
        self.subregions = dataIO.load_json("data/countrycode/subregions.json")
        
        server = ctx.message.server
        user = ctx.message.author

        re1 = '((?:[a-z][a-z]+))'  # Word 1
        re2 = '.*?'  # Non-greedy match on filler
        re3 = '((?:[a-z][a-z]+))'  # Word 2
        rg = re.compile(re1 + re2 + re3, re.IGNORECASE | re.DOTALL)

        m = rg.search(country)
        subregionobj = None
        try:
            if m:
                word1 = m.group(1)
                countryobj = pycountry.countries.get(alpha_2=word1.upper())
                subregionobj = pycountry.subdivisions.get(code=country.upper())
            else:
                countryobj = pycountry.countries.get(alpha_2=country.upper())
        except:
            countryobj = None

        if countryobj is not None:
            if subregionobj is not None:
                msg = "Members from " + countryobj.name + ": " + subregionobj.name + " :flag_" + countryobj.alpha_2.lower() + ": ```"
                try:
                    for member in server.members:
                        if member.id in self.subregions[subregionobj.code]:
                            msg = msg + "\n• " + member.name
                    msg = msg + "```"
                    if msg != "Members from " + countryobj.name + ": " + subregionobj.name + " :flag_" + countryobj.alpha_2.lower().lower() + ": ``````":
                        await self.bot.send_message(user,msg)
                    else:
                        await self.bot.say(
                            "No one found in " + countryobj.name + ": " + subregionobj.name + " :flag_" + countryobj.alpha_2.lower().lower() + ": :(")
                except:
                    await self.bot.say(
                            "No one found in " + countryobj.name + ": " + subregionobj.name + " :flag_" + countryobj.alpha2.lower().lower() + ": :(")
            else:
                msg = "Members from " + countryobj.name + " :flag_"+ countryobj.alpha_2.lower() +": ```"
                try:
                    for member in server.members:
                        if member.id in self.countries[countryobj.name]:
                            msg = msg + "\n• " + member.name
                    msg = msg + "```"
                    if msg != "Members from " + countryobj.name + " :flag_"+ countryobj.alpha_2.lower() +": ``````":
                        await self.bot.send_message(user,msg)
                    else:
                        await self.bot.say("No one found in " + countryobj.name + " :flag_"+ countryobj.alpha_2.lower() +": :(")
                except:
                    await self.bot.say("No one found in " + countryobj.name + " :flag_"+ countryobj.alpha_2.lower() +": :(")
        else:
            await self.bot.say("Sorry I don't know your country! Did you use the correct ISO countrycode? \nExample: `-location GB`")
                
    @commands.command(pass_context=True, no_pm=True)
    async def map(self, ctx):
        try:
            if (self.settings["plotly"]["username"] is None) | (self.settings["plotly"]["api_key"] is None):
                await self.bot.say("Plotly api access is not set up! Please head to <https://plot.ly/settings/api> and get your username and api key!")
                return
        except KeyError:
            await self.bot.say("Plotly api access is not set up! Please head to <https://plot.ly/settings/api> and get your username and api key!")
            return
        
        if(datetime.datetime.now() < self.cooldown):
            await self.bot.say("The holy map of awesomness: " + self.lastlink)
            return
        msg = await self.bot.say("Looking up where members are from...")
        with open("data/countrycode/countries.csv", 'w') as myfile:
            wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
            templist2 = ["code", "count"]
            wr.writerow(templist2)
            d = dataIO.load_json('data/countrycode/countries.json')
            total = len(d)
            i=0
            for country in d:
                await self.bot.edit_message(msg, "Looking up where members are from: " + str(i) + "/" + str(total))
                con = pycountry.countries.get(name=country)
                count = len(d[country])
                i += 1
                if count != 0:
                    templist=[con.alpha_3,count]
                    wr.writerow(templist)
        
        plotly.tools.set_credentials_file(username=self.settings["plotly"]["username"], api_key=self.settings["plotly"]["api_key"])
        df = pd.read_csv('data/countrycode/countries.csv')
        client_id = self.settings["imgur"]["client_id"]
        client_secret = self.settings["imgur"]["client_secret"]
        client = ImgurClient(client_id, client_secret)
        
        data = [ dict(
                type = 'choropleth',
                locations = df['code'],
                z = df['count'],
                autocolorscale = True,
                reversescale = False,
                marker = dict(
                    line = dict (
                        color = 'rgb(180,180,180)',
                        width = 0.5
                    ) ),
                colorbar = dict(),
              ) ]
        
        layout = dict(
            title = 'World Map',
            geo = dict(
                showframe = False,
                showcoastlines = True,
            )
        )
        await self.bot.edit_message(msg, "Generating heatmap...")
        fig = dict( data=data, layout=layout )
        py.image.save_as(fig, filename='worldmap.png', scale=2, width=1920, height = 1080)
        msg = await self.bot.send_file(ctx.message.channel,'worldmap.png')
        self.lastlink = msg.attachments[0]['url']
        self.cooldown = datetime.datetime.now() + datetime.timedelta(hours=1)
        
def check_folders():
    folders = ("data", "data/countrycode/")
    for folder in folders:
        if not os.path.exists(folder):
            print("Creating " + folder + " folder...")
            os.makedirs(folder)
            
def check_files():
    if not os.path.isfile("data/countrycode/countries.json"):
        print("Creating empty countries.json...")
        dataIO.save_json("data/countrycode/countries.json", {})
    if not os.path.isfile("data/countrycode/settings.json"):
        print("Creating empty settings.json...")
        dataIO.save_json("data/countrycode/settings.json", {})
    if not os.path.isfile("data/countrycode/subregions.json"):
        print("Creating empty subregions.json...")
        dataIO.save_json("data/countrycode/subregions.json", {})
        
def setup(bot):
    if pycountry is None:
        raise RuntimeError("You need to run pip3 install pycountry")
    if plotly is None:
        raise RuntimeError("You need to run pip3 install plotly")
    check_folders()
    check_files()
    bot.add_cog(Location(bot))
