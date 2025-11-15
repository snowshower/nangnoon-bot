import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
import datetime
import pytz

CHECKIN_REWARD=1000
KST=pytz.timezone("Asia/Seoul")

class Checkin(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot=bot
        self.conn: sqlite3.Connection=self.bot.db_conn
    
    def get_kst_today(self) -> str:
        return datetime.datetime.now(KST).strftime('%Y-%m-%d')
    
    async def _get_or_create_user(self, user_id: int, guild_id: int) -> sqlite3.Row:
        cursor=self.conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = ? AND guild_id = ?", (user_id, guild_id))
        user_data=cursor.fetchone()
        
        if user_data:
            return user_data
        else:
            try:
                cursor.execute("INSERT INTO users (user_id, guild_id) VALUES (?, ?)", (user_id, guild_id))
                self.conn.commit()
                
                cursor.execute("SELECT * FROM users WHERE user_id = ? AND guild_id = ?", (user_id, guild_id))
                return cursor.fetchone()
            except sqlite3.IntegrityError:
                cursor.execute("SELECT * FROM users WHERE user_id = ? AND guild_id = ?", (user_id, guild_id))
                return cursor.fetchone()
    
    @app_commands.command(name="출석체크", description="하루에 한 번 포인트를 받습니다!")
    async def check_in(self, interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message("❌ 이 명령어는 서버에서만 사용할 수 있어요!", ephemeral=True)
            return
        
        if not self.conn:
            await interaction.response.send_message("❌ DB가 준비되지 않았습니다.", ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=True)
        
        try:
            user_id=interaction.user.id
            guild_id=interaction.guild.id
            today_kst=self.get_kst_today()
            
            user_data=await self._get_or_create_user(user_id, guild_id)
            
            if user_data["last_checkin"]==today_kst:
                await interaction.followup.send("✅ 오늘은 이미 출석체크를 완료했어요!")
                return
            
            cursor=self.conn.cursor()
            cursor.execute("""
                           UPDATE users
                           SET points=points+?, last_checkin=?
                           WHERE user_id=? AND guild_id=?
                           """, (CHECKIN_REWARD, today_kst, user_id, guild_id))
            self.conn.commit()
            
            new_points=user_data["points"]+CHECKIN_REWARD
            await interaction.followup.send(
                f"출석체크 완료! **{CHECKIN_REWARD}P**를 획득했어요!\n"
                f"(현재 보유 포인트: **{new_points}P**)"
            )
        
        except Exception as e:
            print(f"[ERROR: 출석체크 오류]: {e}")
            await interaction.followup.send("❌ 출석체크 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(heckin(bot))