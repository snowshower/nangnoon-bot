import discord
from discord.ext import commands

class Message(commands.Cog):
    
    def __init__(self, bot):
        self.bot=bot
    
    @commands.command(name="안녕")
    async def hi_command(self, ctx):
        await ctx.send("안녕하세요!")
    
    @commands.command(name="응애")
    async def cry_command(self, ctx):
        await ctx.send("응애")

async def setup(bot):
    await bot.add_cog(Message(bot))