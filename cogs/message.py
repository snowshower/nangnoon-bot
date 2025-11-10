import discord
from discord.ext import commands
from discord import app_commands

class Message(commands.Cog):
    
    def __init__(self, bot):
        self.bot=bot
    
    @app_commands.command(name="안녕", description="안녕")
    async def hi_command(self, interaction: discord.Interaction):
        await interaction.response.send_message("❄️안녕하세요!")
    
    @app_commands.command(name="응애", description="응애")
    async def cry_command(self, interaction: discord.Interaction):
        await interaction.response.send_message("🍼응애")
        
    @app_commands.command(name="인생사", description="인생사")
    async def life_command(self, interaction: discord.Interaction):
        await interaction.response.send_message("🏇새옹지마")
        
    @app_commands.command(name="빵구", description="빵구")
    async def poop_command(self, interaction: discord.Interaction):
        await interaction.response.send_message("💨뿡!")
        
    @app_commands.command(name="바부", description="빵구")
    async def stupid_command(self, interaction: discord.Interaction):
        await interaction.response.send_message("🫵")

async def setup(bot):
    await bot.add_cog(Message(bot))