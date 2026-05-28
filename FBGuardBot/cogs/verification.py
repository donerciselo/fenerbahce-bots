import discord
from discord.ext import commands
import config

VERIFY_COLOR = 0x003366
WARN_COLOR = 0xFFB800

class Verification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._settings = {}

    async def _get_unverified(self, guild):
        role = discord.utils.get(guild.roles, name="Doğrulanmamış")
        if not role:
            role = await guild.create_role(
                name="Doğrulanmamış",
                color=0x666666,
                permissions=discord.Permissions.none(),
                mentionable=False,
                reason="Doğrulama sistemi için otomatik oluşturuldu"
            )
        return role

    async def _lockdown(self, guild, verify_channel):
        unverified = await self._get_unverified(guild)
        deny = discord.PermissionOverwrite(
            view_channel=False, read_messages=False, send_messages=False,
            read_message_history=False, add_reactions=False,
            create_public_threads=False, create_private_threads=False,
            send_messages_in_threads=False
        )
        allow = discord.PermissionOverwrite(
            view_channel=True, read_messages=True, send_messages=True,
            read_message_history=True, add_reactions=True
        )
        for channel in guild.channels:
            try:
                if channel.id == verify_channel.id:
                    await channel.set_permissions(unverified, overwrite=allow)
                elif isinstance(channel, (discord.TextChannel, discord.VoiceChannel, discord.ForumChannel, discord.CategoryChannel)):
                    await channel.set_permissions(unverified, overwrite=deny)
            except:
                pass

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.bot:
            return
        role = await self._get_unverified(member.guild)
        await member.add_roles(role, reason="Yeni üye - doğrulama bekliyor")

    @commands.hybrid_command(name="verify-ayarla", description="Doğrulama kanalını ve verilecek rolü ayarlar")
    @commands.has_permissions(administrator=True)
    async def verify_ayarla(self, ctx, kanal: discord.TextChannel, rol: discord.Role):
        gid = ctx.guild.id
        self._settings[gid] = {"channel": kanal.id, "role": rol.id}
        await self._lockdown(ctx.guild, kanal)
        embed = discord.Embed(title="Doğrulama Sistemi Ayarlandı", color=VERIFY_COLOR)
        embed.description = f"**Doğrulama Kanalı:** {kanal.mention}\n**Verilecek Rol:** {rol.mention}"
        embed.set_footer(text="Fenerbahçe Spor Kulübü", icon_url="https://i.imgur.com/8MDMYwD.png")
        await ctx.reply(embed=embed)

    @commands.hybrid_command(name="doğrula", description="Doğrulamayı tamamlar ve sunucuya erişim kazanırsınız")
    async def dogrula(self, ctx):
        if not ctx.guild:
            return
        gid = ctx.guild.id
        cfg = self._settings.get(gid)
        if not cfg:
            embed = discord.Embed(title="Sistem Ayarlanmamış", color=WARN_COLOR)
            embed.description = "Bu sunucuda doğrulama sistemi henüz ayarlanmamış. Yöneticinize başvurun."
            await ctx.reply(embed=embed, delete_after=10)
            return
        unverified = await self._get_unverified(ctx.guild)
        if unverified not in ctx.author.roles:
            embed = discord.Embed(title="Zaten Doğrulanmışsın", color=VERIFY_COLOR)
            embed.description = f"{ctx.author.mention}, hesabın zaten doğrulanmış durumda."
            await ctx.reply(embed=embed, delete_after=10)
            return
        if ctx.channel.id != cfg["channel"]:
            kanal = ctx.guild.get_channel(cfg["channel"])
            embed = discord.Embed(title="Yanlış Kanal", color=WARN_COLOR)
            embed.description = f"Doğrulama için lütfen {kanal.mention if kanal else 'doğrulama kanalına'} git."
            embed.set_footer(text="Sadece doğrulama kanalında işlem yapabilirsin")
            await ctx.reply(embed=embed, delete_after=10)
            return
        try:
            await ctx.author.remove_roles(unverified, reason="Doğrulama tamamlandı")
        except discord.Forbidden:
            embed = discord.Embed(title="Yetki Hatası", color=WARN_COLOR)
            embed.description = "Botun rol verme yetkisi yok. Yöneticinize başvurun."
            await ctx.reply(embed=embed, delete_after=10)
            return
        embed = discord.Embed(title="Doğrulama Başarılı", color=VERIFY_COLOR)
        embed.description = (
            f"{ctx.author.mention}, doğrulaman başarıyla tamamlandı!\n"
            f"Artık tüm kanallara erişebilirsin."
        )
        embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else discord.Embed.Empty)
        embed.set_footer(text="Fenerbahçe Spor Kulübü • Şampiyon Fenerbahçe")
        await ctx.reply(embed=embed)

    @commands.hybrid_command(name="verify-kaldır", description="Bir üyenin doğrulamasını kaldırır")
    @commands.has_permissions(administrator=True)
    async def verify_kaldir(self, ctx, uye: discord.Member):
        gid = ctx.guild.id
        cfg = self._settings.get(gid)
        if cfg:
            verify_role = ctx.guild.get_role(cfg["role"])
            if verify_role and verify_role in uye.roles:
                await uye.remove_roles(verify_role, reason="Admin tarafından doğrulama kaldırıldı")
        unverified = await self._get_unverified(ctx.guild)
        if unverified not in uye.roles:
            await uye.add_roles(unverified, reason="Admin tarafından doğrulama kaldırıldı")
        embed = discord.Embed(title="Doğrulama Kaldırıldı", color=WARN_COLOR)
        embed.description = f"{uye.mention} kullanıcısının doğrulaması kaldırıldı.\nDoğrulanmamış rolü verildi, kanal erişimi kısıtlandı."
        embed.set_footer(text="Fenerbahçe Spor Kulübü")
        await ctx.reply(embed=embed)

    @commands.hybrid_command(name="verify-kontrol", description="Sunucudaki doğrulanmamış üyeleri listeler")
    @commands.has_permissions(administrator=True)
    async def verify_kontrol(self, ctx):
        unverified = await self._get_unverified(ctx.guild)
        members = [m for m in ctx.guild.members if unverified in m.roles and not m.bot]
        embed = discord.Embed(title="Doğrulanmamış Üyeler", color=WARN_COLOR)
        if members:
            lines = [f"{m.mention} (`{m.id}`)" for m in members[:20]]
            embed.description = "\n".join(lines)
            if len(members) > 20:
                embed.set_footer(text=f"Toplam {len(members)} üye (ilk 20 gösteriliyor)")
            else:
                embed.set_footer(text=f"Toplam {len(members)} üye")
        else:
            embed.description = "Tüm üyeler doğrulanmış durumda."
            embed.color = VERIFY_COLOR
        await ctx.reply(embed=embed)


async def setup(bot):
    await bot.add_cog(Verification(bot))
