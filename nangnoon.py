import discord
from discord.ext import commands
import os   # cogs 폴더 안의 파일 목록을 읽기 위해 사용
import asyncio
from dotenv import load_dotenv
import sqlite3

load_dotenv()
BOT_TOKEN=os.getenv("BOT_TOKEN")

intents=discord.Intents.all()

bot=commands.Bot(command_prefix=None, intents=intents)

try:
    bot.db_conn=sqlite3.connect("lotto.db")
    bot.db_conn.row_factory=sqlite3.Row
    print("메인: DB 연결 성공. (lotto.db)")
    
    cursor=bot.db_conn.cursor()
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS users(
                       user_id INTEGER PRIMARY KEY,
                       points INTEGER DEFAULT 0,
                       last_checkin TEXT DEFAULT '1970-01-01'
                   )
                   """)
    
    bot.db_conn.commit()
    print("메인: 모든 테이블 준비 완료.")

except Exception as e:
    print(f"메인: DB 연결 실패: {e}")
    exit()

@bot.event
async def on_ready():
    print(f'{bot.user} (으)로 로그인했습니다.')
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