import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from playwright.async_api import async_playwright, Playwright, Browser, Page

class Nyehuing(commands.Cog):
    
    def __init__(self, bot):
        self.bot=bot
        self.playwright: Playwright | None=None
        self.browser: Browser | None=None
        self.page: Page | None=None
        
    async def cog_load(self):
        print("Nyehuing Cog: PlayWright를 시작합니다")
        try:
            self.playwright=await async_playwright().start()
            self.browser=await self.playwright.chromium.launch()
            
            self.page=await self.browser.new_page()
            
            await self.page.goto("https://beepman.github.io/nyehuing/")
            print("Nyehuing Cog: 페이지 준비 완료")
        except Exception as e:
            print(f"Nyehuing Cog: PlayWright 로드 실패: {e}")
    
    async def cog_unload(self):
        print("Nyehuing Cog: PlayWright를 종료합니다")
        try:
            if self.page:
                await self.page.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            print("Nyehuing Cog: PlayWright 종료")
        except Exception as e:
            print(f"Nyehuing Cog: PlayWright 종료  중 오류: {e}")
    
    @app_commands.command(name="녜힁", description="녜힁제조기")
    @app_commands.describe(choice="버튼을 선택하세요(2글자, 3글자, 6글자)")
    @app_commands.choices(choice=[
        app_commands.Choice(name="2글자", value=2),
        app_commands.Choice(name="3글자", value=3),
        app_commands.Choice(name="더욱 긴!", value=6)
    ])
    async def nyehuing(self, interaction: discord.Interaction, choice: app_commands.Choice[int]):
        
        if not self.page:
            await interaction.response.send_message("녜힁제조기 준비중...", ephemeral=True)
            return
            
        selected_value=choice.value
        
        await interaction.response.defer()
        
        try:
            if selected_value==2:
                await self.page.get_by_role("button", name="Click Me!").click()
            elif selected_value==3:
                await self.page.get_by_role("button", name="세글자").click()
            elif selected_value==6:
                await self.page.get_by_role("button", name="더욱 긴 녜힁").click()
            
            result_locator=self.page.locator("#demo")
            
            result_text=await result_locator.inner_text()
            
            await interaction.followup.send(result_text)
        except Exception as e:
            await interaction.response.send_message(f"녜힁 제조 실패: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Nyehuing(bot))
        
        
# 핵심 함수 가이드
# page.goto(url): 페이지 접속하기
# page.fill(selector, text): 입력창에 텍스트 채우기 (예: page.fill("#input-text", "안녕"))
# page.click(selector): 버튼 클릭하기 (예: page.click("#convert-button"))
# page.input_value(selector): 결과창의 값 가져오기 (예: result = await page.input_value("#output-text"))
# page.close(): 페이지 닫기