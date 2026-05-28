import discord
from discord.ext import commands
import sqlite3
import random

COLOR_FB_NAVY = 0x072A6C
COLOR_FB_YELLOW = 0xFEDB00

class AITahmin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        import os
        db_path = os.path.join(os.environ.get("DATA_DIR", "."), "tahminler.sqlite")
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                opponent TEXT,
                date TEXT,
                ai_score TEXT,
                ai_confidence INTEGER,
                ai_form TEXT,
                derby TEXT,
                active INTEGER DEFAULT 1
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS predictions (
                match_id INTEGER,
                user_id INTEGER,
                prediction TEXT,
                PRIMARY KEY (match_id, user_id)
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                score INTEGER DEFAULT 0
            )
        ''')
        self.conn.commit()

    @commands.command(name="mac-ekle")
    @commands.has_permissions(administrator=True)
    async def mac_ekle(self, ctx, opponent: str, date: str):
        self.cursor.execute("UPDATE matches SET active = 0 WHERE active = 1")
        
        form = "-".join(random.choices(["G", "B", "M"], weights=[60, 20, 20], k=5))
        win_ratio = form.count("G") * 20
        derby = "⚠️ Yüksek" if opponent.lower() in ["galatasaray", "beşiktaş", "trabzonspor"] else "Normal"
        
        fb_score = random.randint(1, 4)
        opp_score = random.randint(0, 2)
        ai_score = f"{fb_score}-{opp_score}"
        confidence = random.randint(65, 95)
        
        self.cursor.execute('''
            INSERT INTO matches (opponent, date, ai_score, ai_confidence, ai_form, derby)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (opponent, date, ai_score, confidence, form, derby))
        self.conn.commit()
        
        embed = discord.Embed(title="🤖 FENERBAHÇE AI MAÇ ANALİZİ", color=COLOR_FB_NAVY)
        embed.add_field(name="Rakip", value=opponent, inline=True)
        embed.add_field(name="Tarih", value=date, inline=True)
        embed.add_field(name="Son 5 Maç", value=f"{form} (Form: %{win_ratio})", inline=False)
        embed.add_field(name="Derbi Faktörü", value=derby, inline=True)
        embed.add_field(name="Sakat/Eksik", value=f"{random.randint(0,4)} oyuncu", inline=True)
        embed.add_field(name="Tahmini Skor", value=f"{ai_score} (Güven: %{confidence})", inline=False)
        embed.set_footer(text="Fenerbahçe AI Tahmin Sistemi")
        
        await ctx.send(embed=embed)

    @commands.command(name="ai-tahmin")
    async def ai_tahmin(self, ctx):
        self.cursor.execute("SELECT opponent, date, ai_score, ai_confidence, ai_form, derby FROM matches WHERE active = 1")
        match = self.cursor.fetchone()
        
        if not match:
            await ctx.send("Şu an aktif bir maç bulunmuyor.")
            return
            
        opponent, date, ai_score, confidence, form, derby = match
        win_ratio = form.count("G") * 20
        
        embed = discord.Embed(title="🤖 FENERBAHÇE AI MAÇ ANALİZİ", color=COLOR_FB_YELLOW)
        embed.add_field(name="Rakip", value=opponent, inline=True)
        embed.add_field(name="Tarih", value=date, inline=True)
        embed.add_field(name="Son 5 Maç", value=f"{form} (Form: %{win_ratio})", inline=False)
        embed.add_field(name="Derbi Faktörü", value=derby, inline=True)
        embed.add_field(name="Tahmini Skor", value=f"{ai_score} (Güven: %{confidence})", inline=False)
        
        await ctx.send(embed=embed)

    @commands.command(name="ai-analiz")
    async def ai_analiz(self, ctx, opponent: str):
        embed = discord.Embed(title=f"📊 {opponent.upper()} DETAYLI AI ANALİZİ", color=COLOR_FB_NAVY)
        embed.add_field(name="Hücum Gücü", value=f"%{random.randint(50, 95)}", inline=True)
        embed.add_field(name="Savunma Gücü", value=f"%{random.randint(40, 90)}", inline=True)
        embed.add_field(name="Topla Oynama (Ort)", value=f"%{random.randint(40, 65)}", inline=True)
        embed.add_field(name="Taktik Zafiyet", value=random.choice(["Kanat Savunması", "Duran Toplar", "Kontra Atak", "Merkez Orta Saha"]), inline=False)
        embed.add_field(name="Öne Çıkan Oyuncu", value="Sistem analizi sürüyor...", inline=False)
        embed.set_footer(text="Bu veriler yapay zeka tarafından simüle edilmiştir.")
        await ctx.send(embed=embed)

    @commands.command(name="tahmin")
    async def tahmin(self, ctx, score: str):
        if "-" not in score:
            await ctx.send("Lütfen skoru 'X-Y' formatında girin. (Örn: 2-1)")
            return
            
        self.cursor.execute("SELECT id, opponent FROM matches WHERE active = 1")
        match = self.cursor.fetchone()
        
        if not match:
            await ctx.send("Şu an tahmin yapılabilecek aktif bir maç yok.")
            return
            
        match_id, opponent = match
        user_id = ctx.author.id
        
        self.cursor.execute('''
            INSERT INTO predictions (match_id, user_id, prediction)
            VALUES (?, ?, ?)
            ON CONFLICT(match_id, user_id) DO UPDATE SET prediction = ?
        ''', (match_id, user_id, score, score))
        self.conn.commit()
        
        await ctx.send(f"✅ Tahmininiz kaydedildi: Fenerbahçe {score.split('-')[0]} - {score.split('-')[1]} {opponent}")

    @commands.command(name="tahminler")
    async def tahminler(self, ctx):
        self.cursor.execute("SELECT id, opponent FROM matches WHERE active = 1")
        match = self.cursor.fetchone()
        
        if not match:
            await ctx.send("Şu an aktif bir maç yok.")
            return
            
        match_id, opponent = match
        self.cursor.execute("SELECT user_id, prediction FROM predictions WHERE match_id = ?", (match_id,))
        preds = self.cursor.fetchall()
        
        if not preds:
            await ctx.send("Henüz kimse tahmin yapmamış.")
            return
            
        desc = ""
        for user_id, prediction in preds:
            member = ctx.guild.get_member(user_id)
            name = member.name if member else f"Kullanıcı ({user_id})"
            desc += f"**{name}:** {prediction}\n"
            
        embed = discord.Embed(title=f"📋 {opponent} Maçı Tahminleri", description=desc, color=COLOR_FB_YELLOW)
        await ctx.send(embed=embed)

    @commands.command(name="sonuc")
    @commands.has_permissions(administrator=True)
    async def sonuc(self, ctx, score: str):
        if "-" not in score:
            await ctx.send("Lütfen skoru 'X-Y' formatında girin. (Örn: 2-1)")
            return
            
        self.cursor.execute("SELECT id, opponent FROM matches WHERE active = 1")
        match = self.cursor.fetchone()
        
        if not match:
            await ctx.send("Sonuçlandırılabilecek aktif bir maç yok.")
            return
            
        match_id, opponent = match
        
        fb_real, opp_real = map(int, score.split("-"))
        real_diff = fb_real - opp_real
        
        self.cursor.execute("SELECT user_id, prediction FROM predictions WHERE match_id = ?", (match_id,))
        preds = self.cursor.fetchall()
        
        for user_id, prediction in preds:
            try:
                fb_pred, opp_pred = map(int, prediction.split("-"))
                pred_diff = fb_pred - opp_pred
                
                points = 0
                if fb_pred == fb_real and opp_pred == opp_real:
                    points = 10
                elif (real_diff > 0 and pred_diff > 0) or (real_diff < 0 and pred_diff < 0) or (real_diff == 0 and pred_diff == 0):
                    points = 5
                    
                if points > 0:
                    self.cursor.execute("SELECT score FROM users WHERE user_id = ?", (user_id,))
                    user_data = self.cursor.fetchone()
                    
                    if user_data is None:
                        self.cursor.execute("INSERT INTO users (user_id, score) VALUES (?, ?)", (user_id, points))
                    else:
                        new_score = user_data[0] + points
                        self.cursor.execute("UPDATE users SET score = ? WHERE user_id = ?", (new_score, user_id))
            except ValueError:
                continue
                
        self.cursor.execute("UPDATE matches SET active = 0 WHERE id = ?", (match_id,))
        self.conn.commit()
        
        await ctx.send(f"🏁 Maç sonuçlandırıldı! {opponent} maçı skoru: {score}. Puanlar dağıtıldı.")

    @commands.command(name="puan")
    async def puan(self, ctx):
        self.cursor.execute("SELECT score FROM users WHERE user_id = ?", (ctx.author.id,))
        result = self.cursor.fetchone()
        
        score = result[0] if result else 0
        embed = discord.Embed(title="👤 Puan Durumu", description=f"{ctx.author.mention}, güncel puanınız: **{score}**", color=COLOR_FB_NAVY)
        await ctx.send(embed=embed)

    @commands.command(name="lider")
    async def lider(self, ctx):
        self.cursor.execute("SELECT user_id, score FROM users ORDER BY score DESC LIMIT 10")
        results = self.cursor.fetchall()
        
        if not results:
            await ctx.send("Henüz kimsenin puanı yok.")
            return
            
        desc = ""
        for index, (user_id, score) in enumerate(results, start=1):
            member = ctx.guild.get_member(user_id)
            name = member.name if member else f"Bilinmeyen ({user_id})"
            desc += f"**{index}.** {name} - {score} Puan\n"
            
        embed = discord.Embed(title="🏆 Tahmin Liderlik Tablosu", description=desc, color=COLOR_FB_YELLOW)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(AITahmin(bot))
