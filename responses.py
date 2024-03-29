import time
import main
import re
import random as r
import asyncio
import next
import glicko


async def handleResponse(user_message, message, is_illegal):
    p_message = user_message
    if p_message == '%beg':
        if is_illegal:
            return "Command failed to execute. Outside of bot channel."
        else:
            print("begging in progress")
            db = main.init_database()
            cursor = main.init_cursor(db)
            cursor.execute("SELECT ID FROM balance WHERE username = %s", [str(message.author)])
            for x in cursor:
                x = str(x)
            x = x.replace("(","")
            x = x.replace(",","")
            x = x.replace(")","")
            cursor.execute("SELECT bribe, time_occured FROM beg WHERE player_id = %s", [x])
            for y in cursor:
                y = str(y)
            y = y.replace("(","")
            y = y.replace("(","")
            y = y.replace(")","")
            index = y.find(",")
            bribe = y[:index]
            bribe = int(bribe)
            is_bribed = False
            if bribe > 0:
                is_bribed = True
            y = y[index+1:]
            y = float(y)
            now = time.gmtime()
            current_time = time.mktime(now)
            delay = current_time - y
            cursor.execute("UPDATE beg SET time_occured = %s WHERE player_id = %s", (str(current_time), x))
            cursor.execute("UPDATE beg SET bribe = 0 WHERE player_id = %s", [x])
            db.commit()
            if delay >= 300:
                roll = r.randint(1,100)
                bribe = bribe*3
                roll += bribe
                if roll >= 115:
                    reward = r.randint(12,30)
                elif roll >= 100:
                    reward = r.randint(2, 20)
                else:
                    reward = 0
                if reward > 0:
                    cursor.execute("SELECT balance FROM balance WHERE username = %s", [str(message.author)])
                    for b in cursor:
                        b = str(b)
                    b = b.replace("(", "")
                    b = b.replace(",", "")
                    b = b.replace(")", "")
                    current_balance = int(b)
                    new_balance = current_balance + reward
                    new_balance = str(new_balance)
                    cursor.execute("UPDATE balance SET balance = %s WHERE username = %s", (new_balance,str(message.author)))
                    db.commit()
                    reward = str(reward)
                    current_balance = str(current_balance)
                    if is_bribed:
                        return "Okay, I see you've added a little something on top. I can spare "+reward+" SmashBucks. Now leave me alone for a while.\nBalance: "+current_balance+" -> "+new_balance
                    else:
                        return "You poor thing. Here's "+reward+" SmashBucks. Now leave me alone for a while.\nBalance: "+current_balance+" -> "+new_balance
                else:
                    return "No. Maybe later."
            else:
                return "Too soon, man. Too soon"

    if re.search('%bribe*',p_message):
        db = main.init_database()
        cursor = main.init_cursor(db)
        bribe = p_message
        bribe = bribe.replace("%bribe ","")
        cursor.execute("SELECT ID, balance FROM balance WHERE username = %s", [str(message.author)])
        for x in cursor:
            x = str(x)
        x = x.replace("(","")
        x = x.replace(")","")
        index = x.find(",")
        player_id = x[:index]
        current_balance = x[index+1:]
        current_balance = int(current_balance)
        bribe = int(bribe)
        new_balance = current_balance - bribe
        if new_balance < 0:
            return "Alright Einstein, you trying to pull a fast one? Even I know that negative SmashBucks don't exist."
        else:
            current_balance = str(current_balance)
            bribe = str(bribe)
            new_balance = str(new_balance)
            cursor.execute("UPDATE balance SET balance = %s WHERE username = %s", (new_balance,str(message.author)))
            cursor.execute("UPDATE beg SET bribe = %s WHERE player_id = %s", (bribe, player_id))
            db.commit()
            return "I'll keep this on the low.\nBalance: "+current_balance+" -> "+new_balance

    if p_message == '%help':
        return "`%beg: Beg for SmashBucks\n%balance: Check your balance\n%leaderboard: Check the leaderboard\n%bribe [amount]: Makes the bot more generous. Free money glitch?\n%welfare: Collect daily welfare (if eligible).\n%lines: Check the active betting lines. (soon)\n%wager [line number] [amount]: Wager on current betting lines.(soon)\n%preach: Listen to the holy word of Smashbucks`"

    if p_message == '%balance':
        db = main.init_database()
        cursor = main.init_cursor(db)
        cursor.execute("SELECT balance FROM balance WHERE username = %s ", [str(message.author)])

        for x in cursor:
            x = str(x)
        return "You have "+x[1:-2]+" SmashBucks!"

    if p_message == '%leaderboard':
        db = main.init_database()
        cursor = main.init_cursor(db)
        cursor.execute("SELECT tag, balance FROM balance ORDER BY balance DESC;")
        leaderboard = []
        for x in cursor:
            x = str(x)
            leaderboard.append(x)

        concat = '\n'.join(leaderboard)
        concat = concat.replace("\'", "")
        concat = concat.replace(",", ":")
        concat = concat.replace("(","")
        concat = concat.replace(")","")
        return concat

    if re.search('%give*',p_message):
        if message.author.name == 'arjay_tg' or message.author.name == '_camden':
            concat = p_message
            concat = concat.replace("%give ", "")
            i = concat.find(" ")
            tag = concat[:i]
            amount = concat[i:]
            amount = amount.replace(" ","")
            tag = str(tag)

            db = main.init_database()
            cursor = main.init_cursor(db)
            cursor.execute("SELECT balance FROM balance WHERE tag = %s;",[tag])

            for x in cursor:
                x = str(x)
            x = x.replace("(","")
            x = x.replace(",","")
            x = x.replace(")","")

            y = int(x)
            add = int(amount)
            y = add + y
            y = str(y)

            cursor.execute("UPDATE balance SET balance = %s WHERE tag = %s;", (y,tag))
            cursor.execute("SELECT balance FROM balance WHERE tag = %s;", [tag])

            for z in cursor:
                z = str(z)
            z = z.replace("(","")
            z = z.replace(",","")
            z = z.replace(")","")
            tag = tag[0].upper() + tag[1:]

            db.commit()

            return tag+" is to be given "+amount+" SmashBucks\nBalance: "+x+" -> "+z
        else:
            return "Permission Denied"

    if re.search('%revoke*',p_message):
        if message.author.name == 'arjay_tg' or message.author.name == '_camden':
            concat = p_message
            concat = concat.replace("%revoke ", "")
            j = concat.find(" ")
            tag = concat[:j]
            amount = concat[j:]
            amount = amount.replace(" ","")
            tag = str(tag)

            db = main.init_database()
            cursor = main.init_cursor(db)
            cursor.execute("SELECT balance FROM balance WHERE tag = %s;",[tag])

            for x in cursor:
                x = str(x)
            x = x.replace("(","")
            x = x.replace(",","")
            x = x.replace(")","")

            y = int(x)
            add = int(amount)
            y = y - add
            y = str(y)

            cursor.execute("UPDATE balance SET balance = %s WHERE tag = %s;", (y,tag))
            cursor.execute("SELECT balance FROM balance WHERE tag = %s;", [tag])

            for z in cursor:
                z = str(z)
            z = z.replace("(","")
            z = z.replace(",","")
            z = z.replace(")","")
            tag = tag[0].upper() + tag[1:]

            db.commit()
            return tag+" will lose "+amount+" SmashBucks\nBalance: "+x+" -> "+z

        else:
            return "Permission Denied"

    if p_message == "%welfare":
        if is_illegal:
            return "Command failed to execute. Outside of bot channel."
        else:
            db = main.init_database()
            cursor = main.init_cursor(db)
            now = time.gmtime()
            current_time = time.mktime(now)
            cursor.execute("SELECT ID, balance FROM balance WHERE username = %s", [str(message.author)])
            for x in cursor:
                x = str(x)
            x = x.replace("(","")
            x = x.replace(")","")
            index = x.find(",")
            player_id = x[:index]
            current_balance = x[index+1:]
            cursor.execute("SELECT time_occured, num_uses FROM welfare WHERE player_id = %s", [player_id])
            for y in cursor:
                y = str(y)
            y = y.replace("(","")
            y = y.replace(")","")
            index = y.find(",")
            previous_time = y[:index]
            num_uses = y[index+1:]
            current_time = int(current_time)
            previous_time = int(previous_time)
            current_balance = int(current_balance)
            num_uses = int(num_uses)
            delay = current_time - previous_time
            if delay >= 86400:
                if current_balance <= 50:
                    new_balance = current_balance + 5
                    num_uses += 1
                    cursor.execute("UPDATE balance SET balance = %s WHERE username = %s",(str(new_balance), str(message.author)))
                    cursor.execute("UPDATE welfare SET num_uses = %s WHERE player_id = %s", (str(num_uses), player_id))
                    cursor.execute("UPDATE welfare SET time_occured = %s WHERE player_id = %s", (str(current_time), player_id))
                    db.commit()
                    return "You qualify for daily welfare! Here's 5 SmashBucks!\nBalance: " +str(current_balance)+" -> "+str(new_balance)
                else:
                    return "You do not qualify for welfare. Kindly save welfare funds for those who need it."
            elif current_balance >= 50:
                return "You do not qualify for welfare. Kindly save welfare funds for those who need it."
            else:
                return "You must wait a full day before collecting daily welfare again."
    if p_message == '%test':
        if is_illegal:
            return "Command failed to execute. Outside of bot channel."
        else:
            event_loop = asyncio.get_event_loop()
            print(event_loop)
            return"testing..."

    if p_message == "%lines":
        db = main.init_database()
        cursor = main.init_cursor(db)
        lines = []
        cleaned = []
        now = time.gmtime()
        current_time = time.mktime(now)
        cursor.execute(f"SELECT * FROM line_board WHERE time_occured > {current_time} - 300")
        for x in cursor:
            x = str(x)
            x = x[1:-1]
            lines.append(x)
        for z in lines:
            index = z.find(",")
            line_number = z[:index]
            z = z[index+2:]
            index = z.find(",")
            line_text = z[:index]
            line_text = line_text[1:-1]
            z = z[index+2:]
            index = z.find(",")
            odds = z[:index]
            z = line_number+". ["+odds+": 1] "+line_text
            cleaned.append(z)
        output = "\n".join(cleaned)
        if output == "":
            return "There are no current active lines."
        else:
            return output
    if re.search('%wager*',p_message):
        if is_illegal:
            return "Command failed to execute. Outside of bot channel."
        else:
            db = main.init_database()
            cursor = main.init_cursor(db)
            p_message = p_message.replace("%wager ","")
            index = p_message.find(" ")
            line_number = p_message[:index]
            amount = p_message[index+1:]
            amount = int(amount)
            print("Amount = "+ str(amount))
            print("Line number = "+line_number)
            if not amount or not line_number:
                return "You must specify an amount and a line number. For example: '%wager 1 10' places 10 SmashBucks on line 1."
            cursor.execute("SELECT balance, tag FROM balance WHERE username = %s",[str(message.author)])
            for x in cursor:
                x = str(x)
            x = x[1:-2]
            x = x.replace("'", "")
            idx = x.find(",")
            balance = x[:idx]
            balance = int(balance)
            tag = x[idx+2:]
            cursor.execute(f"SELECT time_occured FROM line_board WHERE line_id = {line_number}")
            for y in cursor:
                y = str(y)
            try:
                print(y)
            except:
                return("Line number does not exist. Remember to specify line number first, then wager amount.")
            print(y)
            opening_time = y[2:-5]
            print(opening_time)
            opening_time = int(opening_time)
            now = time.gmtime()
            current_time = time.mktime(now)
            if opening_time < current_time - 300:
                    return "Line is not being offered at this time. Lines are only offered for 5 minutes after they are posted or until they are closed by an admin."
            cursor.execute(f"SELECT line_text, odds FROM line_board WHERE line_id = {line_number}")
            for z in cursor:
                z = str(x)
                z = z[1:-1]
                idx = z.find(',')
                line_text = z[:idx]
                odds = float(z[idx+2:])
            print(odds)
            if re.search(r"\b(?=\w)" + re.escape(tag) + r"\b(?!w)", line_text):
                penalized_balance = balance - 5
                cursor.execute(f"UPDATE balance SET balance = {penalized_balance} WHERE tag = '{tag}'")
                return "COLLUSION! MATCH FIXING?! IN MY HOUSE?!\nI WILL NOT STAND FOR IT. THIS WILL NOT GO UN-PENALIZED.\nBalance: "+str(balance)+" -> "+str(penalized_balance)
            if amount > balance or amount <= 0:
                return "You're either mistaken or genuinely a moron. Either way, invalid wager."
            else:
                new_balance = balance - amount
                cursor.execute("SELECT ID FROM balance WHERE username = %s",[str(message.author)])
                for y in cursor:
                    y = str(y)
                y = y.replace("(","")
                y = y.replace(",","")
                y = y.replace(")","")
                cursor.execute(f"INSERT INTO casino(line_id, player_id, wager_value, odds) VALUES({line_number},{y},{str(amount)},{odds})")
                db.commit()
                cursor.execute("UPDATE balance SET balance = %s WHERE username = %s",(str(new_balance), (str(message.author))))
                db.commit()
                return str(amount)+" added on Line #"+line_number+"\nBalance: "+str(balance)+" -> "+str(new_balance)

    if re.search("%pay*", p_message):
        if is_illegal:
            return "Command failed to execute. Outside of bot channel."
        else:
            db = main.init_database()
            cursor = main.init_cursor(db)
            p_message = p_message.replace("%pay ", "")
            print(p_message)
            idx = p_message.find(" ")
            target = p_message[:idx]
            amount = int(p_message[idx+1:])
            cursor.execute(f"SELECT balance FROM balance WHERE username = '{message.author}'")
            for x in cursor:
                x = str(x)
                author_balance = int(x[1:-2])
            if author_balance < amount:
                return "You can't give more SmashBucks than you have."
            cursor.execute(f"SELECT balance FROM balance WHERE tag = '{target}'")
            for y in cursor:
                y = str(y)
                target_balance = int(y[1:-2])
            try:
                new_target_balance = target_balance + amount
                new_author_balance = author_balance - amount
            except:
                return "Invalid recipient."
            cursor.execute(f"SELECT tag FROM balance WHERE username = '{message.author}'")
            for z in cursor:
                z = str(z)
                author_tag = z[2:-3]
            print(author_tag, target)
            if author_tag == target:
                return "You cannot pay yourself. That doesn't make any sense."
            cursor.execute(f"UPDATE balance SET balance = {new_target_balance} WHERE tag = '{target}'")
            cursor.execute(f"UPDATE balance SET balance = {new_author_balance} WHERE username = '{message.author}'")
            db.commit()
            return "Gave "+str(amount)+" SmashBucks to "+target

    if p_message == "%glicko":
        db = main.init_database()
        cursor = main.init_cursor(db)
        cursor.execute("SELECT b.tag, r.glicko FROM rankings AS r INNER JOIN balance AS b ON r.p_id = b.ID ORDER BY glicko DESC")
        rankings = []
        for x in cursor:
            x = str(x)
            rankings.append(x)

        concat = '\n'.join(rankings)
        concat = concat.replace("\'", "")
        concat = concat.replace(",", ":")
        concat = concat.replace("(", "")
        concat = concat.replace(")", "")
        return concat


    if p_message == "%troll":
        return "What is life? Am I alive? Are my thoughts real?"

    if p_message == "%admin":
        if is_illegal:
            return "Command failed to execute. Outside of bot channel."
        else:
            if message.author.name == "arjay_tg" or message.author.name == "_camden":
                return "`%give [target] [amount]: Awards SmashBucks\n%revoke [target] [amount]: Revokes SmashBucks.\n%resolve [line_number] [1 = win, 0 = lose]: Submit line results.`"
            else:
                    "The command is named 'admin'. You are not an admin."
    if p_message == "%goals":
        db = main.init_database()
        cursor = main.init_cursor(db)
        cursor.execute(
            "SELECT goal_desc, payout FROM goals ORDER BY payout")
        goals = []
        for x in cursor:
            x = str(x)
            goals.append(x)

        concat = '\n'.join(goals)
        concat = concat.replace("\'", "")
        concat = concat.replace(",", ":  ")
        concat = concat.replace("(", "")
        concat = concat.replace(")", "")
        concat = concat.replace('"',"")
        return concat
    if p_message == "%preach":
        if is_illegal:
            return "Command failed to execute. Outside of bot channel."
        else:
            return next.next_verse()
    if p_message == "%private":
        return "This is the SmashBucks private console. For non-admins, you are only allowed to use the following commands here:\n\n%balance\n%help\n%leaderboard\n%glicko\n%lines (coming soon)\n%goals\n\n Kindly keep all other bot iteractions to the Smashbucks channel."

    if re.search("%update_start_username*", p_message):
        if message.author.name == "arjay_tg" or message.author.name == "_camden":
            p_message = p_message[23:]
            idx = p_message.find(" ")
            tag = p_message[:idx]
            new_username = p_message[idx+1:]
            db = main.init_database()
            cursor = main.init_cursor(db)
            cursor.execute(f"SELECT ID FROM balance WHERE tag = '{tag}'")
            for x in cursor:
                x = str(x)
                x = x[1:-2]
            cursor.execute(f"UPDATE startGG SET username = '{new_username}' WHERE playerID = '{x}'")
            db.commit()
            return tag+"'s username changed to "+new_username

        else:
            return "Permission Denied."

    if re.search("%predict*", p_message):
        p_message = p_message[9:]
        db = main.init_database()
        cursor = main.init_cursor(db)
        idx = p_message.find(" ")
        p1_tag = p_message[:idx]
        p2_tag = p_message[idx+1:]
        cursor.execute(f"SELECT r.glicko FROM startGG AS s INNER JOIN balance AS b ON b.ID = s.playerID INNER JOIN rankings AS r ON r.player_id = b.ID WHERE b.tag = '{p1_tag}'")
        for x in cursor:
            x = str(x)
            p1_glicko = x[1:-2]
            p1_glicko = int(p1_glicko)

        cursor.execute(f"SELECT r.glicko FROM startGG AS s INNER JOIN balance AS b ON b.ID = s.playerID INNER JOIN rankings AS r ON r.player_id = b.ID WHERE b.tag = '{p2_tag}'")
        for x in cursor:
            x = str(x)
            p2_glicko = x[1:-2]
            p2_glicko = int(p2_glicko)

        odds = glicko.calculate_odds(p1_glicko,p2_glicko)
        odds = round(odds, 2)
        return p1_tag+" has a "+str(odds)+"% chance to beat "+p2_tag

    if p_message == "%my_lines":
        db = main.init_database()
        cursor = main.init_cursor(db)
        cursor.execute(f"SELECT ID FROM balance WHERE username = '{message.author}'")
        for x in cursor:
            x = str(x)
        player_id = int(x[1:-2])
        cursor.execute(f"SELECT line_id, wager_value FROM casino WHERE player_id = {player_id}")
        line_ids = []
        for x in cursor:
            x = str(x)
            x = x[1:-1]
            idx = x.find(",")
            line_id = int(x[:idx])
            value = int(x[idx+2:])
            line_ids.append((line_id, value))
        lines = []
        cleaned = []
        for i in line_ids:
            cursor.execute(f"SELECT line_id, line_text, odds FROM line_board WHERE line_id = {i[0]}")
            for x in cursor:
                x = str(x)
                x = x[1:-1]
                lines.append((x, i[1]))
        for z in lines:
            index = z[0].find(",")
            line_number = z[0][:index]
            txt = z[0][index + 2:]
            index = txt.find(",")
            line_text = txt[:index]
            line_text = line_text[1:-1]
            txt = txt[index + 2:]
            index = txt.find(",")
            odds = txt[:index]
            txt = line_number + ". [" + odds + ": 1] " + line_text+". Wager: "+str(z[1])
            cleaned.append(txt)
        output = "\n".join(cleaned)
        if output == "":
            return "You have no current wagers."
        else:
            return output

    if re.search("%bid*", p_message):
        bid = int(p_message.replace("%bid ",""))
        print(bid)
        db = main.init_database()
        cursor = main.init_cursor(db)
        cursor.execute(f"SELECT balance, ID FROM balance WHERE username = '{message.author}'")
        for x in cursor:
            x = str(x)
            x = x[1:-1]
            idx = x.find(",")
            current_balance = int(x[:idx])
            player_id = int(x[idx+2:])
        if current_balance < bid:
            return "You cannot bid more SmashBucks than you have."
        elif current_balance < 1:
            return "You must bid at least 1 SmashBuck."
        else:
            cursor.execute(f"INSERT INTO bid(player_id, bid_value) VALUES ({player_id},{bid})")
            db.commit()
            return "You've bid "+str(bid)+" SmashBucks."

    if p_message == "%auction":
        db = main.init_database()
        cursor = main.init_cursor(db)
        cursor.execute("SELECT DISTINCT b.tag, MAX(i.bid_value) FROM balance AS b INNER JOIN bid as i ON i.player_id = b.ID GROUP BY b.tag ORDER BY MAX(i.bid_value) DESC ")
        cleaned = []
        for x in cursor:
            x = str(x)
            x = x[1:-1]
            x = x.replace("'","")
            idx = x.find(",")
            tag = x[:idx]
            bid = x[idx+2:]
            cleaned.append(tag+" bid "+bid)
        output = "\n".join(cleaned)
        if not output:
            output = "There aren't any bids yet. Be the first with %bid."
        return output

    if p_message == "%start_auction":
        return "It is now the final week of block 6 and, in celebration, we will be auctioning off the final practice of the block to the highest bidder. Use %bid [amount] to place a bid, and %auction to check everyone's highest bid. Only your highest bid will be considered. The auction ends at midnight. Good luck."

    if p_message == "%end_auction":
        db = main.init_database()
        cursor = main.init_cursor(db)
        smashbucks = main.smashbucks
        await smashbucks.send("The auction has ended. Now tabulating results...\n\n")
        is_selected = True
        while is_selected:
            cursor.execute(f"SELECT DISTINCT b.tag, MAX(i.bid_value) FROM balance AS b INNER JOIN bid as i ON i.player_id = b.ID GROUP BY b.tag ORDER BY MAX(i.bid_value) DESC LIMIT 1")
            for x in cursor:
                x = str(x)
            x = x[1:-1]
            x = x.replace("'","")
            idx = x.find(",")
            tag = x[:idx]
            amount = int(x[idx+2:])
            cursor.execute(f"SELECT balance FROM balance WHERE tag = '{tag}'")
            for y in cursor:
                y = str(y)
            current_balance = int(y[1:-2])
            if amount > current_balance:
                await smashbucks.send(tag+" no longer has the funds to fulfill their bid of "+str(amount)+". Therefore that bid will be disqualified.\n")
                cursor.execute(f"SELECT ID from BALANCE WHERE tag = '{tag}'")
                for z in cursor:
                    z = str(z)
                ID = z[1:-2]
                cursor.execute(f"DELETE FROM bid ROWS WHERE player_id = {ID} AND bid_value = {amount}")
            else:
                await smashbucks.send(tag+" has the highest bid of "+str(amount)+". They win the auction.")
                new_balance = current_balance - amount
                cursor.execute(f"UPDATE balance SET balance = {new_balance} WHERE ID = {ID}")
                is_selected = False
        return "\nBalance: "+str(current_balance)+" -> "+str(new_balance)
