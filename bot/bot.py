# bot.py
import os
import random
import sqlite3
import aiosqlite

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
        'user': m_user,
        'reset':m_reset,
    }

    args = message.content.split(' ')

    response = await switcher.get(args[0][1:], lambda x, y: 'Invalid')(message, args[1:])

    if response == 'Invalid':
        print('Invalid Command: ' + message.content + '\nwith details: ' + str(message))
        response = m_usage(0)

    await message.channel.send(response)

def m_usage(message, args):
    return 'ask 333 for usage'

async def m_test(message, args):
    return 'You got me :)'

async def m_facts(message, args):
    if len(args) > 2:
        print('facts: too many arguements:\n - ' + '\n - '.join(map(str, args)))
        return 'Invalid'

    if len(args) == 0:
        return await _random_facts()
    
    if len(args) == 1:
        if not args[0] == 'all':
            print('facts: expecting all:\n - ' + '\n - '.join(map(str, args)))
            return 'Invalid'

        all_facts = await _all_facts()
        if all_facts == -1:
            return _internal_error()
        return '\n - ' + '\n- '.join(map(str, all_facts))

    if len(args) == 2:
        if args[0] == 'add':
            res = await _add_facts(args[1])
            if res == -1:
                return _internal_error()
            return 'Successfully added ' + str(args[1])
        
        elif args[0] == 'remove':
            res = await _remove_facts(args[1])
            if res == -1:
                return _internal_error()
            return 'Successfully removed ' + str(args[1])

        print('facts: expecting add or remove:\n - ' + '\n - '.join(map(str, args)))
        return 'Invalid'

async def m_user(message, args):
    if len(args) > 1:
        print('user: too many arguements:\n - ' + '\n - '.join(map(str, args)))
        return 'Invalid'
    elif args[0] == 'init':
        credits = await _checkcredit(message.author.id)
        if not credits == -1:
            return 'You already have a balance of: ' + str(credits)
        res = await _init_user(message.author.id)
        if res == -1:
            return _internal_error()
        return 'Successfully init account for ' + str(message.author.name) + '.\nTry "$reset" to get initial balance.'

async def m_reset(message, args):
    if len(args) > 0:
        print('reset: too many arguements:\n - ' + '\n - '.join(map(str, args)))
        return 'Invalid'
    else:
        res = await _set_credit(message.author.id, 2000)
        if res == -1:
            return _internal_error()
        return 'Successfully set your balance to ' + str(await _checkcredit(message.author.id)) + '.'

async def _random_facts():
    db = await aiosqlite.connect('dc.db')
    c = await db.cursor()
    qry = 'SELECT DISTINCT text FROM facts ORDER BY RANDOM() LIMIT 1'

    try:
        await c.execute(qry)
        facts = (await c.fetchone())[0]
        await db.commit()
    except sqlite3.Error as er:
        print('SQLite error: %s' % (' '.join(er.args)))
        print("Exception class is: ", er.__class__)
        await db.close()
        return -1
    
    await db.close()
    return facts

async def _all_facts():
    db = await aiosqlite.connect('dc.db')
    c = await db.cursor()
    facts_list = []
    qry = 'SELECT DISTINCT text FROM facts'

    try:
        await c.execute(qry)
        rows = await c.fetchall()
        for row in rows:
            facts_list.append(row[0])
        await db.commit()
    except sqlite3.Error as er:
        print('SQLite error: %s' % (' '.join(er.args)))
        print("Exception class is: ", er.__class__)
        await db.close()
        return -1
    
    await db.close()
    return facts_list

async def _add_facts(fact):
    db = await aiosqlite.connect('dc.db')
    c = await db.cursor()
    qry = 'INSERT INTO facts (text) VALUES(?)'

    try:
        await c.execute(qry, (fact,))
        await db.commit()
    except sqlite3.Error as er:
        print('SQLite error: %s' % (' '.join(er.args)))
        print("Exception class is: ", er.__class__)
        await db.close()
        return -1

    await db.close()
    return 0

async def _remove_facts(fact):
    db = await aiosqlite.connect('dc.db')
    c = await db.cursor()
    qry = 'DELETE from facts WHERE text = ?'

    try:
        await c.execute(qry, (fact,))
        await db.commit()
    except sqlite3.Error as er:
        print('SQLite error: %s' % (' '.join(er.args)))
        print("Exception class is: ", er.__class__)
        await db.close()
        return -1

    await db.close()
    return 0

async def _checkcredit(user):
    db = await aiosqlite.connect('dc.db')
    c = await db.cursor()
    qry = 'SELECT credit FROM users WHERE id = ?'

    try:
        await c.execute(qry, (user,))
        row = await c.fetchone()
        if row is None:
            await db.close()
            return -1
        credit = row[0]
        await db.commit()
    except sqlite3.Error as er:
        print('SQLite error: %s' % (' '.join(er.args)))
        print("Exception class is: ", er.__class__)
        await db.close()
        return -1
    
    await db.close()
    return credit

async def _change_credit(userid, amount):
    credit = _checkcredit(userid)
    credit = credit + amount
    qry = 'UPDATE users SET credit = ? WHERE id = ?'
    db = await aiosqlite.connect('dc.db')
    c = await db.cursor()

    try:
        await c.execute(qry, (credit, userid))
        await db.commit()
    except sqlite3.Error as er:
        print('SQLite error: %s' % (' '.join(er.args)))
        print("Exception class is: ", er.__class__)
        await db.close()
        return -1

    await db.close()
    return 0

async def _set_credit(user, amount):
    qry = 'UPDATE users SET credit = ? WHERE id = ?'
    db = await aiosqlite.connect('dc.db')
    c = await db.cursor()
   
    try:
        await c.execute(qry, (amount, user))
        await db.commit()
    except sqlite3.Error as er:
        print('SQLite error: %s' % (' '.join(er.args)))
        print("Exception class is: ", er.__class__)
        await db.close()
        return -1

    await db.close()
    return 0

async def _init_user(userid):
    db = await aiosqlite.connect('dc.db')
    c = await db.cursor()
    qry = 'INSERT INTO users (id, credit) VALUES(?, ?)'

    try:
        await c.execute(qry, (userid, 0))
        await db.commit()
    except sqlite3.Error as er:
        print('SQLite error: %s' % (' '.join(er.args)))
        print("Exception class is: ", er.__class__)
        await db.close()
        return -1

    await db.close()
    return 0

def _internal_error():
    return 'Internal error! send DM to 333'




client.run(TOKEN)