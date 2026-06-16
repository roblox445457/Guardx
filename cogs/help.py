import discord
from discord.ext import commands

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Replace the default help command with our custom one
        self.bot.remove_command("help")
        
        # Icons for each category
        self.category_icons = {
            "Admin": "⚙️",
            "Moderation": "🔨",
            "Security": "🔒",
            "AntiNuke": "🛡️",
            "Logging": "📝",
            "WordFilter": "🚫",
            "Help": "❓"
        }
        
        # Category descriptions
        self.category_descriptions = {
            "Admin": "Server management commands",
            "Moderation": "User moderation and punishment commands",
            "Security": "Server security and raid protection commands",
            "AntiNuke": "Protection against server-damaging actions",
            "Logging": "Event logging and auditing commands",
            "WordFilter": "Block and filter unwanted words"
        }
    
    @commands.command()
    async def help(self, ctx, command_name=None):
        """Shows all available commands or detailed information about a specific command"""
        if command_name:
            # Get detailed help for a specific command
            command = self.bot.get_command(command_name)
            if command:
                # Get the command's cog/category
                cog_name = command.cog_name
                icon = self.category_icons.get(cog_name, "📋")
                
                # Parse the docstring to extract description, parameters, and examples
                help_text = command.help or "No description available"
                description = help_text
                parameters = []
                examples = []
                
                # Split help text into sections
                if help_text:
                    lines = help_text.split('\n')
                    current_section = 'description'
                    current_content = []
                    
                    for line in lines:
                        line = line.strip()
                        if line == "Parameters:":
                            if current_content:
                                if current_section == 'description':
                                    description = '\n'.join(current_content).strip()
                                current_content = []
                            current_section = 'parameters'
                        elif line == "Example:" or line.startswith("Example:") or line == "Examples:":
                            if current_content:
                                if current_section == 'description':
                                    description = '\n'.join(current_content).strip()
                                elif current_section == 'parameters':
                                    parameters = current_content
                                current_content = []
                            current_section = 'examples'
                        elif line:
                            current_content.append(line)
                    
                    # Add the last section being processed
                    if current_content:
                        if current_section == 'description':
                            description = '\n'.join(current_content).strip()
                        elif current_section == 'parameters':
                            parameters = current_content
                        elif current_section == 'examples':
                            examples = current_content
                
                embed = discord.Embed(
                    title=f"{icon} Command: g!{command.name}",
                    description=description,
                    color=discord.Color.blue()
                )
                
                # Add usage if arguments are required
                if command.signature:
                    embed.add_field(name="Usage", value=f"g!{command.name} {command.signature}", inline=False)
                
                # Add parameters if found in docstring
                if parameters:
                    params_text = '\n'.join(parameters)
                    embed.add_field(name="Parameters", value=params_text, inline=False)
                
                # Add examples if found in docstring
                if examples:
                    examples_text = '\n'.join(examples)
                    embed.add_field(name="Examples", value=examples_text, inline=False)
                
                # Add permission requirements if available
                permission_checks = [check for check in command.checks if hasattr(check, "__qualname__") and "has_permissions" in check.__qualname__]
                if permission_checks:
                    perms = []
                    for check in permission_checks:
                        # Extract the permission name from the check
                        if hasattr(check, "__closure__") and check.__closure__:
                            for cell in check.__closure__:
                                if hasattr(cell, "cell_contents") and isinstance(cell.cell_contents, dict):
                                    for perm_name, value in cell.cell_contents.items():
                                        if value:
                                            perms.append(perm_name.replace("_", " ").title())
                    
                    if perms:
                        embed.add_field(name="Required Permissions", value=", ".join(perms), inline=False)
                
                # For subcommands of a group
                if isinstance(command, commands.Group):
                    subcommands = [f"`g!{command.name} {subcmd.name}`" for subcmd in command.commands]
                    if subcommands:
                        embed.add_field(name="Subcommands", value=", ".join(subcommands), inline=False)
                
                # Show category
                if cog_name:
                    embed.set_footer(text=f"Category: {cog_name}")
                
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(
                    description=f"❌  Command `{command_name}` not found. Use `g!help` to see all commands.",
                    colour=discord.Colour(0xED4245)
                )
                embed.set_footer(text="Guard Bot")
                await ctx.send(embed=embed)
            return
            
        # Show all commands categorized by cog
        embed = discord.Embed(
            title="🛡️ Guard Bot Help",
            description="Below are all available commands. Use `g!help <command>` to get detailed information about a specific command.",
            color=discord.Color.blue()
        )
        
        # Get commands for each cog
        for cog_name, cog in self.bot.cogs.items():
            # Skip the Help cog itself
            if cog_name == "Help":
                continue
                
            # Get all commands from this cog
            cog_commands = []
            for cmd in cog.get_commands():
                if not cmd.hidden:
                    # For group commands, include subcommands
                    if isinstance(cmd, commands.Group):
                        main_cmd = f"`g!{cmd.name}`"
                        subcmds = [f"`g!{cmd.name} {subcmd.name}`" for subcmd in cmd.commands if not subcmd.hidden]
                        cog_commands.append(main_cmd)
                        cog_commands.extend(subcmds)
                    else:
                        cog_commands.append(f"`g!{cmd.name}`")
            
            if cog_commands:
                # Add field for this category with all its commands
                icon = self.category_icons.get(cog_name, "📋")
                description = self.category_descriptions.get(cog_name, "")
                
                embed.add_field(
                    name=f"{icon} {cog_name} {f'- {description}' if description else ''}",
                    value=", ".join(cog_commands),
                    inline=False
                )
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Help(bot))