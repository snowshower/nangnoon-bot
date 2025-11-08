import discord
from discord.ext import commands

class Message(commands.Cog):
    
    def __init__(self, bot):
        self.bot=bot
    
    @commands.command(name="안녕")
    async def hi_command(self, ctx):
        await ctx.send("❄️안녕하세요!")
    
    @commands.command(name="응애")
    async def cry_command(self, ctx):
        await ctx.send("🍼응애")
        
    @commands.command(name="인생사")
    async def life_command(self, ctx):
        await ctx.send("🏇새옹지마")
        
    @commands.command(name="빵구")
    async def poop_command(self, ctx):
        await ctx.send("💨뿡!")
        
    @commands.command(name="바부")
    async def stupid_command(self, ctx):
        await ctx.send("🫵")

async def setup(bot):
    await bot.add_cog(Message(bot))