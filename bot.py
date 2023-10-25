import discord, random, json, datetime, numpy
from discord.ext import commands

with open('data/config.json', 'r') as f:
  data = json.load(f)
with open('data/boxing.json', 'r') as f2:
  boxing_list = json.load(f2)
with open('data/wins.json', 'r') as f3:
  wins_list = json.load(f3)
with open('data/cooldowns.json', 'r') as f4:
  cooldowns_list = json.load(f4)

discord_token = data["token"]
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all(), help_command=None)

# Bot startup and status
@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.dnd, activity=discord.Activity(type=discord.ActivityType.watching, name="Boxing Matches"))
    print("Online")

# Sends cooldown message on bot command
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.reply(f"{error.retry_after:.2f} seconds to try again", delete_after=3)  

# Command for joining the boxing events
@bot.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def joinbox(ctx):
    member = ctx.author
    string_member = str(member)
    if string_member in boxing_list:
        embed = discord.Embed(title="You are already in the tournament!", color=discord.Colour.dark_red())
        await ctx.reply(embed=embed)
    else:
        boxing_list[string_member] = 4
        wins_list[string_member] = 0
        presentDate = datetime.datetime.now()
        cooldowns_list[string_member] = datetime.datetime.timestamp(presentDate)*1000
        with open("Bot/boxing.json", "w") as outfile:
            json.dump(boxing_list, outfile)
        with open("Bot/wins.json", "w") as outfile2:
            json.dump(wins_list, outfile2)
        with open("Bot/cooldowns.json", "w") as outfile3:
            json.dump(cooldowns_list, outfile3)
        embed = discord.Embed(title="You have joined the tournament, good luck!", color=discord.Colour.dark_green())
        await ctx.reply(embed=embed)

# Command for challenging someone to boxing
@bot.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def box(ctx, member:discord.Member = None):
    string_member, string_author = str(member), str(ctx.author)
    name, pfp = ctx.author.display_name, ctx.author.display_avatar
    if boxing_list[string_author] == 0:
        presentDate = datetime.datetime.now()
        unix_timestamp = datetime.datetime.timestamp(presentDate)*1000
        if cooldowns_list[string_author] <= unix_timestamp:
            boxing_list[string_author] = 4
        else:
            await ctx.reply(f"You can box again at <t:{round(cooldowns_list[string_author] / 1000)}>")
            return
    if (string_member in boxing_list) and (string_member != string_author) and (string_author in boxing_list):
        winner = random.randint(1, 101)
        if string_member == 'rumjahn':
            winner = random.randint(45, 101)
        if winner <= 45:
            wins_list[string_author] += 1
            wins_list[string_member] -= 1
        elif winner > 55:
            wins_list[string_member] += 1
        boxing_list[string_author] -= 1
        if boxing_list[string_author] == 0:
            presentDate = datetime.datetime.now()
            cooldowns_list[string_author] = ((datetime.datetime.timestamp(presentDate)*1000) + 86400000)
            with open("Bot/cooldowns.json", "w") as outfile3:
                json.dump(cooldowns_list, outfile3)
        with open("Bot/boxing.json", "w") as outfile:
            json.dump(boxing_list, outfile)
        with open("Bot/wins.json", "w") as outfile2:
            json.dump(wins_list, outfile2)
        if winner <= 45:
            embed = discord.Embed(title=f"{string_author} won!", color=discord.Colour.brand_green())
            embed.set_author(name=f"{name}", icon_url=f"{pfp}")
            embed.set_image(url="https://i.seadn.io/gcs/files/a60d56eade0f874a8def67cb8b6231ed.gif?auto=format&dpr=1&w=1000")
            await ctx.reply(embed=embed)
        elif winner > 55:
            embed = discord.Embed(title=f"{string_member} won!", color=discord.Colour.brand_red())
            embed.set_author(name=f"{name}", icon_url=f"{pfp}")
            embed.set_image(url="https://i.seadn.io/gcs/files/a60d56eade0f874a8def67cb8b6231ed.gif?auto=format&dpr=1&w=1000")
            await ctx.reply(embed=embed)
        else:
            embed = discord.Embed(title=f"The match is a draw.", color=discord.Colour.dark_gray())
            embed.set_author(name=f"{name}", icon_url=f"{pfp}")
            embed.set_image(url="https://i.seadn.io/gcs/files/a60d56eade0f874a8def67cb8b6231ed.gif?auto=format&dpr=1&w=1000")
            await ctx.reply(embed=embed)
    else:
        embed = discord.Embed(title="Invalid opponent", color=discord.Colour.dark_red())
        await ctx.reply(embed=embed)
        ctx.command.reset_cooldown(ctx)

