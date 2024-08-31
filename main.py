import discord
import games
import boto3
import misc
import csv

from discord.ext import commands, tasks
from datetime import datetime, time, timedelta

# Initialize a DynamoDB resource
dynamodb = boto3.resource(
    'dynamodb',
    region_name='ap-south-1',
    aws_access_key_id='',
    aws_secret_access_key=''
)

# Reference your table
table = dynamodb.Table('Sora_Settings')

intents = discord.Intents.default()
intents.message_content = True  # Enable the message content intent

bot = commands.Bot(command_prefix="!", intents=intents)  


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} (ID: {bot.user.id})')
    print('------')

bot.remove_command('help')
@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="Help - Commands List",
        description="Here's a list of available commands:",
        color=discord.Color.blue()
    )
    
    # Set the embed image
    embed.set_image(url="https://media1.tenor.com/m/54TfSd8JOe0AAAAC/anime-cute.gif")
    
    # Adding fields for each section
    embed.add_field(
        name="Alerts",
        value="`setcustomgames [Array Of Game IDs Upto 5]`: Set custom games alerts.\n"
              "`setchannel [Channel Name]`: Set channel game alerts."
              "`gameAlert`: Toggle game alerts on or off.",
        inline=False  # This ensures that the field starts on a new line
    )
    
    embed.add_field(
        name="Search",
        value="`search [steamId]`: Search for a Steam ID.",
        inline=False
    )
    
    embed.add_field(
        name="Utility",
        value="`customgames`: List all custom games.\n"
              "`hi`: Say hi to the bot.\n"
              "`ping`: Responds with 'Pong!' and the latency.",
        inline=False
    )
    
    # Send the embed
    await ctx.send(embed=embed)

@bot.command()
async def about(ctx):
    embed = discord.Embed(
        title="Heyo there, fellow gamers! Sora here.",
        description=("I'm not your average bot, oh no! Think of me as your personal gaming assistant, "
                     "straight out of your favorite anime. I've got the scoop on the hottest deals, "
                     "I'll track your most-wanted titles, and I'm always up for a chat about the latest releases.\n\n"
                     "Got a favorite game you're dying for a discount on? Just whisper its name, and I'll keep a "
                     "watchful eye on it, alerting you the moment its price drops. Consider me your secret weapon "
                     "for building that epic game library without breaking the bank!"),
        color=discord.Color.blue()
    )
    
    # Set the embed gif
    embed.set_image(url="https://media1.tenor.com/m/-iFhBGk747MAAAAC/anime-girl.gif")
    
    # Add hyperlinks for GitHub and bot invite
    embed.add_field(
        name="Useful Links",
        value=":screwdriver: [GitHub](https://github.com/D3FaltXD/Sora-Bot) | :robot: [Bot Invite](https://discord.com/oauth2/authorize?client_id=1261365031103102977&permissions=137439463488&integration_type=0&scope=bot) ",
        inline=False
    )
    
    # Send the embed
    await ctx.send(embed=embed)
    
@bot.command()
async def ping(ctx):
    """Responds to the !ping command with 'Pong!' and the latency."""
    latency = round(bot.latency * 1000)  # Calculate latency in milliseconds
    await ctx.send(f'Pong! Latency: {latency}ms')


@bot.command()  # Ensure only server admins can use this command
async def setchannel(ctx, channel: discord.TextChannel):
    # Save the server ID and channel ID to DynamoDB
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("You must be an admin to use this command.")
        return
    save_default_channel(ctx.guild.id, channel.id)
    await ctx.send(f"Default channel set to {channel.mention}")

# Function to save the default channel to DynamoDB
def save_default_channel(server_id, channel_id):
    game_alert=False
    custom_games=[]
    table.put_item(
        Item={
            'ServerID': str(server_id),
            'DefaultChannelID': str(channel_id),
            'GameAlert': game_alert,
            'CustomGames': custom_games
        }
    )

# Modify the message sending logic to check for default channel
async def send_alert(server_id, message):
    # Query DynamoDB to get the default channel ID for the server
    default_channel_id = get_default_channel(server_id)
    if default_channel_id:
        channel = bot.get_channel(int(default_channel_id))
        if channel:
            await channel.send(message)

# Function to get the default channel from DynamoDB
def get_default_channel(server_id):
    response = table.get_item(
        Key={
            'ServerID': str(server_id)
        }
    )
    if 'Item' in response:
        return response['Item']['DefaultChannelID']
    else:
        return None
