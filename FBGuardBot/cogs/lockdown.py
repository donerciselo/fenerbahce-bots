import discord
from discord.ext import commands
import config
import datetime

class Lockdown(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.locked_channels = set()
        self.guild_locked = set()

    @commands.hybrid_command(name="lock", description="Kanalı kilitler")
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx, kanal: discord.TextChannel = None):
        ch = kanal or ctx.channel
        try:
            overwrite = ch.overwrites_for(ctx.guild.default_role)
            overwrite.send_messages = False
            await ch.set_permissions(ctx.guild.default_role, overwrite=overwrite)
            self.locked_channels.add(ch.id)
            embed = discord.Embed(title="Kanal Kilitlendi", color=config.COLOR_WARNING)
            embed.description = f"{ch.mention} kilitlendi."
            await ctx.reply(embed=embed)
        except Exception as e:
            embed = discord.Embed(title="Hata", color=config.COLOR_CRITICAL)
            embed.description = str(e)
            await ctx.reply(embed=embed)

    @commands.hybrid_command(name="unlock", description="Kanalın kilidini açar")
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx, kanal: discord.TextChannel = None):
        ch = kanal or ctx.channel
        try:
            overwrite = ch.overwrites_for(ctx.guild.default_role)
            overwrite.send_messages = None
            await ch.set_permissions(ctx.guild.default_role, overwrite=overwrite)
            self.locked_channels.discard(ch.id)
            embed = discord.Embed(title="Kanal Kilidi Açıldı", color=config.COLOR_NORMAL)
            embed.description = f"{ch.mention} kilidi açıldı."
            await ctx.reply(embed=embed)
        except Exception as e:
            embed = discord.Embed(title="Hata", color=config.COLOR_CRITICAL)
            embed.description = str(e)
            await ctx.reply(embed=embed)

    @commands.hybrid_command(name="lockall", description="Tüm kanalları kilitler")
    @commands.has_permissions(administrator=True)
    async def lockall(self, ctx):
        embed = discord.Embed(title="Tüm Kanallar Kilitleniyor...", color=config.COLOR_CRITICAL)
        msg = await ctx.reply(embed=embed)
        count = 0
        for ch in ctx.guild.text_channels:
            try:
                overwrite = ch.overwrites_for(ctx.guild.default_role)
                overwrite.send_messages = False
                await ch.set_permissions(ctx.guild.default_role, overwrite=overwrite)
                self.locked_channels.add(ch.id)
                count += 1
            except:
                pass
        self.guild_locked.add(ctx.guild.id)
        embed.description = f"{count} kanal kilitlendi."
        await msg.edit(embed=embed)

    @commands.hybrid_command(name="unlockall", description="Tüm kanalların kilidini açar")
    @commands.has_permissions(administrator=True)
    async def unlockall(self, ctx):
        embed = discord.Embed(title="Tüm Kanalların Kilidi Açılıyor...", color=config.COLOR_NORMAL)
        msg = await ctx.reply(embed=embed)
        count = 0
        for ch in ctx.guild.text_channels:
            try:
                overwrite = ch.overwrites_for(ctx.guild.default_role)
                overwrite.send_messages = None
                await ch.set_permissions(ctx.guild.default_role, overwrite=overwrite)
                self.locked_channels.discard(ch.id)
                count += 1
            except:
                pass
        self.guild_locked.discard(ctx.guild.id)
        embed.description = f"{count} kanalın kilidi açıldı."
        await msg.edit(embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        if isinstance(channel, discord.TextChannel) and channel.guild.id in self.guild_locked:
                try:
                    overwrite = channel.overwrites_for(channel.guild.default_role)
                    overwrite.send_messages = False
                    await channel.set_permissions(channel.guild.default_role, overwrite=overwrite)
                except:
                    pass

async def setup(bot):
    await bot.add_cog(Lockdown(bot))
