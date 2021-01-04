import discord
import qrys

async def m_usage(message, args):
    return '''Usage:
- $bet all
- $bet start <content>
- $bet dime <id> <side> <amount>
- $bet close <id> <win_side>
- $user init 
- $user credits
- $reset
- $facts
- $facts add <content>
- $facts all
- $facts remove <content>
- $test
- current version: v0.0.2'''

async def m_test(message, args):
    return 'You got me :)'

async def m_facts(message, args):
    if len(args) > 2:
        print('facts: too many arguements:\n - ' + '\n - '.join(map(str, args)))
        return 'Invalid'

    if len(args) == 0:
        return await qrys.random_facts()
    
    if len(args) == 1:
        if not args[0] == 'all':
            print('facts: expecting all:\n - ' + '\n - '.join(map(str, args)))
            return 'Invalid'

        all_facts = await qrys.all_facts()
        if all_facts == -1:
            return _internal_error()
        return '- ' + '\n- '.join(map(str, all_facts))

    if len(args) == 2:
        if args[0] == 'add':
            res = await qrys.add_facts(args[1])
            if res == -1:
                return _internal_error()
            return 'Successfully added ' + str(args[1])
        
        elif args[0] == 'remove':
            res = await qrys.remove_facts(args[1])
            if res == -1:
                return _internal_error()
            return 'Successfully removed ' + str(args[1])

        print('facts: expecting add or remove:\n - ' + '\n - '.join(map(str, args)))
        return 'Invalid'

async def m_user(message, args):
    if len(args) > 1 or len(args) == 0:
        print('user: too many arguements:\n - ' + '\n - '.join(map(str, args)))
        return 'Invalid'
    else:
        if args[0] == 'init':
            credits = await qrys.check_credits(message.author.id)
            if not credits == -1:
                return 'You already have a balance of: ' + str(credits)
            res = await qrys.init_user(message.author.id)
            if res == -1:
                return _internal_error()
            return 'Successfully init account for ' + str(message.author.name) \
                + '.\nTry "$reset" to get initial balance.'

        if args[0] == 'credits':
            credits = await qrys.check_credits(message.author.id)
            if credits == -1:
                return _internal_error()
            return 'Your balance is: ' + str(round(credits, 2))

    return 'Invalid'

async def m_reset(message, args):
    if len(args) > 0:
        print('reset: too many arguements:\n - ' + '\n - '.join(map(str, args)))
        return 'Invalid'
    else:
        res = await qrys.set_credits(message.author.id, 2000)
        if res == -1:
            return _internal_error()
        return 'Successfully set your balance to ' \
            + str(await qrys.check_credits(message.author.id)) + '.'

async def m_bet(message, args):
    if len(args) > 4 or len(args) == 0:
        print('bet: too many arguements:\n - ' + '\n - '.join(map(str, args)))
        return 'Invalid'
    
    else:
        if args[0] == 'all' and len(args) == 1:
            all_games = await qrys.get_all_open_games()
            if all_games == -1:
                return _internal_error()
            return '- ' + '\n- '.join(map(str, all_games))

        if args[0] == 'start' and len(args) == 2:
            content = args[1]
            res = await qrys.init_game(content)
            if res == -1:
                return _internal_error()
            return 'Successfully start bet ' + content + ' with id ' + str(res) \
                + ' , current odds are: 1:2 and 1:2.'

        if args[0] == 'check' and len(args) == 2:
            game_id = args[1]
            raw_odds = await _check_cur_odds(game_id)
            return 'The current odds of ' + (await _get_content_by_id(game_id)) + ' with id ' + str(game_id) \
                + ' are: 1 : ' + str(1 + raw_odds[0]) + ' and 1 : ' + str(1 + raw_odds[1]) + '.'

        if args[0] == 'dime' and len(args) == 4:
            game_id = args[1]
            side = int(args[2])
            amount = float(args[3])
            user_id = message.author.id
            if not (side == 0 or side == 1):
                print('bet dime: wrong side arguments: ' + str(side))
                return 'Invalid'

            if amount <= 0:
                return 'You need to dime at least 0.01'

            if (await _get_closed_by_id(game_id)) == 1:
                return 'You can not dime a closed game.'

            if (await qrys.check_credits(user_id)) - amount < 0:
                return 'You do not have enough balance.'\
                    + 'If you ran got of your balance, try "$reset" to get some balance'

            res = await qrys.add_bet(game_id, message.author.id, amount, side)
            if res == -1:
                print('bet dime: add bets error\n - ' + '\n - '.join(map(str, args)))
                return _internal_error()
            
            raw_odds = await _check_cur_odds(game_id)
            return 'Successfully dimed "' + str(await _get_content_by_id(game_id)) \
                + '", current odds are: 1 : ' + str(1 + raw_odds[0]) + ' and 1 : ' + str(1 + raw_odds[1]) + '.'

        if args[0] == 'close' and len(args) == 2:
            game_id = args[1]

            res = await qrys.close_game(game_id)
            if res == -1:
                return _internal_error()

            return 'Successfully close game: ' + str(game_id) + ', it is no longer open for dimes.'
            

        if args[0] == 'result' and len(args) == 3:
            game_id = args[1]
            win_side = int(args[2])
            if not (win_side == 0 or win_side == 1):
                print('bet dime: wrong win_side argument ' + str(win_side))
                return 'Invalid'

            if (await _get_closed_by_id(game_id)) == 0:
                return 'Please use "$bet close ' + str(game_id) + '"close game: ' + str(game_id) + ' first.'

            raw_odds = await _check_cur_odds(game_id)
            winner_list = await qrys.get_game_side_bets(game_id, win_side)
            for winner in winner_list:
                user_id = winner[0]
                amount = winner[1] * (raw_odds[win_side] + 1)
                res = await qrys.change_credits(user_id, amount)
            return 'Successfully result game: ' + str(game_id) + ' and win side is ' + str(win_side) + '.'\
                + '\nTry "$user credits" to check your current balance'
            

        print('bet: wrong number of arguements:\n - ' + '\n - '.join(map(str, args)))
        return 'Invalid'

async def _check_cur_odds(game_id):
    bet_0 = await qrys.get_bets_side_bet(game_id, 0) or 1
    bet_1 = await qrys.get_bets_side_bet(game_id, 1) or 1
    return (bet_1 / bet_0, bet_0 / bet_1)

async def _get_content_by_id(game_id):
    row = await qrys.get_game_by_id(game_id)
    return row[1]

async def _get_closed_by_id(game_id):
    row = await qrys.get_game_by_id(game_id)
    return row[2]

def _internal_error():
    return 'Internal error! send DM to 333'
