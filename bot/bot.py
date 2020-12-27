# bot.py
import os
import random

import discord
from dotenv import load_dotenv

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
        'test': m_test,
        'facts': m_facts,
    }
    
    args = message.content.split(' ')

    response = switcher.get(args[0][1:], lambda: 'Invalid')(args[1:])

    if response == 'Invalid':
        print('Invalid Command: ' + message.content + '\nwith details: ' + str(message))
        return
        
    await message.channel.send(response)
    

def m_test(args):
    return 'You got me :)'

def m_facts(args):
    facts_list = [
        '俞勇哲是狗',
        '没有人🙌比雪梨🙌更懂🙌k头',
    ]
    return random.choice(facts_list)

client.run(TOKEN)