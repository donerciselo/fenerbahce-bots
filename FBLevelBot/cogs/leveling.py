import discord
from discord.ext import commands
import sqlite3
import random
import time
import config

class Leveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        import os
        db_path = os.path.join(os.environ.get("DATA_DIR", "."), "levels.sqlite")
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                xp INTEGER DEFAULT 0,
                level INTEGER DEFAULT 0,
                last_message_time REAL DEFAULT 0
            )
        ''')
        self.conn.commit()

    def get_xp_for_level(self, level):
        return 5 * (level ** 2) + 50 * level + 100

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        user_id = message.author.id
        current_time = time.time()

        self.cursor.execute("SELECT xp, level, last_message_time FROM users WHERE user_id = ?", (user_id,))
        result = self.cursor.fetchone()

        if result is None:
            self.cursor.execute("INSERT INTO users (user_id, xp, level, last_message_time) VALUES (?, ?, ?, ?)", (user_id, 0, 0, 0))
            self.conn.commit()
            xp, level, last_message_time = 0, 0, 0
        else:
            xp, level, last_message_time = result

        if current_time - last_message_time >= config.COOLDOWN_SECONDS:
            gained_xp = random.randint(config.MIN_XP, config.MAX_XP)
            new_xp = xp + gained_xp
            new_level = level

            next_level_xp = self.get_xp_for_level(new_level)

            level_up = False
            while new_xp >= next_level_xp:
                new_xp -= next_level_xp
                new_level += 1
                level_up = True
                next_level_xp = self.get_xp_for_level(new_level)

            if new_level > level:
                self.cursor.execute("UPDATE users SET xp = ?, level = ?, last_message_time = ? WHERE user_id = ?",
                                  (new_xp, new_level, current_time, user_id))
            else:
                self.cursor.execute("UPDATE users SET xp = ?, last_message_time = ? WHERE user_id = ?",
                                  (new_xp, current_time, user_id))
            self.conn.commit()
            print(f"[XP] {message.author.name} -> gained:{gained_xp} total_xp:{new_xp} level:{new_level}")

            if level_up:
                embed = discord.Embed(
                    title="🎉 Seviye Atladın!",
                    description=f"Tebrikler {message.author.mention}, **Seviye {new_level}** oldun! 💛💙",
                    color=config.GOLD
                )
                embed.set_thumbnail(url=message.author.display_avatar.url)
                await message.channel.send(embed=embed)

    @commands.command(name="rank")
    async def rank(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        self.cursor.execute("SELECT xp, level FROM users WHERE user_id = ?", (member.id,))
        result = self.cursor.fetchone()
        print(f"[RANK] {member.name} result={result}")

        if result is None:
            await ctx.send(f"{member.mention} henüz hiç XP kazanmamış.")
            return

        xp, level = result
        next_level_xp = self.get_xp_for_level(level)

        embed = discord.Embed(title=f"{member.name} - Seviye Bilgisi", color=config.NAVY)
        embed.add_field(name="Seviye", value=str(level), inline=True)
        embed.add_field(name="XP", value=f"{xp} / {next_level_xp}", inline=True)
        embed.set_thumbnail(url=member.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.command(name="avatar")
    async def avatar(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        embed = discord.Embed(title=f"{member.name}", color=config.NAVY)
        embed.set_image(url=member.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.command(name="top")
    async def leaderboard(self, ctx):
        self.cursor.execute("SELECT user_id, xp, level FROM users ORDER BY level DESC, xp DESC LIMIT 10")
        results = self.cursor.fetchall()

        if not results:
            await ctx.send("Henüz liderlik tablosunda kimse yok.")
            return

        embed = discord.Embed(title="🏆 Liderlik Tablosu", color=config.GOLD)
        
        desc = ""
        for index, (user_id, xp, level) in enumerate(results, start=1):
            member = ctx.guild.get_member(user_id)
            name = member.name if member else f"Bilinmeyen Kullanıcı ({user_id})"
            desc += f"**{index}.** {name} - Seviye: `{level}` (XP: `{xp}`)\n"

        embed.description = desc
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Leveling(bot))
