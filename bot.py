import discord
import responses
import auto_wager_loop
import re
import main


async def send_message(message, user_message, is_private, is_update, is_bid):  # Takes in messages and their metadata from the on_message trigger. Outputs the message to discord.
    try:
        if (not message.author.name == "_camden") and (not message.author.name == "arjay_tg") and (not message.channel.id == 1203022860340166758) and (not is_bid):
            # decides if the both should be executing a given command
            response = responses.handleResponse(user_message, message, is_illegal=True)
        else:
            response = responses.handleResponse(user_message, message, is_illegal=False)
        if message.author.name == "_camden" or message.author.name == "arjay_tg":  # gives admins the ability to use private and update commands
            if is_private:
                await message.author.send(response)
            elif is_update:
                message.channel.id = 1203022860340166758 # the channel id for Cornell Esports' Smashbucks channel
                await message.channel.send(response)
            else:
                await message.channel.send(response)
        else:
            await message.channel.send(response) #responds to all other messages normally. Non-commands will fail due to response being blank

    except Exception as e:
        print(e)


async def run_discord_bot():
    TOKEN = main.TOKEN
    client = main.client
    smashbucks = main.smashbucks

    @client.event  # the client event decorator matches the function name (on_ready) to prexisting discord.py functions. On_ready is called when the bot inits and runs properly.
    async def on_ready():
        print(f'{client.user} is now running!')

    @client.event # on_message is called whenever a message is sent in a channel where the bot exists.
    async def on_message(message):
        if message.author == client.user:  # don't respond to messages sent by the bot itself.
            return




        username = str(message.author)
        user_message = str(message.content)
        if user_message[0] == '*':  # the special character used to indicate a private command
            user_message = user_message[1:]
            await send_message(message, user_message, is_private=True, is_update=False, is_bid=False)
        elif user_message[0] == '^': # the special character used to indicate an updating command
            user_message = user_message[1:]
            await send_message(message, user_message, is_private=False, is_update=True, is_bid=False)
        elif re.search("%auto_wager_start*", user_message): # the auto_wager_protocol creates a second asnycio loop that manages wagering on a given start.gg bracket
            if username == 'arjay_tg' or username == '_camden': # only admins can start the protocol
                idx = user_message.find(" ")
                slug = user_message[idx+1:]
                await message.channel.send("Started auto wager protocol on " + slug)
                await auto_wager_loop.start_loop(slug)
            else:
                await message.channel.send("Permission Denied")
        elif re.search("%bid*", user_message) or re.search("%private", user_message):  #allows non-admins to use typically admin-only perks under certain circumstances
            await send_message(message, user_message, is_private=False, is_update=False, is_bid=True)
        elif user_message == "%remote test":
            await smashbucks.send("Hooray. This message is not a response to an inputted discord command. I'm free.")
        else:
            await send_message(message, user_message, is_private=False, is_update=False, is_bid=False)
    await client.start(TOKEN, reconnect=True) # starts the bot
