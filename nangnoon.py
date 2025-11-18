import discord
from discord.ext import commands, tasks
import os   # cogs 폴더 안의 파일 목록을 읽기 위해 사용
import asyncio
from dotenv import load_dotenv
import sqlite3
import pytz
import datetime
from lotto_domain.lotto_generator import generate_lotto

load_dotenv()
BOT_TOKEN=os.getenv("BOT_TOKEN")

intents=discord.Intents.all()

bot=commands.Bot(command_prefix=None, intents=intents)

KST=pytz.timezone("Asia/Seoul")

try:
    DB_DIR="db"
    DB_PATH=os.path.join(DB_DIR, "lotto.db")
    
    os.makedirs(DB_DIR, exist_ok=True)
    
    bot.db_conn=sqlite3.connect(DB_PATH)
    bot.db_conn.row_factory=sqlite3.Row
    print(f"메인: DB 연결 성공. {DB_PATH}")
    
    cursor=bot.db_conn.cursor()
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS users(
                       user_id INTEGER NOT NULL,
                       guild_id INTEGER NOT NULL,
                       points INTEGER DEFAULT 0,
                       last_checkin TEXT DEFAULT '1970-01-01',
                       PRIMARY KEY (user_id, guild_id)
                   )
                   """)
    
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS lotto_tickets(
                       ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
                       user_id INTEGER NOT NULL,
                       guild_id INTEGER NOT NULL,
                       numbers TEXT NOT NULL,
                       purchase_date TEXT NOT NULL,
                       status TEXT DEFAULT 'pending'
                   )
                   """)
    
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS winning_numbers(
                       date TEXT PRIMARY KEY,
                       numbers TEXT NOT NULL
                   )
                   """)
    
    bot.db_conn.commit()
    print("메인: 모든 테이블 준비 완료.")

except Exception as e:
    print(f"메인: DB 연결 실패: {e}")
    exit()
    
@tasks.loop(time=datetime.time(hour=0, minute=0, tzinfo=KST))
async def daily_lotto_task():
    await bot.wait_until_ready()
    
    today=datetime.datetime.now(KST).strftime('%Y-%m-%d')
    print(f"[{today} 00:00] 일일 로또 태스크 시작...")
    
    try:
        cursor=bot.db_conn.cursor()
        
        new_winning_numbers=generate_lotto()
        numebrs_str=",".join(map(str, new_winning_numbers))
        
        cursor.execute("INSERT OR REPLACE INTO winning_numbers (date, numbers) VALUES (?, ?)", (today, numebrs_str))
        print(f"오늘({today})의 당첨 번호 생성 완료: {numebrs_str}")
        
        yesterday=(datetime.datetime.now(KST) - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        cursor.execute("""
                       UPDATE lotto_tickets
                       SET status = 'expired'
                       WHERE purchase_date=? AND status='pending'
                       """, (yesterday,))
        print(f"어제({yesterday})의 미확인 로또 폐기 완료.")
        
        bot.db_conn.commit()
    except Exception as e:
        print(f"일일 로또 태스크 실행 중 오류 발생: {e}")
        bot.db_conn.rollback()

@bot.event
async def on_ready():
    print(f'{bot.user} (으)로 로그인했습니다.')
    
    try:
        today=datetime.datetime.now(KST).strftime('%Y-%m-%d')
        cursor=bot.db_conn.cursor()
        cursor.execute("SELECT 1 FROM winning_numbers WHERE date=?", (today,))
        
        if cursor.fetchone() is None:
            print(f"[{today}] 봇 시작: 오늘자 당첨 번호가 없습니다. 즉시 생성합니다...")
            await daily_lotto_task()
        else:
            print(f"[{today}] 봇 시작: 오늘자 당첨 번호가 이미 존재합니다.")
    except Exception as e:
        print(f"봇 시작 시 당첨 번호 체크 실패: {e}")
    
    if not daily_lotto_task.is_running():
        daily_lotto_task.start()
        
    try:
        await bot.tree.sync()
        print("슬래시 커맨드 동기화 완료")
    except Exception as e:
        print(f"동기화 실패: {e}")

async def main():
    if BOT_TOKEN is None:
        print("[ERROR]: .env 파일에서 BOT_TOKEN을 찾을 수 없습니다.")
        return

    cogs_folder='./cogs'
    for filename in os.listdir(cogs_folder):
        if filename.endswith('.py'):
            module_name=f'cogs.{filename[:-3]}'
            try:
                await bot.load_extension(module_name)
                print(f"Cog 로드 성공: {module_name}")
            except Exception as e:
                print(f"Cog 로드 실패: {module_name} (에러: {e})")
    
    async with bot:
        await bot.start(BOT_TOKEN)

if __name__=='__main__':
    try:
        asyncio.run(main())
    finally:
        if hasattr(bot, 'db_conn'):
            bot.db_conn.close()
            print("메인: DB 연결 종료.")

    
# # 명령어 접두사를 !로 사용
# bot=commands.Bot(command_prefix='!', intents=intents)
# @bot.event
# async def on_ready():
#     print(f'{bot.user} (으)로 로그인했습니다.')
    
#     cogs_folder='./cogs'
#     for filename in os.listdir(cogs_folder):
#         if filename.endswith('.py'):
#             module_name=f'cogs.{filename[:-3]}'

#             try:
#                 await bot.load_extension(module_name)
#                 print(f"Cog 로드 성공: {module_name}")
#             except Exception as e:
#                 print(f"Cog 로드 실패: {module_name} (에러: {e})")

# BOT_TOKEN=os.getenv("BOT_TOKEN")

# if BOT_TOKEN is None:
#     print("[ERROR]: .env 파일에서 BOT_TOKEN을 찾을 수 없습니다.")
# else:
#     bot.run(BOT_TOKEN)