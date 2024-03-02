import glicko
import main
import startgg
import time


async def start_loop(tourney_slug):
    db = main.init_database()
    cursor = main.init_cursor(db)
    smashbucks = main.smashbucks
    output = await startgg.get_ids(tourney_slug)
    event_id = output[0]
    for i in output[1]:
        current_id = i['id']
        username = i['name']
        cursor.execute(f"UPDATE startGG SET current_id = '{current_id}' WHERE username = '{username}'")
        db.commit()
    print("Collected Tag IDs and Event ID.")
    tourney_slug = tourney_slug.replace("-", " ")
    tourney_slug = tourney_slug.replace("in house", "In-House")
    tourney_slug = tourney_slug.replace("cornell", "Cornell")
    #await smashbucks.send("Welcome to "+tourney_slug+"!\nYou will be able to place wagers on all of tonight's sets. Wagers will appear as the tournament continues. For all wagers, the minimum bet is 5 SmashBucks and the maximum bet is 100 SmashBucks. Any payouts that are less than 1 will become 1.\nHave fun!")
    await collect_finished_sets(event_id)
    #await collect_started_sets(event_id)



async def collect_started_sets(event_id):
    db = main.init_database()
    cursor = main.init_cursor(db)
    smashbucks = main.smashbucks
    sets = await startgg.chain_locate_started(event_id)
    print(sets)
    for i in sets:
        print(i)
        cursor.execute(f"SELECT r.glicko FROM startGG AS s INNER JOIN balance AS b ON b.ID = s.playerID INNER JOIN rankings AS r ON r.player_id = b.ID WHERE s.current_id = '{i[1]}'")
        p1_id = i[1]
        for x in cursor:
            x = str(x)
            p1_glicko = x[1:-2]
            p1_glicko = int(p1_glicko)
            print(p1_glicko)
        cursor.execute(f"SELECT r.glicko FROM startGG AS s INNER JOIN balance AS b ON b.ID = s.playerID INNER JOIN rankings AS r ON r.player_id = b.ID WHERE s.current_id = '{i[2]}'")
        p2_id = i[2]
        for x in cursor:
            x = str(x)
            p2_glicko = x[1:-2]
            p2_glicko = int(p2_glicko)
            print(p2_glicko)
        odds = glicko.calculate_odds(p1_glicko, p2_glicko)
        if odds > 50:
            plus_odds = 100 - odds #odds that the underdog wins
            minus_odds = odds #odds that the favorite wins
        elif odds == 50:
            minus_odds = 1
            plus_odds = 1
        else:
            plus_odds = odds
            minus_odds = 100 - odds
        if odds > 0:
            minus_odds = (100 / minus_odds)
            plus_odds = (100 / plus_odds)

        else:
            print("odds are 0")
        print("odds calculated")
        cursor.execute(f"SELECT b.tag FROM balance as b INNER JOIN startGG as s ON s.playerID = b.ID WHERE s.current_id = '{p1_id}'")
        for x in cursor:
            x = str(x)
            p1_tag = x[2:-3]
            print(p1_tag)
        cursor.execute(f"SELECT b.tag FROM balance as b INNER JOIN startGG as s ON s.playerID = b.ID WHERE s.current_id = '{p2_id}'")
        for x in cursor:
            x = str(x)
            p2_tag = x[2:-3]
            print(p2_tag)
        cursor.execute("SELECT total_profit FROM margin LIMIT 1")
        for x in cursor:
            x = str(x)
            total_profit = float(x[1:-2])
        margin = glicko.calculate_margin(total_profit)
        now = time.gmtime()
        current_time = time.mktime(now)
        minus_odds = minus_odds * (1 - margin)
        minus_odds = round(minus_odds, 2)
        if minus_odds <= 1:
            minus_odds = 1.01
        plus_odds = plus_odds * (1 - margin)
        plus_odds = round(plus_odds, 2)
        if plus_odds <= 1:
            plus_odds = 1.01
        if p1_glicko > p2_glicko:
            cursor.execute(f"INSERT INTO line_board(line_text, odds, heroID, enemyID, time_occured)VALUES ('{p1_tag} to beat {p2_tag}',{minus_odds},'{p1_id}','{p2_id}','{current_time}')")
            cursor.execute(f"INSERT INTO line_board(line_text, odds, heroID, enemyID, time_occured)VALUES ('{p2_tag} to beat {p1_tag}',{plus_odds},'{p2_id}','{p1_id}','{current_time}')")
            db.commit()

        elif p2_glicko > p1_glicko:
            cursor.execute(f"INSERT INTO line_board(line_text, odds, heroID, enemyID, time_occured)VALUES ('{p2_tag} to beat {p1_tag}',{minus_odds},'{p2_id}','{p1_id}','{current_time}')")
            cursor.execute(f"INSERT INTO line_board(line_text, odds, heroID, enemyID, time_occured)VALUES ('{p1_tag} to beat {p2_tag}',{plus_odds},'{p1_id}','{p2_id}','{current_time}')")
            db.commit()

        print(f'Set: {i[0]},{i[1]},{i[2]}')
        cursor.execute(f"INSERT INTO processed_sets_started(startID, p1ID, p2ID) VALUES('{i[0]}','{i[1]}','{i[2]}')")
        db.commit()
    if sets:
        pass
        #await smashbucks.send("New lines have been added! Check %lines to view them.")
    print("finished")


