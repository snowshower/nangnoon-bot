import discord
from discord.ext import commands
import random

class Fortunes(commands.Cog):
    
    def __init__(self, bot):
        self.bot=bot
        
        self.fortunes=[]
        try:
            with open('fortunes.txt', 'r', encoding='utf-8') as f:
                self.fortunes=[line.strip() for line in f.readlines()]
            
            if self.fortunes:
                print(f"포춘쿠키 문장 {len(self.fortunes)}개 로드 성공")
            else:
                print("'fortunes.txt' 파일은 있으나 내용이 비어있음")
        except FileNotFoundError:
            print("[ERROR]: 'fortunes.txt' 파일을 찾을 수 없습니다")
        except Exception as e:
            print(f"포춘쿠키 파일 로드 중 오류 발생: {e}")
    
    @commands.command(name='포춘쿠키')
    async def fortune_cookie(self, ctx):
        if not self.fortunes:
            await ctx.send("아직 포춘쿠키 반죽을 굽는 중이에요!")
            return
        
        selected_message=random.choice(self.fortunes)
        
        await ctx.send(f"🥠 {selected_message}")
    
async def setup(bot):
    await bot.add_cog(Fortunes(bot))