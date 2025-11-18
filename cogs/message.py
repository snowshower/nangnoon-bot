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
        
    @app_commands.command(name="인생사", description="life is...")
    async def life_command(self, interaction: discord.Interaction):
        await interaction.response.send_message("🏇새옹지마")
        
    @app_commands.command(name="빵구", description="빵구")
    async def poop_command(self, interaction: discord.Interaction):
        await interaction.response.send_message("💨뿡!")
        
    @app_commands.command(name="바부", description="바부")
    async def stupid_command(self, interaction: discord.Interaction):
        await interaction.response.send_message("🫵")
    
    @app_commands.command(name="쉿", description="증명하세요.")
    async def shh_command(self, interaction: discord.Interaction):
        gif_path="assets/faker-shush.gif"
        gif_filename="faker-shush.gif"
        try:
            file_to_send=discord.File(gif_path, filename=gif_filename)
            
            embed=discord.Embed()
            
            embed.set_image(url=f"attachment://{gif_filename}")
            
            await interaction.response.send_message(embed=embed, file=file_to_send)
        except FileNotFoundError:
            await interaction.response.send_message("증명하세요.")

async def setup(bot):
    await bot.add_cog(Message(bot))