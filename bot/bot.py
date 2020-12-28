# bot.py
import os
import random
import sqlite3

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

def _all_facts(args):
    facts_list = [
        # '俞勇哲是狗',
        # '没有人🙌比雪梨🙌更懂🙌k头',
    ]
    conn = sqlite3.connect('dc.db')
    c = conn.cursor()
    qry = 'SELECT DISTINCT text FROM facts'
    c.execute(qry)
    for row in c:
        facts_list.append(row[0])
    conn.commit()
    conn.close()
    return facts_list

def _random_facts(args):
    facts_list = [
        # '俞勇哲是狗',
        # '没有人🙌比雪梨🙌更懂🙌k头',
    ]
    conn = sqlite3.connect('dc.db')
    c = conn.cursor()
    qry = 'SELECT DISTINCT text FROM facts ORDER BY RANDOM() LIMIT 1'
    c.execute(qry)
    facts = c.fetchone()[0]
    conn.commit()
    conn.close()
    return facts

def m_addfacts(fact):
    conn = sqlite3.connect('dc.db')
    c = conn.cursor()
    qry = 'INSERT INTO facts VALUES(?)'
    c.execute(qry, fact)
    conn.commit()
    conn.close()

def _remove_facts(fact):
    conn = sqlite3.connect('dc.db')
    c = conn.cursor()
    qry = 'DELETE from facts WHERE text = ?'
    c.execute(qry, fact)
    conn.commit()
    conn.close()

def m_checkcredit(user):
    conn = sqlite3.connect('dc.db')
    c = conn.cursor()
    qry = 'SELECT credit FROM users WHERE id = ?'
    c.execute(qry, user)
    credit = c.fetchone()[0]
    conn.commit()
    conn.close()
    return credit

def _change_credit(user, amount):
    credit = m_checkcredit(user)
    credit = credit + amount
    qry = 'UPDATE users SET credit = ? WHERE id = ?'
    conn = sqlite3.connect('dc.db')
    c = conn.cursor()
    data = [credit, user]
    c.execute(qry, data)
    conn.commit()
    conn.close()

def _set_credit(user, amount):
    qry = 'UPDATE users SET credit = ? WHERE id = ?'
    conn = sqlite3.connect('dc.db')
    c = conn.cursor()
    data = [amount, user]
    c.execute(qry, data)
    conn.commit()
    conn.close()


client.run(TOKEN)