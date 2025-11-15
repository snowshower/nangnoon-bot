import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
import datetime
import pytz

from lotto_domain.lotto_generator import generate_lotto

KST=pytz.timezone("Asia/Seoul")
LOTTO_PRICE=1000

class LottoBuy(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot=bot
        self.conn: sqlite3.Connection=self.bot.db_conn
        
    def get_kst_today(self) -> str:
        return datetime.datetime.now(KST).strftime('%Y-%m-%d')
    
    async def _get_or_create_user(self, user_id: int, guild_id: int) -> sqlite3.Row:
        cursor=self.conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id=? AND guild_id=?", (user_id, guild_id))
        user_data=cursor.fetchone()
        
        if user_data:
            return user_data
        else:
            try:
                cursor.execute("INSERT INTO users(user_id, guild_id) VALUES(?, ?)", (user_id, guild_id))
                self.conn.commit()
                cursor.execute("SELECT * FROM users WHERE user_id=? AND guild_id=?", (user_id, guild_id))
                return cursor.fetchone()
            except sqlite3.IntegrityError:
                cursor.execute("SELECT * FROM users WHERE user_id=? AND guild_id=?", (user_id, guild_id))
                return cursor.fetchone()
    
    @app_commands.command(name="로또구매", description="포인트로 로또를 구매하세요!")
    @app_commands.describe(count="구매할 로또 개수(1~10장)")
    async def buy_lotto(self, interaction: discord.Interaction, count: app_commands.Range[int, 1, 10]):
        
        if interaction.guild is None:
            await interaction.response.send_message("❌ 이 명령어는 서버에서만 사용할 수 있어요!", ephemeral=True)
            return
        
        if not self.conn:
            await interaction.response.send_message("❌ DB가 준비되지 않았습니다.", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        user_id=interaction.user.id
        guild_id=interaction.guild.id
        today_kst=self.get_kst_today()
        total_cost=count*LOTTO_PRICE
        
        try:
            user_data=await self._get_or_create_user(user_id, guild_id)
            current_points=user_data["points"]
            
            if current_points<total_cost:
                await interaction.followup.send(
                    f"❌ 포인트가 부족해요!\n"
                    f"(현재 보유 포인트: {current_points}P / 구매 필요: {total_cost}P)",
                    ephemeral=True
                )
                return
            
            cursor=self.conn.cursor()
            
            cursor.execute("""
                           UPDATE users SET points=points-?
                           WHERE user_id=? AND guild_id=?
                           """, (total_cost, user_id, guild_id))
            
            bought_tickets_str=[]
            for _ in range(count):
                new_numbers_list=generate_lotto()
                numbers_str=",".join(map(str, new_numbers_list))
                
                cursor.execute("""
                               INSERT INTO lotto_tickets (user_id, guild_id, numbers, purchase_date, status)
                               VALUES(?, ?, ?, ?, 'pending')
                               """, (user_id, guild_id, numbers_str, today_kst))
                
                bought_tickets_str.append(f"🎫 `{str(new_numbers_list)}`")
            
            self.conn.commit()
            
            response_msg=(
                f"✅ **로또 {count}장 구매 완료!** (총 {total_cost}P 지출)\n"
                f"남은 포인트: {current_points-total_cost}P\n\n"
                f"**{interaction.user.display_name}님의 구매 번호!**\n"
            )
            response_msg+="\n".join(bought_tickets_str)
            await interaction.followup.send(response_msg)
        
        except Exception as e:
            self.conn.rollback()
            print(f"[ERROR]: 로또구매 {e}")
            await interaction.followup.send(f"❌ 구매 중 오류가 발생했습니다: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(LottoBuy(bot))