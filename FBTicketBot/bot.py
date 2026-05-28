import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import chat_exporter
import io
import asyncio
import config

load_dotenv()

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Ticket Aç", style=discord.ButtonStyle.primary, emoji="🎫", custom_id="open_ticket")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        ticket_name = f"ticket-{interaction.user.name.lower()}"
        
        # Zaten açık ticket var mı kontrolü
        existing_channel = discord.utils.get(interaction.guild.text_channels, name=ticket_name)
        if existing_channel:
            return await interaction.response.send_message(f"Zaten açık bir destek talebiniz var: {existing_channel.mention}", ephemeral=True)

        # İzinleri ayarla
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            interaction.guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, manage_channels=True)
        }

        # Yetkili rolleri ekle
        for role_id in config.STAFF_ROLES:
            try:
                role = interaction.guild.get_role(int(role_id))
                if role:
                    overwrites[role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
            except ValueError:
                pass

        category = None
        if config.TICKET_CATEGORY and config.TICKET_CATEGORY != "Kategori_ID_Gireceksiniz":
            try:
                category = interaction.guild.get_channel(int(config.TICKET_CATEGORY))
            except ValueError:
                pass

        try:
            ticket_channel = await interaction.guild.create_text_channel(
                name=ticket_name,
                category=category,
                overwrites=overwrites
            )

            embed = discord.Embed(
                title="Destek Talebi",
                description=f"Merhaba {interaction.user.mention}, yetkililerimiz en kısa sürede sizinle ilgilenecektir.\nLütfen sorununuzu detaylı bir şekilde açıklayın.\n\nTalebi sonlandırmak için aşağıdaki \"Kapat\" butonuna tıklayabilirsiniz.",
                color=discord.Color.from_str("#001e61")
            )

            await ticket_channel.send(content=f"{interaction.user.mention}", embed=embed, view=CloseTicketView())
            await interaction.response.send_message(f"Destek talebiniz oluşturuldu: {ticket_channel.mention}", ephemeral=True)
        except Exception as e:
            print(e)
            await interaction.response.send_message("Ticket oluşturulurken bir hata oluştu. Yetkilerimi kontrol edin.", ephemeral=True)


class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Kapat", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Ticket kapatılıyor, transcript hazırlanıyor...")

        try:
            # Transcript oluştur
            transcript = await chat_exporter.export(interaction.channel)
            transcript_file = discord.File(io.BytesIO(transcript.encode()), filename=f"{interaction.channel.name}-transcript.html")

            # Log kanalına gönder
            if config.LOG_CHANNEL and config.LOG_CHANNEL != "Log_Kanal_ID_Gireceksiniz":
                try:
                    log_channel = interaction.guild.get_channel(int(config.LOG_CHANNEL))
                    if log_channel:
                        embed = discord.Embed(title="Ticket Kapatıldı", color=discord.Color.red())
                        embed.add_field(name="Kapatan", value=f"{interaction.user.mention} ({interaction.user.name})", inline=True)
                        embed.add_field(name="Kanal", value=interaction.channel.name, inline=True)
                        await log_channel.send(embed=embed, file=transcript_file)
                except ValueError:
                    pass

            # Kanalı sil
            await asyncio.sleep(3)
            await interaction.channel.delete()

        except Exception as e:
            print(e)
            try:
                await interaction.edit_original_response(content="Kapatma işlemi sırasında bir hata oluştu.")
            except:
                pass


class TicketBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix=config.PREFIX, intents=intents)

    async def setup_hook(self):
        self.add_view(TicketView())
        self.add_view(CloseTicketView())

bot = TicketBot()

@bot.event
async def on_ready():
    print(f'Bot giriş yaptı: {bot.user}')

@bot.command()
@commands.has_permissions(administrator=True)
async def kurulum(ctx):
    embed = discord.Embed(
        title="💛💙 Fenerbahçe Destek Sistemi",
        description="Destek talebi (ticket) oluşturmak için aşağıdaki butona tıklayabilirsiniz.",
        color=discord.Color.from_str("#001e61")
    )
    await ctx.send(embed=embed, view=TicketView())
    try:
        await ctx.message.delete()
    except:
        pass

@kurulum.error
async def kurulum_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("Bu komutu kullanmak için `Yönetici` yetkisine sahip olmalısın.")

if __name__ == "__main__":
    token = os.getenv("TICKET_TOKEN")
    if not token:
        print("TOKEN bulunamadı! Lütfen .env dosyasını kontrol edin.")
    else:
        # Eğer botu Türkiye'de çalıştırıyorsanız ve DNS/WARP kullanmak istemiyorsanız
        # bir proxy belirtebilirsiniz. Örnek: bot.run(token, proxy="http://127.0.0.1:8080")
        bot.run(token)
