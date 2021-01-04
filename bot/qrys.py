import sqlite3
import aiosqlite
db = None

async def connect_db():
    global db
    db = await aiosqlite.connect('dc.db')

async def close_db():
    global db
    await db.close()

async def random_facts():
    global db
    c = await db.cursor()
    qry = 'SELECT DISTINCT text FROM facts ORDER BY RANDOM() LIMIT 1'

    try:
        await c.execute(qry)
        facts = (await c.fetchone())[0]
    except sqlite3.Error as er:
        print('SQLite error: %s' % (' '.join(er.args)))
        print("Exception class is: ", er.__class__)
        await c.close()
        return -1

    await db.commit()
    await c.close()
    return facts

async def all_facts():
    global db
    c = await db.cursor()
    facts_list = []
    qry = 'SELECT DISTINCT text FROM facts'

    try:
        await c.execute(qry)
        rows = await c.fetchall()
        for row in rows:
            facts_list.append(row[0])
    except sqlite3.Error as er:
        print('SQLite error: %s' % (' '.join(er.args)))
        print("Exception class is: ", er.__class__)
        await c.close()
        return -1

    await db.commit()
    await c.close()
    return facts_list

async def add_facts(fact):
    global db
    c = await db.cursor()
    qry = 'INSERT INTO facts (text) VALUES(?)'

    try:
        await c.execute(qry, (fact,))
    except sqlite3.Error as er:
        print('SQLite error: %s' % (' '.join(er.args)))
        print("Exception class is: ", er.__class__)
        await c.close()
        return -1

    await db.commit()
    await c.close()
    return 0

async def remove_facts(fact):
    global db
    c = await db.cursor()
    qry = 'DELETE from facts WHERE text = ?'

    try:
        await c.execute(qry, (fact,))
    except sqlite3.Error as er:
        print('SQLite error: %s' % (' '.join(er.args)))
        print("Exception class is: ", er.__class__)
        await c.close()
        return -1

    await db.commit()
    await c.close()
    return 0

async def check_credits(user):
    global db
    c = await db.cursor()
    qry = 'SELECT credit FROM users WHERE id = ?'

    try:
        await c.execute(qry, (user,))
        row = await c.fetchone()
        if row is None:
            return -1
        credit = row[0]
    except sqlite3.Error as er:
        print('SQLite error: %s' % (' '.join(er.args)))
        print("Exception class is: ", er.__class__)
        await c.close()
        return -1

    await db.commit()
    await c.close()
    return credit

async def change_credits(userid, amount):
    amount = round(amount, 2)
    credit = await check_credits(userid)
    credit = credit + amount
    qry = 'UPDATE users SET credit = ? WHERE id = ?'
    global db
    c = await db.cursor()

    try:
        await c.execute(qry, (credit, userid))
    except sqlite3.Error as er:
        print('SQLite error: %s' % (' '.join(er.args)))
        print("Exception class is: ", er.__class__)
        await c.close()
        return -1

    await db.commit()
    await c.close()
    return 0

async def set_credits(user, amount):
    qry = 'UPDATE users SET credit = ? WHERE id = ?'
    global db
    c = await db.cursor()

    try:
        await c.execute(qry, (amount, user))
    except sqlite3.Error as er:
        print('SQLite error: %s' % (' '.join(er.args)))
        print("Exception class is: ", er.__class__)
        await c.close()
        return -1

    await db.commit()
    await c.close()
    return 0

async def init_user(userid):
    global db
    c = await db.cursor()
    qry = 'INSERT INTO users (id, credit) VALUES(?, ?)'

    try:
        await c.execute(qry, (userid, 0))
    except sqlite3.Error as er:
        print('SQLite error: %s' % (' '.join(er.args)))
        print("Exception class is: ", er.__class__)
        await c.close()
        return -1

    await db.commit()
    await c.close()
    return 0

