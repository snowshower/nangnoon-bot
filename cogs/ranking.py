import discord
from discord.ext import commands
from discord import app_commands
import sqlite3

class Ranking(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot=bot
        self.conn: sqlite3.Connection=self.bot.db_conn
    
    @app_commands.command(name="랭킹", description="포인트 랭킹 TOP 10을 봅니다")
    async def show_ranking(self, interaction:discord.Interaction):
        
        if interaction.guild is None:
            await interaction.response.send_message("❌ 이 명령어는 서버에서만 사용할 수 있어요!", ephemeral=True)
            return
        
        if not self.conn:
            await interaction.response.send_message("❌ DB가 준비되지 않았습니다.", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        guild_id=interaction.guild.id
        
        try:
            cursor=self.conn.cursor()
            
            cursor.execute("""
                           SELECT user_id, points FROM users
                           WHERE guild_id=?
                           ORDER BY points DESC
                           LIMIT 10
                           """, (guild_id,))
            
            rank_data=cursor.fetchall()
            
            if not rank_data:
                await interaction.followup.send("ℹ️ 아직 서버에 랭킹 데이터가 없어요!")
                return
            
            response_msg=f"=== 🏆 **{interaction.guild.name} 서버 포인트 랭킹** ===\n\n"
            
            for i, row in enumerate(rank_data):
                user_id=row["user_id"]
                points=row["points"]
                
                user_name=f"Unknown User ({user_id})"
                try:
                    user=self.bot.get_user(user_id) or await self.bot.fetch_user(user_id)
                    user_name=user.display_name if user else f"Unknown User ({user_id})"
                except discord.NotFound:
                    user_name=f"알 수 없는 유저 ({user_id})"
                
                emoji=""
                if i==0:
                    emoji="🥇"
                elif i==1:
                    emoji="🥈"
                elif i==2:
                    emoji="🥉"
                else:
                    emoji=f"**{i+1}위**"
                
                response_msg+=f"{emoji} {user_name}: **{points}P**\n"
            
            await interaction.followup.send(response_msg)
        
        except Exception as e:
            print(f"[ERROR]: 랭킹: {e}")
            await interaction.followup.send(f"❌ 랭킹을 불러오는 중 오류가 발생했어요! {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Ranking(bot))