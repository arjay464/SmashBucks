import bot
import mysql.connector
import asyncio
import discord
import configparser

config = configparser.ConfigParser()
configFilePath = r'C:\Users\arjay\PycharmProjects\SmashBucks\venv\file.ini'
config.read(configFilePath)
host = config.get('section_a', 'host')
user = config.get('section_a', 'user')
password = config.get('section_a', 'password')
database = config.get('section_a', 'database')
TOKEN = config.get('section_a', 'token')
smashbucks_id = config.getint('section_a', 'channel')


db = mysql.connector.connect(  # initializes the connection to the mysql db
    host=host,
    user=user,
    passwd=password,
    database=database,
    connection_timeout=178956
)

intents = discord.Intents.default()
intents.message_content = True
intents.guild_scheduled_events = True
client = discord.Client(intents=intents)
smashbucks = client.get_partial_messageable(id=smashbucks_id)

cursor = db.cursor()  # creates a cursor object to interact with the database


if __name__ == '__main__':
    asyncio.run(bot.run_discord_bot())  # starts the main event loop





