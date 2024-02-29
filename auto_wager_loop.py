import glicko
import main
import startgg
import asyncio


async def start_loop(tourney_slug):
    cursor = main.cursor
    db = main.db
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
    await smashbucks.send("Welcome to "+tourney_slug+"!\nYou will be able to place wagers on all of tonight's sets. Wagers will appear as the tournament continues. For all wagers, the minimum bet is 5 SmashBucks and the maximum bet is 100 SmashBucks. Any payouts that are less than 1 will become 1.\nHave fun!")
    #while loop starts here
    await collect_finished_sets(event_id)
    await collect_started_sets(event_id)



async def collect_started_sets(event_id):
    db = main.db
    cursor = main.cursor
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
        if p1_glicko > p2_glicko:
            cursor.execute(f"INSERT INTO line_board(line_text, output_odds, input_odds, is_active, heroID, enemyID)VALUES ('{p1_tag} to beat {p2_tag}',1,{minus_odds},1,'{p1_id}','{p2_id}')")
            cursor.execute(f"INSERT INTO line_board(line_text, output_odds, input_odds, is_active, heroID, enemyID)VALUES ('{p2_tag} to beat {p1_tag}',{plus_odds},1,1,'{p2_id}','{p1_id}')")
            db.commit()

        elif p2_glicko > p1_glicko:
            cursor.execute(f"INSERT INTO line_board(line_text, output_odds, input_odds, is_active, heroID, enemyID)VALUES ('{p2_tag} to beat {p1_tag}',1,{minus_odds},1,'{p2_id}','{p1_id}')")
            cursor.execute(f"INSERT INTO line_board(line_text, output_odds, input_odds, is_active, heroID, enemyID)VALUES ('{p1_tag} to beat {p2_tag}',{plus_odds},1,1,'{p1_id}','{p2_id}')")
            db.commit()

        print(f'Set: {i[0]},{i[1]},{i[2]}')
        cursor.execute(f"INSERT INTO processed_sets_started(startID, p1ID, p2ID) VALUES('{i[0]}','{i[1]}','{i[2]}')")
        db.commit()
         #smashbucks.send("A new line was added! Use %lines to see all available lines.")
        await smashbucks.send("New lines have been added! Check %lines to view them.")
    print("finished")


async def collect_finished_sets(event_id):
    db = main.db
    cursor = main.cursor
    smashbucks = main.smashbucks
    sets = await startgg.chain_locate_finished(event_id)
    # set[i] format: [startID, p1ID, p2ID, p1result, p2result]
    cursor.execute(f"SELECT startID from processed_sets_started")
    active_lines = []
    for x in cursor:
        x = str(x)
        x = x[2:-3]
        active_lines.append(x)
    for i in sets:
        if i[0] in active_lines:
            if i[3] == 1:
                winning_id = i[1]
            elif i[4] == 1:
                winning_id = i[2]
            else:
                print("something went wrong. No one won the set?")
                winning_id = 0
            cursor.execute(f"SELECT l.heroID from line_board as l INNER JOIN processed_sets_started as p ON p.line_id = l.line_id WHERE p.startID = '{i[0]}' ")
            for x in cursor:
                x = str(x)
                hero_id = x[1:-2]
            if hero_id == winning_id:
                pass
                #the line wins
            else:
                pass
                #the line loses








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
# 1. Collect all matches that have finished and the usernames of the participants done
# 2. Check these match ids against the already processed ones done
# 3. For each new match:
#   a. Check if the match has an associated odds line. If it does, resolve the line
#   c. add the set to the list of already processed sets
