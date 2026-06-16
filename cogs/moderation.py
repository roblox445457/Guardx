import discord
from discord.ext import commands
import asyncio
from datetime import datetime, timedelta
from utils.helpers import create_log_embed, check_permissions, error_embed, success_embed, info_embed, e, footer, BLURPLE, GREEN, RED, YELLOW, FUCHSIA

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.temp_bans = {}

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        """Kicks a member from the server"""
        if not check_permissions(ctx, member, "kick"):
            return await ctx.send(embed=error_embed("I don't have permission to kick members!"))
        await member.kick(reason=reason)
        await ctx.send(embed=create_log_embed("Kick", member, ctx.author, reason))

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        """Permanently bans a member from the server"""
        if not check_permissions(ctx, member, "ban"):
            return await ctx.send(embed=error_embed("I don't have permission to ban members!"))
        await member.ban(reason=reason, delete_message_days=1)
        await ctx.send(embed=create_log_embed("Ban", member, ctx.author, reason))

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def tempban(self, ctx, member: discord.Member, duration: int, *, reason=None):
        """Temporarily bans a member (duration in minutes)"""
        if not check_permissions(ctx, member, "ban"):
            return await ctx.send(embed=error_embed("I don't have permission to ban members!"))

        await member.ban(reason=f"Temporary ban: {reason}", delete_message_days=1)
        self.temp_bans[member.id] = {
            'guild': ctx.guild.id,
            'unban_time': datetime.utcnow() + timedelta(minutes=duration)
        }

        embed = create_log_embed("Temporary Ban", member, ctx.author, reason)
        embed.add_field(name="⏱️  Duration", value=f"`{duration}` minutes", inline=True)
        await ctx.send(embed=embed)

        await asyncio.sleep(duration * 60)
        if member.id in self.temp_bans:
            await ctx.guild.unban(member, reason="Temporary ban expired")
            del self.temp_bans[member.id]
            embed2 = discord.Embed(
                title="🔓  Temporary Ban Expired",
                description=f"{member.mention} has been automatically unbanned.",
                colour=e(GREEN)
            )
            embed2.set_thumbnail(url=member.display_avatar.url)
            footer(embed2)
            await ctx.send(embed=embed2)

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def clear(self, ctx, amount: int):
        """Clears specified number of messages"""
        if amount > 100:
            return await ctx.send(embed=error_embed("Cannot delete more than **100** messages at once!"))

        deleted = await ctx.channel.purge(limit=amount + 1)
        embed = discord.Embed(
            description=f"🗑️  Cleared **{len(deleted) - 1}** messages.",
            colour=e(BLURPLE)
        )
        footer(embed)
        msg = await ctx.send(embed=embed)
        await asyncio.sleep(4)
        await msg.delete()

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def mute(self, ctx, member: discord.Member, duration: int = None, *, reason=None):
        """Mutes a member (duration in minutes, if specified)"""
        if not check_permissions(ctx, member, "mute"):
            return await ctx.send(embed=error_embed("I don't have permission to manage roles!"))

        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not muted_role:
            muted_role = await ctx.guild.create_role(name="Muted")
            for channel in ctx.guild.channels:
                await channel.set_permissions(muted_role, speak=False, send_messages=False)

        await member.add_roles(muted_role, reason=reason)

        embed = create_log_embed("Mute", member, ctx.author, reason)
        if duration:
            embed.add_field(name="⏱️  Duration", value=f"`{duration}` minutes", inline=True)
        await ctx.send(embed=embed)

        if duration:
            await asyncio.sleep(duration * 60)
            if muted_role in member.roles:
                await member.remove_roles(muted_role, reason="Mute duration expired")
                embed2 = discord.Embed(
                    title="🔊  Mute Expired",
                    description=f"{member.mention} has been automatically unmuted.",
                    colour=e(GREEN)
                )
                embed2.set_thumbnail(url=member.display_avatar.url)
                footer(embed2)
                await ctx.send(embed=embed2)

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def unmute(self, ctx, member: discord.Member, *, reason=None):
        """Unmutes a member"""
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not muted_role or muted_role not in member.roles:
            return await ctx.send(embed=error_embed(f"{member.mention} is not muted!"))
        await member.remove_roles(muted_role, reason=reason)
        await ctx.send(embed=create_log_embed("Unmute", member, ctx.author, reason))

async def setup(bot):
    await bot.add_cog(Moderation(bot))