# Command for displaying boxing leaderboard
@bot.command(aliases=["boxingleaderboard", "lb", "blb"])
@commands.cooldown(1, 15, commands.BucketType.user)
async def leaderboard(ctx):
    rank1, rank2, rank3, rank4, rank5 = '', '', '', '', ''
    rank1score, rank2score, rank3score, rank4score, rank5score = 0, 0, 0, 0, 0

    keys, values = list(wins_list.keys()), list(wins_list.values())
    sorted_value_index = numpy.argsort(values)
    sorted_dict = {keys[i]: values[i] for i in sorted_value_index}
    key_list = list(sorted_dict.keys())
    key_list = list(reversed(key_list))
    value_list = list(sorted_dict.values())
    value_list = list(reversed(value_list))

    if len(sorted_dict) >= 1:
        rank1, rank1score = key_list[0], value_list[0]
        if len(sorted_dict) >= 2:
            rank2, rank2score = key_list[1], value_list[1]
            if len(sorted_dict) >= 3:
                rank3, rank3score = key_list[2], value_list[2]
                if len(sorted_dict) >= 4:
                    rank4, rank4score = key_list[3], value_list[3]
                    if len(sorted_dict) >= 5:
                        rank5, rank5score = key_list[4], value_list[4]
                            
    embed = discord.Embed(title="Boxing Leaderboard", description="*Top 5 Trophies*", color=discord.Colour.dark_gold())
    embed.add_field(name=f"**1st. **{rank1}", value=f"{rank1score} trophies", inline='false')
    embed.add_field(name=f"**2nd. **{rank2}", value=f"{rank2score} trophies", inline='false')
    embed.add_field(name=f"**3rd. **{rank3}", value=f"{rank3score} trophies", inline='false')
    embed.add_field(name=f"**4th. **{rank4}", value=f"{rank4score} trophies", inline='false')
    embed.add_field(name=f"**5th. **{rank5}", value=f"{rank5score} trophies", inline='false')
    await ctx.send(embed=embed)

# Check your rank
@bot.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def rank(ctx, member:discord.Member = None):
    if member is None:
        member = ctx.author
    string_member = str(member)
    name, pfp = member.display_name, member.display_avatar
    keys, values = list(wins_list.keys()), list(wins_list.values())
    sorted_value_index = numpy.argsort(values)
    sorted_dict = {keys[i]: values[i] for i in sorted_value_index}
    key_list = list(sorted_dict.keys())
    key_list = list(reversed(key_list))
    rank_number = key_list.index(string_member) + 1
    embed = discord.Embed(title="Rank", description=f"#{rank_number}", color=discord.Colour.dark_gold())
    embed.set_author(name=f"{name}", icon_url=f"{pfp}")
    await ctx.reply(embed=embed)

# Command for displaying your remaining lives
@bot.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def actions(ctx):
    string_author = str(ctx.author)
    name, pfp = ctx.author.display_name, ctx.author.display_avatar
    if string_author in boxing_list:
        total_lives = boxing_list[string_author]
        if total_lives == 0:
            embed = discord.Embed(title=":broken_heart::broken_heart::broken_heart::broken_heart:", color=discord.Colour.dark_gray())
            embed.set_author(name=f"{name}", icon_url=f"{pfp}")
            await ctx.reply(embed=embed)
        else:
            embed = discord.Embed(title=(":heart:"*total_lives) + (":broken_heart:"*(4-total_lives)), color=discord.Colour.brand_red())
            embed.set_author(name=f"{name}", icon_url=f"{pfp}")
            await ctx.reply(embed=embed)
    else:
        embed = discord.Embed(title="You are not in the event", color=discord.Colour.dark_red())
        embed.set_author(name=f"{name}", icon_url=f"{pfp}")
        await ctx.reply(embed=embed)

# Command for displaying your total boxing wins
@bot.command(aliases=["wins", "trophy", "awards"])
@commands.cooldown(1, 5, commands.BucketType.user)
async def trophies(ctx):
    string_author = str(ctx.author)
    name, pfp = ctx.author.display_name, ctx.author.display_avatar
    if string_author in wins_list:
        total_wins = wins_list[string_author]
        if total_wins == 0:
            embed = discord.Embed(title=":wastebasket:", color=discord.Colour.dark_gray())
            embed.set_author(name=f"{name}", icon_url=f"{pfp}")
            await ctx.reply(embed=embed)
        else:
            embed = discord.Embed(title=":trophy:"*total_wins, color=discord.Colour.dark_gold())
            embed.set_author(name=f"{name}", icon_url=f"{pfp}")
            await ctx.reply(embed=embed)
    else:
        embed = discord.Embed(title="You are not in the event", color=discord.Colour.dark_red())
        embed.set_author(name=f"{name}", icon_url=f"{pfp}")
        await ctx.reply(embed=embed)

# Command for displaying prize list
# @bot.command()
# @commands.cooldown(1, 5, commands.BucketType.user)
# async def prizes(ctx):
#     embed = discord.Embed(title="Prizes", description="*Top 3*", color=discord.Colour.gold())
#     embed.add_field(name="1st", value="???", inline='false')
#     embed.add_field(name="2nd", value="???", inline='false')
#     embed.add_field(name="3rd", value="???", inline='false')
#     await ctx.reply(embed=embed)

# Command for displaying other command informations
@bot.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def help(ctx):
    embed = discord.Embed(title="Help Menu", description="*To participate in the boxing event you must first use !joinbox to be able to use the commands. Then, you can box up to 4 other members a day using the !box command. The top 3 members with the most wins will recieve a prize.*", color=discord.Colour.dark_green())
    embed.add_field(name="> !joinbox", value="Joins the tournament", inline='false')
    embed.add_field(name="> !box <target>", value="Challenges another discord member to boxing", inline='false')
    embed.add_field(name="> !actions", value="Displays your remaining actions for the day", inline='false')
    embed.add_field(name="> !trophies", value="Displays your trophies", inline='false')
    embed.add_field(name="> !leaderboard", value="Displays the top 5 members for trophies", inline='false')
    embed.add_field(name="> !rank", value="Check your rank or someone else's rank", inline='false')
    # embed.add_field(name="!prizes", value="Displays the prize list for Top 3", inline='false')
    await ctx.reply(embed=embed)

if __name__ == '__main__':
    bot.run(discord_token)