import discord
from discord.ext import commands, tasks
import requests
from bs4 import BeautifulSoup
import random
import time
from datetime import datetime


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": "https://www.google.com/",
}

EMBED_COLOR = 0x1A1A5E

DUMMY_SQUAD = [
    {"name": "Ederson", "position": "Kaleci", "age": 32, "value": "10M €"},
    {"name": "Tarık Çetin", "position": "Kaleci", "age": 29, "value": "600K €"},
    {"name": "Mert Günok", "position": "Kaleci", "age": 37, "value": "500K €"},
    {"name": "Milan Škriniar", "position": "Stoper", "age": 31, "value": "10M €"},
    {"name": "Jayden Oosterwolde", "position": "Stoper", "age": 25, "value": "20M €"},
    {"name": "Çağlar Söyüncü", "position": "Stoper", "age": 30, "value": "3.5M €"},
    {"name": "Yiğit Efe Demir", "position": "Stoper", "age": 21, "value": "6M €"},
    {"name": "Archie Brown", "position": "Sol Bek", "age": 23, "value": "12M €"},
    {"name": "Levent Mercan", "position": "Sol Bek", "age": 25, "value": "5M €"},
    {"name": "Mert Müldür", "position": "Sağ Bek", "age": 27, "value": "7M €"},
    {"name": "Nélson Semedo", "position": "Sağ Bek", "age": 32, "value": "6M €"},
    {"name": "İsmail Yüksek", "position": "Orta Saha", "age": 27, "value": "15M €"},
    {"name": "Edson Álvarez", "position": "Orta Saha", "age": 28, "value": "15M €"},
    {"name": "N'Golo Kanté", "position": "Orta Saha", "age": 35, "value": "4M €"},
    {"name": "Mattéo Guendouzi", "position": "Orta Saha", "age": 27, "value": "27M €"},
    {"name": "Fred", "position": "Orta Saha", "age": 33, "value": "4.5M €"},
    {"name": "Marco Asensio", "position": "Orta Saha", "age": 30, "value": "15M €"},
    {"name": "Talisca", "position": "Orta Saha", "age": 32, "value": "7M €"},
    {"name": "Mert Hakan Yandaş", "position": "Orta Saha", "age": 31, "value": "N/A"},
    {"name": "Kerem Aktürkoğlu", "position": "Kanat", "age": 27, "value": "20M €"},
    {"name": "Dorgeles Nene", "position": "Kanat", "age": 23, "value": "20M €"},
    {"name": "Oğuz Aydın", "position": "Kanat", "age": 25, "value": "7M €"},
    {"name": "Anthony Musaba", "position": "Kanat", "age": 25, "value": "7M €"},
    {"name": "Sidiki Chérif", "position": "Forvet", "age": 19, "value": "18M €"},
]

POSITION_MAP = {
    "Goalkeeper": "Kaleci", "GK": "Kaleci", "Kaleci": "Kaleci",
    "Centre-Back": "Stoper", "CB": "Stoper", "Stoper": "Stoper",
    "Right-Back": "Sağ Bek", "RB": "Sağ Bek", "Sağ Bek": "Sağ Bek",
    "Left-Back": "Sol Bek", "LB": "Sol Bek", "Sol Bek": "Sol Bek",
    "Defensive Midfield": "Orta Saha", "DM": "Orta Saha",
    "Central Midfield": "Orta Saha", "CM": "Orta Saha", "Orta Saha": "Orta Saha",
    "Attacking Midfield": "Orta Saha", "AM": "Orta Saha",
    "Right Winger": "Kanat", "RW": "Kanat", "Kanat": "Kanat",
    "Left Winger": "Kanat", "LW": "Kanat",
    "Second Striker": "Forvet", "SS": "Forvet",
    "Centre-Forward": "Forvet", "CF": "Forvet", "Forvet": "Forvet",
}

