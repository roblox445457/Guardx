import discord
from discord.ext import commands
from datetime import datetime
from utils.helpers import error_embed, success_embed, footer, e, BLURPLE, GREEN

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def serverinfo(self, ctx):
        """Displays server information"""
        guild = ctx.guild
        owner = guild.owner

        text_channels  = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        categories     = len(guild.categories)
        online = sum(1 for m in guild.members if m.status != discord.Status.offline)

        embed = discord.Embed(
            title=f"🏰  {guild.name}",
            description=guild.description or "",
            colour=e(BLURPLE),
        )

        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        if guild.banner:
            embed.set_image(url=guild.banner.url)

        embed.add_field(name="👑  Owner",    value=owner.mention,                   inline=True)
        embed.add_field(name="🌍  Region",   value="Automatic",                     inline=True)
        embed.add_field(name="🪪  Server ID", value=f"`{guild.id}`",               inline=True)

        embed.add_field(name="👥  Members",  value=f"**{guild.member_count}** total\n🟢 {online} online", inline=True)
        embed.add_field(name="💬  Channels", value=f"📝 {text_channels}  🔊 {voice_channels}  📁 {categories}", inline=True)
        embed.add_field(name="🎭  Roles",    value=f"`{len(guild.roles)}`",         inline=True)

        embed.add_field(name="🔒  Verification", value=str(guild.verification_level).title(), inline=True)
        embed.add_field(name="🚀  Boosts",       value=f"`{guild.premium_subscription_count}` (Tier {guild.premium_tier})", inline=True)
        embed.add_field(name="📅  Created",      value=f"<t:{int(guild.created_at.timestamp())}:D>", inline=True)

        embed.set_footer(text=f"Guard Bot  •  Requested by {ctx.author}")
        embed.timestamp = datetime.utcnow()
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def role(self, ctx, member: discord.Member, role: discord.Role):
        """Adds or removes a role from a member"""
        if role >= ctx.guild.me.top_role:
            return await ctx.send(embed=error_embed("I can't manage a role that is higher than or equal to my own!"))

        if role in member.roles:
            await member.remove_roles(role)
            embed = discord.Embed(
                title="➖  Role Removed",
                description=f"Removed {role.mention} from {member.mention}",
                colour=role.colour if role.colour.value else e(BLURPLE)
            )
        else:
            await member.add_roles(role)
            embed = discord.Embed(
                title="➕  Role Added",
                description=f"Gave {role.mention} to {member.mention}",
                colour=role.colour if role.colour.value else e(BLURPLE)
            )

        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="👤  Member",     value=f"{member.mention} `{member.id}`", inline=True)
        embed.add_field(name="🎭  Role",        value=f"{role.mention} `{role.id}`",    inline=True)
        embed.add_field(name="🛡️  Moderator",  value=ctx.author.mention,               inline=True)
        footer(embed)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Admin(bot))
