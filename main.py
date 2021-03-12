import discord
import os
import requests
import json
import random
from replit import db
from keep_alive import keep_alive
import lists


client = discord.Client()

all_commands = [  ### THIS LIST NEEDS TO KEPT UPDATED!
    "here is a list of all commands: ",
    "Note: There are a few hidden commands that are triggered by specific words :)",
    " ",
    "$help - Show this list.",
    "$tolle - Testa så får du se.",
    "$inspire - Get a random inspiring message.",
    "$bestgifeu - The best gif eu!",
    "$mys - Chill." 
    "$gg <words to google> - Googles it for you.",
    " ",
    "$list-inspo - List of manually added inspiring messages.",
    "$del-inspo <num> - Delete inspiring message at position <num>.",
    "$add-inspo <msg> - Add inspiring message",
    " ",
    "$fish - Go fishing!",
    "$list-fish - List of all fish in the ocean.",
    "$add-fish <url> - Add a fish to the ocean.",
    "$del-fish <num> - Remove fish at position <num> from the ocean.",
]

###### DATABASE CHECKS /START ######
## detta används för att trigga automatisk respons på sad_words.
if "responding" not in db.keys():
    db["responding"] = True
###### DATABASE CHECKS /END ######

###### FUNCTIONS /START ######
## hämtar ett citat från hemsida, ändrar till json och sedan till string.
def get_quote():
    response = requests.get(lists.quotes_url)
    json_data = json.loads(response.text)
    quote = json_data[0]["q"] + " -" + json_data[0]["a"]
    return (quote)

## lägger till nytt meddelande i databasen för encouragements.
def update_encouragements(encouraging_message):
    if "encouragements" in db.keys():
        encouragements = db["encouragements"]
        encouragements.append(encouraging_message)
        db["encouragements"] = encouragements
    else:
        db["encouragements"] = [encouraging_message]

## tar bort objekt från encouragements databas.
def delete_encouragment(index):
    encouragements = db["encouragements"]
    if index < len(encouragements):
        index = index - 1
        del encouragements[index]
    db["encouragements"] = encouragements

def add_fish(new_fish):
    if "ocean" in db.keys():
        ocean = db["ocean"]
        ocean.append(new_fish)
        db["ocean"] = ocean
    else:
        db["ocean"] = ocean

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
    print("We have logged in as {0.user}".format(client))
    print(db["responding"])
    print(db["encouragements"])
    print(db["ocean"])
    print("*********")
    channel = client.get_channel(818827445141504050)
    await channel.send(lists.bot_starts)
    

@client.event
async def on_message(message):

## om skribenten av meddelandet är boten så returnas det på en gång för att inte trigga fler kommandon
    if message.author == client.user: 
        return

## genvägar / förkortningar
    msg = message.content
    reply = message.channel.send

## skriver ut en lista på alla tillgängliga kommandon
    if msg.startswith("$help"):
        list_of_commands = "\n".join(map(str, all_commands))
        help_reply = f"{message.author.mention} {list_of_commands}"
        await reply(help_reply)

## prints all entries of all the specified databases.
    if msg.startswith("$list_all_databases_entries"):
        inspo_value = db["encouragements"]
        fish_value = db["ocean"]
        print(f"***\n{fish_value}")
        print(f"***\n{inspo_value}")

## wipes the whole database.
#    if msg.startswith("$delete_entire_database"):
#        await reply("Database cleared.")

## svarar med ett motiverande citat
    if msg.startswith("$inspire"):
        quote = get_quote()
        bot_reply = f"{message.author.mention} here is a message for you: \n {quote}"
        await reply(bot_reply)

## togglar auto-reply på sad_words
    if msg.startswith("$toggle"):
        if db["responding"] == True:
            db["responding"] = False
            await reply("Responding is now off.")
        else:
            db["responding"] = True
            await reply("Responding is now on.")

## Kollar om toggle är av eller på för responding och om den är på ger feedback på sad_words
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

## lägger till objekt i sad_words databas.
    if msg.startswith("$add-inspo"):
        encouraging_message = msg.split("$add-inspo ", 1)[1]
        update_encouragements(encouraging_message)
        await reply("New encouraging message added.")

## tar bort objekt i sad_words databas.
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

## listar alla objekt i sad_words databas.
    if msg.startswith("$list-inspo"):
        list_to_show = " "
        encouragements = []
        if "encouragements" in db.keys():
            encouragements = db["encouragements"]
            for i in encouragements:
                list_to_show = list_to_show + f"{i}\n"
            print(list_to_show)
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
            print(list_to_show)
        await reply(f"These are all the fish in the ocean:\n{list_to_show}")


### Derp AF kommandon här: ###

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

    if msg.startswith("$gg"):
        string_to_google = msg.split("$gg ", 1)[1]
        url = "https://www.google.com/search?q=" + string_to_google.replace(" ", "+")
        await reply(url)


###### BOT RESPONSES /END ######

keep_alive()
client.run(os.getenv("TOKEN"))