import os
import random
import discord
import yaml

with open("../config/config.yml", 'r') as cfg:
    config = yaml.load(cfg, Loader=yaml.FullLoader)

token = os.getenv("config['token']")
#guild = os.getenv("DISCORD_GUILD")

our_guild = "NimbleEdge"

# Configuration for pick-up-your-roles channel
#
# roles_message_content : actual content of the roles message
# roles_message_id      : id of the message to check for reactions
# 
roles_message_id      = 0
emojis_to_roles       = {
    discord.PartialEmoji(name='💻'): 893061014206156840,
    discord.PartialEmoji(name='📜'): 894142617527414854,
}
roles_message_content = """
**Pick up your roles to see everything you need!**

Community channels are accessible to everyone.
Development & Research channels are hidden and can be accessed with developer & researcher roles respectively.

Add a reaction to gain access to the role.
Take away your reaction, to remove the role.

💻 : Developer
📜 : Researcher

"""

# Actual intents & client for discord API

intents = discord.Intents.default()
intents.members = True
#intents.reactions = True
#intents.messages = True
client = discord.Client(intents=intents)


# Initialization (as soon as bot is ready)
@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == our_guild:
            break

    print(
        f"{client.user} is connected to the following guild:\n"
        f"{guild.name}(id: {guild.id})"
    )

    # Get the roles channel
    for channel in guild.text_channels:
        if "pick-up-your-roles" in channel.name:
            break

    # Get associated roles message (if exists)
    message = None
    messages = await channel.history(limit=5).flatten()
    for m in messages:
        if "pick up your roles to see everything you need" in m.content.lower():
            message = m
            break

    # Create the roles message if it does not exist
    if not message:
        message = await channel.send(roles_message_content)

        for emoji in emojis_to_roles:
            await message.add_reaction(emoji)

    # Finally save the role_message_id for future
    roles_message_id = message.id


# Currently unused, on_message can be used to do something on a new message.
@client.event
async def on_message(message):
    if message.author == client.user:
        return

# Gives a role based on a reaction emoji
@client.event
async def on_raw_reaction_add(payload):
    print(roles_message_id)
    print(payload)
    # Make sure that the message user is reacting to is the one we want.
    if payload.message_id != roles_message_id:
        return

    # Confirm that we're still in the guild
    guild = client.get_guild(payload.guild_id)
    if (guild is None) or (guild.name != our_guild):
        return

    # If the emoji isn't the one we care about then exit as well
    try:
        role_id = emojis_to_roles[payload.emoji]
    except KeyError:
        print("The emoji: ", payload.emoji, " does not exist!")
        return

    # Make sure the role still exists and is valid
    role = guild.get_role(role_id)
    if role is None:
        print("The role: ", role_id, " does not exist!")
        return

    # Finally add the role
    try:
        await payload.member.add_roles(role)
    except discord.HTTPException:
        print("ERROR: Not able to add role for member: ", payload.member, " ,role: ", role)
        pass

# Removes a role based on a reaction emoji
@client.event
async def on_raw_reaction_remove(payload):
    print(payload)
    # Make sure that the message user is reacting to is the one we want.
    if payload.message_id != roles_message_id:
        return

    # Confirm that we're still in the guild
    guild = client.get_guild(payload.guild_id)
    if (guild is None) or (guild.name != our_guild):
        return

    # If the emoji isn't the one we care about then exit as well
    try:
        role_id = emojis_to_roles[payload.emoji]
    except KeyError:
        print("The emoji: ", payload.emoji, " does not exist!")
        return

    # Make sure the role still exists and is valid
    role = guild.get_role(role_id)
    if role is None:
        print("The role: ", role_id, " does not exist!")
        return

    # The payload for `on_raw_reaction_remove` does not provide `.member`
    # so we must get the member ourselves from the payload's `.user_id`
    member = guild.get_member(payload.user_id)
    if member is None:
        return

    # Finally remove the role
    try:
        await member.remove_roles(role)
    except discord.HTTPException:
        print("ERROR: Not able to remove role for member: ", member, " ,role: ", role)
        pass

# Finally run the client
client.run(token)
