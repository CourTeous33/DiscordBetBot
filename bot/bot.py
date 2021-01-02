# bot.py
import os
import random

import discord
from dotenv import load_dotenv
import commands as cm
import qrys

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

client = discord.Client()
prefix = '$'

@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == GUILD:
            break
    
    await qrys.connect_db()

    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if not message.content.startswith(prefix):
        return

    switcher = {
        'test': cm.m_test,
        'facts': cm.m_facts,
        'user': cm.m_user,
        'reset': cm.m_reset,
        'bet': cm.m_bet,
    }

    args = message.content.split(' ')

    response = await switcher.get(args[0][1:], cm.m_usage)(message, args[1:])

    if response == 'Invalid':
        print('Invalid Command: ' + message.content + '\nwith details: ' + str(message))
        response = cm.m_usage(0, 0)

    await message.channel.send(response)

client.run(TOKEN)
