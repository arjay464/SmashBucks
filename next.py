import main


def next_verse():
    cursor = main.cursor
    db = main.db
    verses = []
    cursor.execute("SELECT verse_text FROM bag WHERE picked = 0 LIMIT 1")
    for x in cursor: 
        x = str(x)
        verses.append(x)
    if not verses:
        cursor.execute("UPDATE bag SET picked = 0")
        db.commit()
        cursor.execute("SELECT verse_text FROM bag WHERE picked = 0 LIMIT 1")
        for x in cursor:
            x = str(x)
            verses.append(x)
    output = verses[0]
    output = output[1:-2]
    cursor.execute(f"UPDATE bag SET picked = 1 WHERE verse_text = {output}")
    db.commit()
    output = output.replace("'", "")
    output = output.replace('"','')
    output = output.replace("#", "\n\n")
    return output
