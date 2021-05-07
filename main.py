import discord
import os
import requests
import json
import random
from replit import db
from keep_alive import keep_alive
import lists
import time

client = discord.Client()
#channel_id = os.environ['CHANNEL']

###### DATABASE CHECKS /START ######
## Used to trigger automatic reponses from the bot and more.
if "responding" not in db.keys():
	db["responding"] = True
###### DATABASE CHECKS /END ######

###### FUNCTIONS /START ######
## Extracts a quote from webpage, changes to json, creates a readable string and returns it.
def get_quote():
	response = requests.get(lists.quotes_url)
	json_data = json.loads(response.text)
	quote = json_data[0]["q"] + " -" + json_data[0]["a"]
	return (quote)

## Adds a new msg in the encouragements database.
def update_encouragements(encouraging_message):
	if "encouragements" in db.keys():
		encouragements = db["encouragements"]
		encouragements.append(encouraging_message)
		db["encouragements"] = encouragements
	else:
		db["encouragements"] = [encouraging_message]

## Deletes an object from the encouragements database.
def delete_encouragment(index):
	encouragements = db["encouragements"]
	if index < len(encouragements):
		index = index - 1
		del encouragements[index]
		db["encouragements"] = encouragements

## Adds a fish to the ocean.
def add_fish(new_fish):
	if "ocean" in db.keys():
		ocean = db["ocean"]
		ocean.append(new_fish)
		db["ocean"] = ocean
	else:
		db["ocean"] = ocean

## Removes a fish from the ocean.
def remove_fish(index):
	ocean = db["ocean"]
	if index < len(ocean):
		index = index - 1
		del ocean[index]
		db["ocean"] = ocean

###### FUNCTIONS /END ######
###### BOT RESPONSES ######

@client.event
async def on_ready():
	#print("We have logged in as {0.user}".format(client))
	#print(f"We have logged in as {client.user}")
	print(db["responding"])
	print(db["encouragements"])
	print(db["ocean"])
	print("*********")
	channel = client.get_channel(818827445141504050)
	await channel.send(lists.bot_starts)


@client.event
async def on_message(message):

	if message.author == client.user:
		return

## Shorts.
	msg = message.content
	reply = message.channel.send

## Returns a list of all avaiable commands.
	if msg.startswith("$help"):
		list_of_commands = "\n".join(map(str, lists.all_commands))
		help_reply = f"{message.author.mention} {list_of_commands}"
		await reply(help_reply)

## Prints all entries of all the specified databases.
	if msg.startswith("$list_all_databases_entries"):
		inspo_value = db["encouragements"]
		fish_value = db["ocean"]
		print(f"***\n{fish_value}")
		print(f"***\n{inspo_value}")

## wipes the whole database.
#  if msg.startswith("$delete_entire_database"):
#    await reply("Database cleared.")

## Returns an inspiring quote.
	if msg.startswith("$inspire"):
		quote = get_quote()
		bot_reply = f"{message.author.mention} here is a message for you: \n {quote}"
		await reply(bot_reply)

## Toggles auto-reply of sad_words.
	if msg.startswith("$toggle"):
		if db["responding"] == True:
			db["responding"] = False
			await reply("Responding is now off.")
		else:
			db["responding"] = True
			await reply("Responding is now on.")

## Checks if toggle is on/off, if on, gives auto-reply for sad_words and $fish.
	if db["responding"]:
		encourage_options = lists.starter_encouragements
		if "encouragements" in db.keys():
			encourage_options = encourage_options + db["encouragements"]
		if any(word in msg for word in lists.sad_words):
			await reply(random.choice(encourage_options))
		fish_options = lists.default_fish
		if "ocean" in db.keys():
			fish_options = fish_options + db["ocean"]
		if msg.startswith("$fish"):
			await reply(random.choice(fish_options))

## Adds object to encouragements database.
	if msg.startswith("$add-inspo"):
		encouraging_message = msg.split("$add-inspo ", 1)[1]
		update_encouragements(encouraging_message)
		await reply("New encouraging message added.")

## Deletes object from encouragements database.
	if msg.startswith("$del-inspo"):
		encouragements = []
		remaining_entries = " "
		if "encouragements" in db.keys():
			index = int(msg.split("$del-inspo", 1)[1])
			delete_encouragment(index)
			encouragements = db["encouragements"]
			for i in encouragements:
				remaining_entries = remaining_entries + f"{i}\n"
				update_encouragements_response = f"Removed entry as requested. Remaining entries are the following:\n{remaining_entries}"
		await reply(update_encouragements_response)

## Returns a list of all items in encouragements database.
	if msg.startswith("$list-inspo"):
		list_to_show = " "
		encouragements = []
		if "encouragements" in db.keys():
			encouragements = db["encouragements"]
			for i in encouragements:
				list_to_show = list_to_show + f"{i}\n"
		await reply(f"Behold the list of encouragement:\n{list_to_show}")

## Add new fish to the ocean.
	if msg.startswith("$add-fish"):
		new_fish = msg.split("$add-fish ", 1)[1]
		add_fish(new_fish)
		await reply("New fish added to ocean.")

## Remove a fish from the ocean
	# TODO: något är fel i borttagningen, den kan inte ta bort item på pos[1]
	if msg.startswith("$del-fish"):
		ocean = []
		remaining_entries = " "
		if "ocean" in db.keys():
			index = int(msg.split("$del-fish ", 1)[1])
			remove_fish(index)
			ocean = db["ocean"]
			for i in ocean:
				remaining_entries = remaining_entries + f"{i}\n"
				updated_ocean = f"Removed fish as requested. Remaining fish are the following:\n{remaining_entries}"
		await reply(updated_ocean)

	if msg.startswith("$list-fish"):
		list_to_show = " "
		ocean = []
		if "ocean" in db.keys():
			ocean = db["ocean"]
			for i in ocean:
				list_to_show = list_to_show + f"{i}\n"
		await reply(f"These are all the fish in the ocean:\n{list_to_show}")

### Derp commands: ###

	if msg.startswith("$tolle"):
		await reply("Ta din skit och gå härifrån.")

	if any(word in msg.lower() for word in lists.hello_words):
		await reply(lists.boat_hello)

	if any(word in msg.lower() for word in lists.table_flip):
		await reply(random.choice(lists.table_flip_response))

	if msg.startswith("$bestgifeu"):
		with open('images/sausage.gif', 'rb') as f:
			picture = discord.File(f)
		await reply(file=picture)

	if msg.startswith("$mys"):
		with open('images/cat-vibe.gif', 'rb') as f:
			picture = discord.File(f)
		await reply(file=picture)
	
	if msg.startswith("$wat"):
		with open('images/wat.gif', 'rb') as f:
			picture = discord.File(f)
		await reply(file=picture)

	if msg.startswith("$gg"):
		string_to_google = msg.split("$gg ", 1)[1]
		url = "https://www.google.com/search?q=" + string_to_google.replace(" ", "+")
		await reply(url)

	if msg.startswith("$bot"):
		url = "https://www.youtube.com/watch?v=RYQUsp-jxDQ"
		await reply(url)
	
	if msg.startswith("$timestartsnow"):
		# t = 30
		url = "https://www.youtube.com/watch?v=73tGe3JE5IU"
		await reply(url)

	if "flame" in msg:
		await reply("Hey, flame is a pretty cool guy")


###### BOT RESPONSES /END ######

keep_alive()
client.run(os.getenv("TOKEN"))