async def collect_finished_sets(event_id):
    db = main.init_database()
    cursor = main.init_cursor(db)
    smashbucks = main.smashbucks
    sets = await startgg.chain_locate_finished(event_id)
    # sets[i] format: [startID, p1ID, p2ID, p1result, p2result]
    print("sets collected successfully")
    cursor.execute(f"SELECT startID from processed_sets_started")
    active_lines = []
    for x in cursor:
        x = str(x)
        x = int(x[2:-3])
        active_lines.append(x)
    print("active_lines built")
    for i in sets:
        print(i)
        print(active_lines)
        i[0] = int(i[0])
        print(i[0])
        if i[0] in active_lines:
            if i[3] == 1:
                winning_id = i[1]
            elif i[4] == 1:
                winning_id = i[2]
            else:
                print("something went wrong. No one won the set?")
                winning_id = 0
            winning_id = int(winning_id)
            print("winner decided")
            # for each set, we want to collect all lines attributed to that set. There should be two for each set. This code assumes there is only one. Also processed_sets_started is not receiving the line ids when it receives other data. 2 line id columns both MULs
            cursor.execute(f"SELECT l.heroID, l.line_id from line_board as l INNER JOIN processed_sets_started as p ON p.line_id = l.line_id WHERE p.startID = '{i[0]}' ")
            for x in cursor:
                x = str(x)
                x = x[1:-1]
                x = x.replace("'", "")
                idx = x.find(",")
                hero_id = int(x[:idx])
                line_id = int(x[idx+2:])
                print("collected heroID, lineID")
                if hero_id == winning_id:
                    print("line wins")
                    #await smashbucks.send("Line #"+str(line_id)+" has won!")
                    cursor.execute(f"SELECT player_id, wager_value, odds, wager_id FROM casino WHERE line_id = {line_id}")
                    for x in cursor:
                        x = str(x)
                        x = x[1:-1]
                        idx = x.find(",")
                        player_id = x[:idx]
                        x = x[idx+2:]
                        idx = x.find(",")
                        value = x[:idx]
                        x = x[idx+2:]
                        idx = x.find(",")
                        odds = x[:idx]
                        wager_id = int(x[idx+2:])
                        player_id = int(player_id)
                        value = float(value)
                        odds = float(odds)
                        print("collected wager_id, player_id, value, odds")
                        cursor.execute(f"SELECT balance, tag FROM balance WHERE ID = {player_id}")
                        for x in cursor:
                            x = str(x)
                            x = x[1:-1]
                            idx = x.find(",")
                            current_balance = x[:idx]
                            tag = x[idx+2:]
                            tag = tag[1:-1]
                        current_balance = float(current_balance)
                        payout = odds * value
                        if payout < value + 1:
                            payout = value + 1
                        new_balance = current_balance + payout
                        new_balance = round(new_balance, 0)
                        new_balance = int(new_balance)
                        cursor.execute(f"UPDATE balance SET balance = {new_balance}")
                        cursor.execute(f"DELETE FROM casino WHERE wager_id = {wager_id}")
                        db.commit()
                        print("submitted payout and deleted casino row")
                        # await smashbucks.send(f"{tag} has won {payout} SmashBucks!\nBalance: {current_balance} -> {new_balance}")
                else:
                    print("line loses")
                    # await smashbucks.send(f"Line # {line_id} has lost. Unfortunate.")
                    cursor.execute(f"SELECT wager_id FROM casino WHERE line_id = {line_id}")
                    for x in cursor:
                        x = str(x)
                        wager_id = x[1:-2]
                        wager_id = int(wager_id)
                        cursor.execute(f"DELETE FROM casino WHERE wager_id = {wager_id}")
                        db.commit()
            if winning_id == i[1]:
                print(f"set {i[0]} inserting in upper insert.")
                cursor.execute(f"INSERT INTO processed_sets_finished(startID, winnerID, loserID)VALUES('{i[0]}','{i[1]}','{i[2]}')")
                db.commit()
            else:
                print(f"set {i[0]} inserting in lower insert.")
                cursor.execute(f"INSERT INTO processed_sets_finished(startID, winnerID, loserID)VALUES('{i[0]}','{i[2]}','{i[1]}')")
                db.commit()
        print("processed set successfully")
    print("done.")


# STEP ONE: HANDLE ALL SETS THAT HAVE BEEN STARTED
# 1. Collect all matches that have been started and the usernames of the participants (DONE, TESTED)
#   a. Check all match ids to filter out any sets we have already processed (DONE, TESTED)
#   b. For each match, create a match row (DONE, TESTED)
# 2. Select all match rows
# 3. For each match row:
#   a. Calculate odds line by glicko ratings (DONE, tested)
#   b. Post odds line to discord (DONE, tested)
#   c. add the set to the list of already processed sets (DONE, tested)
# STEP TWO: HANDLE ALL SETS THAT HAVE FINISHED
# 1. Collect all matches that have finished and the usernames of the participants (DONE, untested)
# 2. Check these match ids against the already processed ones (DONE, untested)
# 3. For each new match:
#   a. Check if the match has an associated odds line. If it does, resolve the line (DONE, untested)
#   c. add the set to the list of already processed sets (DONE, untested)