FORMATION_4231 = {
    "Kaleci": 1,
    "Stoper": 2,
    "Sağ Bek": 1,
    "Sol Bek": 1,
    "Defansif Orta Saha": 2,
    "Ofansif Orta Saha": 1,
    "Kanat": 2,
    "Forvet": 1,
}

FORMATION_433 = {
    "Kaleci": 1,
    "Stoper": 2,
    "Sağ Bek": 1,
    "Sol Bek": 1,
    "Orta Saha": 3,
    "Kanat": 2,
    "Forvet": 1,
}


class KadroCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cache = {}
        self.cache_time = 0
        self.cache_duration = 86400
        self.dummy_mode = False

    def _get_cached_squad(self, team_url):
        now = time.time()
        if team_url in self.cache and (now - self.cache_time) < self.cache_duration:
            return self.cache[team_url]
        return None

    def _set_cached_squad(self, team_url, squad):
        self.cache[team_url] = squad
        self.cache_time = time.time()

    def _normalize_position(self, raw_position):
        for key, value in POSITION_MAP.items():
            if key.lower() in raw_position.lower():
                return value
        return "Orta Saha"

    def _parse_market_value(self, value_str):
        if not value_str or value_str == "-":
            return "N/A"
        value_str = value_str.strip()
        if "€" in value_str:
            return value_str
        return f"{value_str} €"

    def scrape_squad(self, url):
        cached = self._get_cached_squad(url)
        if cached:
            return cached

        try:
            response = requests.get(url, headers=HEADERS, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "lxml")

            squad = []
            table = soup.select_one("table.items")

            if not table:
                raise Exception("Kadro tablosu bulunamadı")

            rows = table.select("tbody tr.odd, tbody tr.even")

            for row in rows:
                try:
                    name_cell = row.select_one("td.hauptlink a")
                    if not name_cell:
                        continue
                    name = name_cell.get_text(strip=True)

                    pos_cell = row.select_one("td.pos")
                    raw_pos = pos_cell.get_text(strip=True) if pos_cell else "Orta Saha"
                    position = self._normalize_position(raw_pos)

                    age_cell = row.select("td.zentriert")
                    age = "N/A"
                    for cell in age_cell:
                        text = cell.get_text(strip=True)
                        if text.isdigit() and 15 <= int(text) <= 45:
                            age = int(text)
                            break

                    value_cell = row.select_one("td.rechts.hauptlink")
                    value = self._parse_market_value(
                        value_cell.get_text(strip=True) if value_cell else ""
                    )

                    squad.append({
                        "name": name,
                        "position": position,
                        "age": age,
                        "value": value,
                    })
                except Exception:
                    continue

            if not squad:
                raise Exception("Kadro verisi ayrıştırılamadı")

            self._set_cached_squad(url, squad)
            self.dummy_mode = False
            return squad

        except Exception as e:
            print(f"Scraping hatası: {e}")
            self.dummy_mode = True
            return DUMMY_SQUAD

    def scrape_opponent(self, team_name):
        search_name = team_name.lower().replace(" ", "-")
        search_name = search_name.replace("ş", "s").replace("ö", "o").replace("ü", "u").replace("ğ", "g").replace("ı", "i").replace("ç", "c")

        search_url = f"https://www.transfermarkt.com/schnellsuche/ergebnis/schnellsuche?query={team_name}"

        try:
            response = requests.get(search_url, headers=HEADERS, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "lxml")

            link = soup.select_one("td.hauptlink a")
            if not link:
                return None

            team_url = "https://www.transfermarkt.com" + link["href"]
            team_url = team_url.replace("/profil/", "/startseite/")

            cached = self._get_cached_squad(team_url)
            if cached:
                return cached

            response = requests.get(team_url, headers=HEADERS, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "lxml")

            squad = []
            table = soup.select_one("table.items")

            if not table:
                return None

            rows = table.select("tbody tr.odd, tbody tr.even")

            for row in rows:
                try:
                    name_cell = row.select_one("td.hauptlink a")
                    if not name_cell:
                        continue
                    name = name_cell.get_text(strip=True)

                    pos_cell = row.select_one("td.pos")
                    raw_pos = pos_cell.get_text(strip=True) if pos_cell else "Orta Saha"
                    position = self._normalize_position(raw_pos)

                    age_cell = row.select("td.zentriert")
                    age = "N/A"
                    for cell in age_cell:
                        text = cell.get_text(strip=True)
                        if text.isdigit() and 15 <= int(text) <= 45:
                            age = int(text)
                            break

                    value_cell = row.select_one("td.rechts.hauptlink")
                    value = self._parse_market_value(
                        value_cell.get_text(strip=True) if value_cell else ""
                    )

                    squad.append({
                        "name": name,
                        "position": position,
                        "age": age,
                        "value": value,
                    })
                except Exception:
                    continue

            if squad:
                self._set_cached_squad(team_url, squad)
            return squad if squad else None

        except Exception as e:
            print(f"Rakip scraping hatası: {e}")
            return None

    def _get_position_players(self, squad, position):
        return [p for p in squad if p["position"] == position]

    def _build_formation(self, squad, formation_type="random"):
        if formation_type == "random":
            formation_type = random.choice(["4-2-3-1", "4-3-3"])

        result = {}
        used = []

        goalkeepers = self._get_position_players(squad, "Kaleci")
        if goalkeepers:
            gk = random.choice(goalkeepers)
            result["Kaleci"] = gk
            used.append(gk["name"])

        if formation_type == "4-2-3-1":
            defenders = [p for p in squad if p["position"] in ["Stoper", "Sağ Bek", "Sol Bek"] and p["name"] not in used]
            if len(defenders) >= 4:
                backs = [p for p in defenders if p["position"] in ["Sağ Bek", "Sol Bek"]]
                centers = [p for p in defenders if p["position"] == "Stoper"]

                selected_def = []
                if backs:
                    rb = random.choice([p for p in backs if p["position"] == "Sağ Bek"] or backs)
                    selected_def.append(("Sağ Bek", rb))
                    used.append(rb["name"])

                    lb_candidates = [p for p in backs if p["position"] == "Sol Bek" and p["name"] not in used]
                    if lb_candidates:
                        lb = random.choice(lb_candidates)
                        selected_def.append(("Sol Bek", lb))
                        used.append(lb["name"])

                available_cb = [p for p in centers if p["name"] not in used]
                if len(available_cb) >= 2:
                    cbs = random.sample(available_cb, 2)
                    for cb in cbs:
                        selected_def.append(("Stoper", cb))
                        used.append(cb["name"])

                result["Defans"] = selected_def

            midfielders = [p for p in squad if p["position"] == "Orta Saha" and p["name"] not in used]
            if len(midfielders) >= 3:
                dm = random.sample(midfielders, 2)
                result["Defansif Orta Saha"] = [(p["name"], p) for p in dm]
                used.extend([p["name"] for p in dm])

                om_candidates = [p for p in midfielders if p["name"] not in used]
                if om_candidates:
                    om = random.choice(om_candidates)
                    result["Ofansif Orta Saha"] = om
                    used.append(om["name"])

            wingers = [p for p in squad if p["position"] == "Kanat" and p["name"] not in used]
            if len(wingers) >= 2:
                selected_w = random.sample(wingers, 2)
                result["Kanatlar"] = selected_w
                used.extend([p["name"] for p in selected_w])

            strikers = [p for p in squad if p["position"] == "Forvet" and p["name"] not in used]
            if strikers:
                result["Forvet"] = random.choice(strikers)
                used.append(result["Forvet"]["name"])

        else:
            defenders = [p for p in squad if p["position"] in ["Stoper", "Sağ Bek", "Sol Bek"] and p["name"] not in used]
            if len(defenders) >= 4:
                backs = [p for p in defenders if p["position"] in ["Sağ Bek", "Sol Bek"]]
                centers = [p for p in defenders if p["position"] == "Stoper"]

                selected_def = []
                if backs:
                    rb = random.choice([p for p in backs if p["position"] == "Sağ Bek"] or backs)
                    selected_def.append(("Sağ Bek", rb))
                    used.append(rb["name"])

                    lb_candidates = [p for p in backs if p["position"] == "Sol Bek" and p["name"] not in used]
                    if lb_candidates:
                        lb = random.choice(lb_candidates)
                        selected_def.append(("Sol Bek", lb))
                        used.append(lb["name"])

                available_cb = [p for p in centers if p["name"] not in used]
                if len(available_cb) >= 2:
                    cbs = random.sample(available_cb, 2)
                    for cb in cbs:
                        selected_def.append(("Stoper", cb))
                        used.append(cb["name"])

                result["Defans"] = selected_def

            midfielders = [p for p in squad if p["position"] == "Orta Saha" and p["name"] not in used]
            if len(midfielders) >= 3:
                selected_mf = random.sample(midfielders, 3)
                result["Orta Saha"] = selected_mf
                used.extend([p["name"] for p in selected_mf])

            wingers = [p for p in squad if p["position"] == "Kanat" and p["name"] not in used]
            if len(wingers) >= 2:
                selected_w = random.sample(wingers, 2)
                result["Kanatlar"] = selected_w
                used.extend([p["name"] for p in selected_w])

            strikers = [p for p in squad if p["position"] == "Forvet" and p["name"] not in used]
            if strikers:
                result["Forvet"] = random.choice(strikers)
                used.append(result["Forvet"]["name"])

        result["formation"] = formation_type
        return result

    def _find_key_player(self, squad):
        max_val = 0
        key_player = None
        for p in squad:
            val_str = p["value"].replace("M €", "").replace("€", "").replace(",", ".").strip()
            try:
                val = float(val_str)
                if val > max_val:
                    max_val = val
                    key_player = p
            except ValueError:
                continue
        return key_player

    @commands.command(name="kadro")
    async def show_squad(self, ctx):
        url = "https://www.transfermarkt.com/fenerbahce-istanbul/startseite/verein/36"

        loading_msg = await ctx.send("⚽ Kadro yükleniyor...")

        squad = self.scrape_squad(url)

        embed = discord.Embed(
            title="🟡🔵 Fenerbahçe Güncel Kadro",
            description="Transfermarkt verilerine göre güncel kadro",
            color=EMBED_COLOR,
            timestamp=datetime.now(),
        )

        positions = {"Kaleci": [], "Stoper": [], "Sağ Bek": [], "Sol Bek": [], "Orta Saha": [], "Kanat": [], "Forvet": []}
        for player in squad:
            pos = player["position"]
            if pos in positions:
                positions[pos].append(player)

        pos_emojis = {
            "Kaleci": "🧤", "Stoper": "🛡️", "Sağ Bek": "➡️",
            "Sol Bek": "⬅️", "Orta Saha": "⚙️", "Kanat": "💨", "Forvet": "⚡",
        }

        for pos, players in positions.items():
            if players:
                player_list = []
                for p in players:
                    age_str = f"{p['age']}" if p['age'] != "N/A" else "?"
                    player_list.append(f"**{p['name']}** | {age_str} yaş | {p['value']}")
                embed.add_field(
                    name=f"{pos_emojis.get(pos, '⚽')} {pos} ({len(players)})",
                    value="\n".join(player_list),
                    inline=False,
                )

        if self.dummy_mode:
            embed.set_footer(text="⚠️ Canlı veri alınamadı — örnek kadro gösteriliyor")
        else:
            embed.set_footer(text="Veri Transfermarkt'tan çekilmiştir")

        embed.set_thumbnail(url="https://images.fenerbahce.org.tr/images/kulup/logo.png")

        await loading_msg.edit(content=None, embed=embed)

    @commands.command(name="taktik")
    async def tactic(self, ctx):
        url = "https://www.transfermarkt.com/fenerbahce-istanbul/startseite/verein/36"

        loading_msg = await ctx.send("🧠 Taktik oluşturuluyor...")

        squad = self.scrape_squad(url)

        if len(squad) < 11:
            await loading_msg.edit(content="❌ Yeterli oyuncu bulunamadı.")
            return

        formation = self._build_formation(squad)
        key_player = self._find_key_player(squad)
        formation_name = formation["formation"]

        embed = discord.Embed(
            title=f"🧠 AI Taktik: {formation_name}",
            description=f"Fenerbahçe için önerilen ideal 11",
            color=EMBED_COLOR,
            timestamp=datetime.now(),
        )

        if "Kaleci" in formation:
            gk = formation["Kaleci"]
            embed.add_field(
                name="🧤 Kaleci",
                value=f"**{gk['name']}** | {gk['age']} yaş | {gk['value']}",
                inline=False,
            )

        if "Defans" in formation:
            def_lines = []
            for pos_name, player in formation["Defans"]:
                def_lines.append(f"**{player['name']}** ({pos_name}) | {player['age']} yaş | {player['value']}")
            embed.add_field(name="🛡️ Defans", value="\n".join(def_lines), inline=False)

        if formation_name == "4-2-3-1":
            if "Defansif Orta Saha" in formation:
                dm_lines = []
                for name, player in formation["Defansif Orta Saha"]:
                    dm_lines.append(f"**{player['name']}** | {player['age']} yaş | {player['value']}")
                embed.add_field(name="⚙️ Defansif Orta Saha", value="\n".join(dm_lines), inline=True)

            if "Ofansif Orta Saha" in formation:
                om = formation["Ofansif Orta Saha"]
                embed.add_field(
                    name="🎯 Ofansif Orta Saha",
                    value=f"**{om['name']}** | {om['age']} yaş | {om['value']}",
                    inline=True,
                )
        else:
            if "Orta Saha" in formation:
                mf_lines = []
                for p in formation["Orta Saha"]:
                    mf_lines.append(f"**{p['name']}** | {p['age']} yaş | {p['value']}")
                embed.add_field(name="⚙️ Orta Saha", value="\n".join(mf_lines), inline=False)

        if "Kanatlar" in formation:
            wing_lines = []
            for p in formation["Kanatlar"]:
                wing_lines.append(f"**{p['name']}** | {p['age']} yaş | {p['value']}")
            embed.add_field(name="💨 Kanatlar", value="\n".join(wing_lines), inline=True)

        if "Forvet" in formation:
            fw = formation["Forvet"]
            embed.add_field(
                name="⚡ Forvet",
                value=f"**{fw['name']}** | {fw['age']} yaş | {fw['value']}",
                inline=True,
            )

        if key_player:
            embed.add_field(
                name="⭐ Kilit Oyuncu",
                value=f"**{key_player['name']}** — Piyasa değeri: {key_player['value']}",
                inline=False,
            )

        embed.set_footer(text=f"Diziliş: {formation_name} | Rastgele oluşturuldu")
        embed.set_thumbnail(url="https://images.fenerbahce.org.tr/images/kulup/logo.png")

        await loading_msg.edit(content=None, embed=embed)

    @commands.command(name="rakip")
    async def opponent(self, ctx, *, team_name: str = None):
        if not team_name:
            await ctx.send("❌ Lütfen bir takım adı girin. Örnek: `+rakip Galatasaray`")
            return

        loading_msg = await ctx.send(f"🔍 {team_name} analiz ediliyor...")

        opponent_squad = self.scrape_opponent(team_name)

        if not opponent_squad:
            await loading_msg.edit(content=f"❌ **{team_name}** için kadro verisi bulunamadı.")
            return

        fener_squad = self.scrape_squad("https://www.transfermarkt.com/fenerbahce-istanbul/startseite/verein/36")

        embed = discord.Embed(
            title=f"📊 Rakip Analizi: {team_name.title()}",
            description=f"Transfermarkt verilerine göre karşılaştırmalı analiz",
            color=EMBED_COLOR,
            timestamp=datetime.now(),
        )

        fener_avg = self._calc_avg_age(fener_squad)
        opp_avg = self._calc_avg_age(opponent_squad)

        fener_total = self._calc_total_value(fener_squad)
        opp_total = self._calc_total_value(opponent_squad)

        fener_count = len(fener_squad)
        opp_count = len(opponent_squad)

        embed.add_field(
            name="📋 Kadro Bilgisi",
            value=(
                f"**Fenerbahçe:** {fener_count} oyuncu\n"
                f"**{team_name.title()}:** {opp_count} oyuncu"
            ),
            inline=True,
        )

        embed.add_field(
            name="📅 Ortalama Yaş",
            value=(
                f"**Fenerbahçe:** {fener_avg}\n"
                f"**{team_name.title()}:** {opp_avg}"
            ),
            inline=True,
        )

        embed.add_field(
            name="💰 Toplam Piyasa Değeri",
            value=(
                f"**Fenerbahçe:** {fener_total}\n"
                f"**{team_name.title()}:** {opp_total}"
            ),
            inline=True,
        )

        pos_emojis = {
            "Kaleci": "🧤", "Stoper": "🛡️", "Sağ Bek": "➡️",
            "Sol Bek": "⬅️", "Orta Saha": "⚙️", "Kanat": "💨", "Forvet": "⚡",
        }

        opp_positions = {"Kaleci": [], "Stoper": [], "Sağ Bek": [], "Sol Bek": [], "Orta Saha": [], "Kanat": [], "Forvet": []}
        for player in opponent_squad:
            pos = player["position"]
            if pos in opp_positions:
                opp_positions[pos].append(player)

        for pos, players in opp_positions.items():
            if players:
                player_list = []
                for p in players[:3]:
                    age_str = f"{p['age']}" if p['age'] != "N/A" else "?"
                    player_list.append(f"**{p['name']}** | {age_str} yaş | {p['value']}")
                if len(players) > 3:
                    player_list.append(f"*+{len(players)-3} diğer...*")
                embed.add_field(
                    name=f"{pos_emojis.get(pos, '⚽')} {pos}",
                    value="\n".join(player_list),
                    inline=True,
                )

        opp_key = self._find_key_player(opponent_squad)
        fener_key = self._find_key_player(fener_squad)

        if opp_key and fener_key:
            embed.add_field(
                name="⭐ Kilit Oyuncu Karşılaştırması",
                value=(
                    f"**Fenerbahçe:** {fener_key['name']} ({fener_key['value']})\n"
                    f"**{team_name.title()}:** {opp_key['name']} ({opp_key['value']})"
                ),
                inline=False,
            )

        embed.set_footer(text="Veri Transfermarkt'tan çekilmiştir")
        embed.set_thumbnail(url="https://images.fenerbahce.org.tr/images/kulup/logo.png")

        await loading_msg.edit(content=None, embed=embed)

    def _calc_avg_age(self, squad):
        ages = [p["age"] for p in squad if isinstance(p["age"], int)]
        if not ages:
            return "N/A"
        return f"{sum(ages)/len(ages):.1f}"

    def _calc_total_value(self, squad):
        total = 0
        for p in squad:
            val_str = p["value"].replace("M €", "").replace("€", "").replace(",", ".").strip()
            try:
                total += float(val_str)
            except ValueError:
                continue
        if total >= 1000:
            return f"{total/1000:.2f}B €"
        return f"{total:.1f}M €"


async def setup(bot):
    await bot.add_cog(KadroCog(bot))
