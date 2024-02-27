import main
import startgg
import asyncio


async def start_loop(tourney_slug):
    cursor = main.cursor
    db = main.db
    output = await startgg.get_ids(tourney_slug)
    event_id = output[0]
    for i in output[1]:
        current_id = i['id']
        username = i['name']
        cursor.execute(f"UPDATE startGG SET current_id = '{current_id}' WHERE username = '{username}'")
        db.commit()
    await collect_started_sets(event_id)


async def collect_started_sets(event_id):
    db = main.db
    cursor = main.cursor
    sets = await startgg.chain_locate_started(event_id)
# sets is list with the format [set ID, P1 ID, P2 ID]
# append all sets to processed_sets_started
    for i in sets:
        cursor.execute(f"SELECT r.glicko FROM startGG AS s INNER JOIN balance AS b ON b.ID = s.playerID INNER JOIN rankings AS r ON r.player_id = b.ID WHERE s.current_id = '{i[1]}'")
        for x in cursor:
            x = str(x)
            p1_glicko = x[1:-2]
            p1_glicko = int(p1_glicko)
        cursor.execute(f"SELECT r.glicko FROM startGG AS s INNER JOIN balance AS b ON b.ID = s.playerID INNER JOIN rankings AS r ON r.player_id = b.ID WHERE s.current_id = '{i[2]}'")
        for x in cursor:
            x = str(x)
            p2_glicko = x[1:-2]
            p2_glicko = int(p2_glicko)

        print(f'Set: {i[0]},{i[1]},{i[2]}')
        cursor.execute(f"INSERT INTO processed_sets_started(startID, p1ID, p2ID) VALUES('{i[0]}','{i[1]}','{i[2]}')")
        db.commit()
        print("added")
    print("finished")


async def collect_finished_sets():
    await asyncio.sleep(10)

# STEP ONE: HANDLE ALL SETS THAT HAVE BEEN STARTED
# 1. Collect all matches that have been started and the usernames of the participants (DONE, TESTED)
#   a. Check all match ids to filter out any sets we have already processed (DONE, TESTED)
#   b. For each match, create a match row (DONE, TESTED)
# 2. Select all match rows
# 3. For each match row:
#   a. Calculate odds line by glicko ratings
#   b. Post odds line to discord
#   c. add the set to the list of already processed sets
# STEP TWO: HANDLE ALL SETS THAT HAVE FINISHED
# 1. Collect all matches that have finished and the usernames of the participants
# 2. Check these match ids against the already processed ones
# 3. For each new match:
#   a. Check if the match has an associated odds line. If it does, resolve the line
#   b. Update the glicko rankings with the results of the set
#   c. add the set to the list of already processed sets