# Command to toggle the GameAlert status for a guild
@bot.command()
async def gameAlert(ctx):
    # Retrieve the current GameAlert status
    current_status = get_game_alert(ctx.guild.id)
    # Toggle the GameAlert status
    new_status = not current_status
    # Update the GameAlert status in DynamoDB
    table.update_item(
        Key={'ServerID': str(ctx.guild.id)},
        UpdateExpression='SET GameAlert = :val',
        ExpressionAttributeValues={':val': new_status}
    )
    await ctx.send(f"Game Alert status set to {'enabled' if new_status else 'disabled'}.")

# Function to get the GameAlert status from DynamoDB
def get_game_alert(server_id):
    response = table.get_item(
        Key={'ServerID': str(server_id)}
    )
    if 'Item' in response and 'GameAlert' in response['Item']:
        return response['Item']['GameAlert']
    else:
        # Default to False if not set
        return False


@bot.command()    
async def hi(ctx):    #Test Command
    # Get the server ID
    server_id = ctx.guild.id
    
    # Get the default channel ID from DynamoDB
    default_channel_id = get_default_channel(server_id)
    
    # Check if default channel ID exists
    if default_channel_id:
        # Get the channel object
        channel = bot.get_channel(int(default_channel_id))
        
        # Check if channel object exists
        if channel:
            # Send the message in the default channel
            await channel.send("hi")
        else:
            await ctx.send("Default channel not found.")
    else:
        await ctx.send("Default channel not set.")



def get_custom_games(server_id):
    try:
        response = table.get_item(
            Key={
                'ServerID': str(server_id)
            }
        )
        if 'Item' in response:
            return response['Item']['CustomGames']
        else:
            print(f"No CustomGame found for ServerID: {server_id}")
            return []  # Returning an empty list for consistency
    except Exception as e:
        print(f"Error accessing DynamoDB: {e}")
        return []  # Returning an empty list in case of error for consistency

def save_custom_games(server_id, custom_games):
    try:
        # Ensure no more than 5 custom games are saved
        custom_games = list(set(custom_games))[:5]  # Enforce uniqueness and convert to a list
        response = table.update_item(
            Key={
                'ServerID': str(server_id)
            },
            UpdateExpression="set CustomGames = :g",
            ExpressionAttributeValues={
                ':g': custom_games 
            },
            ReturnValues="UPDATED_NEW"
        )

        return response
    except Exception as e:
        print(f"Error updating DynamoDB for server {server_id}: {e}")
        print(f"Custom games: {custom_games}") # Log the custom games data for debugging
        return None
 
    
@bot.command()
async def setcustomgames(ctx, games):
    # Ensure the command is used by an admin
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("You must be an admin to use this command.")
        return

    server_id = ctx.guild.id
    custom_games = games.split(',')


    if not custom_games:
        await ctx.send("Please provide at least one game.")
        return

    # Sanity check if the custom game IDs exist
    valid_games = []
    for game in custom_games:
        if misc.is_valid_game_id(game):
            valid_games.append(game)
            await ctx.send(f"Game ID {game} added.")
        else:
            await ctx.send(f"Invalid game ID: {game}. Please provide a valid Steam game ID.")
            return

    save_custom_games(server_id, valid_games)
    

@bot.command()
async def customgames(ctx):
    server_id = ctx.guild.id
    custom_games = get_custom_games(server_id)
    if custom_games:
        games_list = ', '.join(custom_games)
        await ctx.send(f"Custom games: {games_list}")
    else:
        await ctx.send("No custom games set.")
        


from discord import Embed