async def init_game(content):
    global db
    c = await db.cursor()
    qry = 'INSERT INTO games (content, is_closed) VALUES(?, ?)'

    try:
        await c.execute(qry, (content, 0))
        game_id = c.lastrowid
    except sqlite3.Error as er:
        print('SQLite error: %s' % (' '.join(er.args)))
        print("Exception class is: ", er.__class__)
        await c.close()
        return -1

    await db.commit()
    await c.close()
    return game_id

async def get_game_by_id(game_id):
    global db
    c = await db.cursor()
    qry = 'SELECT * FROM games WHERE id = ?'

    try:
        await c.execute(qry, (game_id,))
        row = await c.fetchone()
    except sqlite3.Error as er:
        print('SQLite error: %s' % (' '.join(er.args)))
        print("Exception class is: ", er.__class__)
        await c.close()
        return -1

    await db.commit()
    await c.close()
    return row

async def get_all_open_games():
    global db
    c = await db.cursor()
    games_list = []
    qry = 'SELECT * FROM games WHERE win_side IS NULL'

    try:
        await c.execute(qry)
        rows = await c.fetchall()
        for row in rows:
            games_list.append(row)
    except sqlite3.Error as er:
        print('SQLite error: %s' % (' '.join(er.args)))
        print("Exception class is: ", er.__class__)
        await c.close()
        return -1

    await db.commit()
    await c.close()
    return games_list

async def get_bets_side_bet(game_id, side):
    global db
    c = await db.cursor()
    qry = 'SELECT SUM(b.bet) FROM games g, bets b WHERE g.id = b.game_id AND g.id = ? AND b.side = ?'

    try:
        await c.execute(qry, (game_id, side))
        row = await c.fetchone()
        if row is None:
            return -1
        credit = row[0]
    except sqlite3.Error as er:
        print('SQLite error: %s' % (' '.join(er.args)))
        print("Exception class is: ", er.__class__)
        await c.close()
        return -1

    await db.commit()
    await c.close()
    return credit
    
async def add_bet(game_id, user_id, bet, side):
    bet = round(bet, 2)
    global db
    c = await db.cursor()
    credit = await check_credits(user_id)
    credit = credit - bet
    qry1 = 'INSERT INTO bets (game_id, user_id, bet, side) VALUES(?, ?, ?, ?)'
    qry2 = 'UPDATE users SET credit = ? WHERE id = ?'

    try:
        await c.execute(qry1, (game_id, user_id, bet, side))
        await c.execute(qry2, (credit, user_id))
    except sqlite3.Error as er:
        print('SQLite error: %s' % (' '.join(er.args)))
        print("Exception class is: ", er.__class__)
        await c.close()
        return -1

    await db.commit()
    await c.close()
    return 0

async def close_game(game_id):
    qry = 'UPDATE games SET is_closed = ? WHERE id = ?'
    global db
    c = await db.cursor()

    try:
        await c.execute(qry, (1, game_id))
    except sqlite3.Error as er:
        print('SQLite error: %s' % (' '.join(er.args)))
        print("Exception class is: ", er.__class__)
        await c.close()
        return -1
    
    await db.commit()
    await c.close()
    return 0

async def result_game(game_id, win_side):
    qry = 'UPDATE games SET win_side = ? WHERE id = ?'
    global db
    c = await db.cursor()

    try:
        await c.execute(qry, (win_side, game_id))
    except sqlite3.Error as er:
        print('SQLite error: %s' % (' '.join(er.args)))
        print("Exception class is: ", er.__class__)
        await c.close()
        return -1
    
    await db.commit()
    await c.close()
    return 0

async def get_game_side_bets(game_id, side):
    global db
    c = await db.cursor()
    user_list = []
    qry = 'SELECT user_id, bet FROM bets WHERE game_id = ? and side = ?'

    try:
        await c.execute(qry, (game_id, side))
        rows = await c.fetchall()
        for row in rows:
            user_list.append(row)
    except sqlite3.Error as er:
        print('SQLite error: %s' % (' '.join(er.args)))
        print("Exception class is: ", er.__class__)
        await c.close()
        return -1

    await db.commit()
    await c.close()
    return user_list
