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
        cursor.execute("SELECT total_profit FROM margin LIMIT 1")
        for x in cursor:
            x = str(x)
            total_profit = float(x[1:-2])
        odds = glicko.calculate_odds(p1_glicko, p2_glicko)
        margin = glicko.calculate_margin(total_profit)
        if odds > 50:
            odds = 100 - odds
        elif odds == 50:
            minus_odds = 1 + margin
            plus_odds = 1 + margin
        if odds > 0:
            minus_odds = (100 / odds) * (1 + margin)
            plus_odds = (100 / odds) * (1 - margin)
        else:
            print("odds are 0")
        print("odds calculated")
        print(minus_odds,plus_odds)
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
            cursor.execute(f"INSERT INTO line_board(line_text, output_odds, input_odds, is_active)VALUES ('{p1_tag} to beat {p2_tag}',1,{minus_odds},1)")
            cursor.execute(f"INSERT INTO line_board(line_text, output_odds, input_odds, is_active)VALUES ('{p2_tag} to beat {p1_tag}',{plus_odds},1,1)")
            db.commit()

        elif p2_glicko > p1_glicko:
            cursor.execute(f"INSERT INTO line_board(line_text, output_odds, input_odds, is_active)VALUES ('{p2_tag} to beat {p1_tag}',1,{minus_odds},1)")
            cursor.execute(f"INSERT INTO line_board(line_text, output_odds, input_odds, is_active)VALUES ('{p1_tag} to beat {p2_tag}',{plus_odds},1,1)")
            db.commit()

        print(f'Set: {i[0]},{i[1]},{i[2]}')
        cursor.execute(f"INSERT INTO processed_sets_started(startID, p1ID, p2ID) VALUES('{i[0]}','{i[1]}','{i[2]}')")
        db.commit()
        smashbucks.send("A new line was added! Use %lines to see all available lines.")
    print("finished")


async def collect_finished_sets():
    await asyncio.sleep(10)

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
# 1. Collect all matches that have finished and the usernames of the participants
# 2. Check these match ids against the already processed ones
# 3. For each new match:
#   a. Check if the match has an associated odds line. If it does, resolve the line
#   c. add the set to the list of already processed sets