def cronjob(guild_id,list_1, list_2):
    embeds = []  # List to hold all embeds for general game deals
    custom_embeds = []  # List to hold all embeds for the custom game list
    heading_embed=[]
    embed = Embed(title="Game Deals", description="Here are the latest game deals:")
    heading_embed = Embed(title="Weekly Gaming Report!", description="Here are the latest game deals and your favorite game on sale!",color=0xffff00)
    heading_embed.set_image(url="https://i.ibb.co/f2P8f2Y/Embed-Banner-01.png")  # Set the image for the heading embed

    embed = Embed(title="Game Deals", description="Here are the latest game deals:")
    custom_embed = Embed(title="Your Personalized Games List:", description="Your Favourite Games on Discount",color=0xffff00)  # New embed for custom game list


    # Add general game deals to embeds
    for i in list_2:
        for game_id, data in i.items():
            embed.add_field(name=data, value=f"[Store Link](https://store.steampowered.com/app/{game_id})", inline=False)
            if len(embed.fields) % 25 == 0:  # Discord embeds have a max of 25 fields
                embeds.append(embed)
                embed = Embed(title="Game Deals (cont.)", description="Continued...")

    # Ensure the last embed is added if it has fields
    if len(embed.fields) > 0:
        embeds.append(embed)

    # Add custom games to custom_embeds
    # Retrieve custom games for the server
    custom_game_ids = get_custom_games(guild_id)
    
    if custom_game_ids is None:
        print("No custom games found for this server.")
        return embeds  # Return only the general game deals if no custom games are set
    
    # Convert custom_game_ids to a set for faster lookup
    custom_game_ids_set = set(custom_game_ids)
    # Filter list_1 to include only games present in custom_game_ids
    filtered_list_1 = [game for game in list_1 if any(key in custom_game_ids_set for key in game.keys())]
    
    for i in filtered_list_1:
        for game_id, data in i.items():
            
            custom_embed.add_field(name=data, value=f"[Store Link](https://store.steampowered.com/app/{game_id})", inline=False)
            if len(custom_embed.fields) % 25 == 0:  # Discord embeds have a max of 25 fields
                custom_embeds.append(custom_embed)
                custom_embed = Embed(title="Your Custom Game List (cont.):", description="Customized just for you!")

    # Ensure the last custom embed is added if it has fields
    if len(custom_embed.fields) > 0:
        custom_embeds.append(custom_embed)

    # Combine both lists of embeds
    return [heading_embed] + embeds + custom_embeds
    
    



def write_to_csv():
    filename = "custom_games.csv"
    
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        for guild in bot.guilds:
            # Use 'get_custom_games(guild.id)' to get a list of game IDs for the specified guild
            custom_game_ids = get_custom_games(guild.id)
            
            # Check if custom_game_ids is not None before iterating
            if custom_game_ids != []:
                # Write each game ID in a new row in the same column
                for game_id in custom_game_ids:

                    writer.writerow([games.steam_to_cheapshark(game_id)])
            else:
                # Handle the case where custom_game_ids is None, e.g., log a warning
                print(f"No custom games found for guild ID {guild.id}")

# Define your task here

@tasks.loop(hours=24)
async def scheduled_task():
    now = datetime.now()
    if now.weekday() in (6, 2):
        write_to_csv()
        list_1 = games.csv_games()
        list_2 = games.onSale()
        for guild in bot.guilds:
            if get_game_alert(guild.id):  # Check if game alerts are enabled for the guild
                default_channel_id = get_default_channel(guild.id)
                channel = bot.get_channel(int(default_channel_id))
                embeds = cronjob(guild.id, list_1, list_2)  # Get the list of embeds
                for embed in embeds:  # Send each embed
                    await channel.send(embed=embed)
@bot.command()
async def noti(ctx):
    list_1 = games.csv_games()
    list_2 = games.onSale()
    if get_game_alert(ctx.guild.id):  # Check if game alerts are enabled for the guild
        default_channel_id = get_default_channel(guild.id)
        channel = bot.get_channel(int(default_channel_id))
        embeds = cronjob(guild.id, list_1, list_2)  # Get the list of embeds
        for embed in embeds:  # Send each embed
            await channel.send(embed=embed)    
            
@scheduled_task.before_loop
async def before_scheduled_task():
    print("Waiting for the bot to be ready...")
    await bot.wait_until_ready()
    print("Bot is ready, scheduled task can now start.")

@scheduled_task.after_loop
async def after_scheduled_task():
    if scheduled_task.failed():
        exception = scheduled_task.get_task().exception()
        print(f"Scheduled task failed with exception: {exception}")

# Error handling and bot event code here
@bot.event
async def on_command_error(ctx, error): #Error Handling
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Command not found.")
    else:
        # Handle other errors here (optional)
        print(f"An error occurred: {error}") 


# IMPORTANT: Start the scheduled task
@bot.event
async def on_ready():
    print("Bot is ready.")
    scheduled_task.start()     
      
       
       
 

token = ""
bot.run(token)

