import bot
import mysql.connector
import asyncio

db = mysql.connector.connect(  # initializes the connection to the mysql db
    host="localhost",
    user='root',
    passwd="#13MCimfmlbpe",
    database="SmashBucks"
)

cursor = db.cursor()  # creates a cursor object to interact with the database


if __name__ == '__main__':
    asyncio.run(bot.run_discord_bot())  # starts the main event loop





