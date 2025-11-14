import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
import datetime
import pytz
from collections import defaultdict

from lotto_domain.lotto import lotto
from lotto_domain.lotto_rank import lotto_rank
from lotto_domain.lotto_result_calculator import lotto_result_calculator

KST=pytz.timezone("Asia/Seoul")

class lotto_result(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot=bot
        self.conn: sqlite3.Connection=self.bot.db_conn
        
    def get_kst_today(self) -> str:
        return datetime.datetime.now(KST).strftime('%Y-%m-%d')
    
    async def _check_user(self, user_id: int, guild_id: int):
        cursor=self.conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO users (user_id, guild_id) VALUES(?, ?)", (user_id, guild_id))
        self.conn.commit()
        
    @app_commands.command(name="로또결과", description="오늘 구매한 로또의 당첨 결과를 확인하세요!")
    async def check_lotto_results(self, interaction: discord.Interaction):
        
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
        
        cursor=self.conn.cursor()
        
        try:
            cursor.execute("SELECT numbers FROM winning_numbers WHERE date=?", (today_kst,))
            winning_row=cursor.fetchone()
            
            if not winning_row:
                await interaction.followup.send("⏳ 아직 오늘의 당첨 번호가 추첨되지 않았어요!", ephemeral=True)
                return
            
            winning_lotto=lotto([int(n) for n in winning_row["numbers"].split(',')])
            
            cursor.execute("""
                           SELECT ticket_id, numbers FROM lotto_tickets
                           WHERE user_id=? AND guild_id=? AND purchase_date=? AND status='pending'
                           """, (user_id, guild_id, today_kst))
            
            tickets_to_check=cursor.fetchall()
            
            if not tickets_to_check:
                await interaction.followup.send("ℹ️ 오늘 구매했거나 아직 확인하지 않은 로또가 없어요!")
                return
            
            my_lottos=[lotto([int(n) for n in row["numbers"].split(',')]) for row in tickets_to_check]
            
            statistics=lotto_result_calculator.calculate_all_results(winning_lotto, my_lottos)
            
            total_prize=0
            response_msg=(
                f"--- 🎫 **{interaction.user.display_name}님의 {today_kst} 로또 결과** ---\n"
                f"오늘의 당첨 번호: **`{winning_lotto.numbers}`**\n\n"
            )
            
            result_details=defaultdict(int)
            for rank, count in statistics.items():
                result_details[rank]+=count
                total_prize+=rank.prize_amount*count
            
            if total_prize==0:
                response_msg+="아쉽지만, 오늘은 꽝이에요 😥"
            else:
                for rank in sorted(result_details.keys(), key=lambda r: r.prize_amount, reverse=True):
                    if rank.prize_amount>0:
                        count=result_details[rank]
                        response_msg+=f"**{rank.description}** ({rank.prize_amount}P) x **{count}장** = **{rank.prize_amount*count}P**\n"
                
                response_msg+=f"\n🎉 **총 {total_prize}P**를 획득했어요!"
                
                await self._check_user(user_id, guild_id)
                cursor.execute("UPDATE users SET points=points+? WHERE user_id=? AND guild_id=?", (total_prize, user_id, guild_id))
            
            tickets_ids_to_update=[row["ticket_id"] for row in tickets_to_check]
            cursor.executemany("UPDATE lotto_tickets SET status='checked' WHERE ticket_id=?", [(tid,) for tid in tickets_ids_to_update])
            
            self.conn.commit()
            await interaction.followup.send(response_msg)
        
        except Exception as e:
            self.conn.rollback()
            print(f"[ERROR] 로또 결과: {e}")
            await interaction.followup.send(f"❌ 결과 확인 중 오류가 발생했습니다: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(lotto_result(bot))