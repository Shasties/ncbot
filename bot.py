#!/opt/ncbot/python36/bin/python3
import random,os,discord,json,time
from dotenv import load_dotenv
from PIL import Image, ImageFont, ImageDraw

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()

image_tracker_file = "/opt/ncbot/tracker.json"
stat_tracker_file = "/opt/ncbot/stats.json"
ranks = ['Nostalgia Casual','Nostalgia Fan','Nostalgia Nut','Nostalgia Cultist','Nostalgia Freak','Fennah','The Dictator']
keywords_file = "/opt/ncbot/keywords.json"
keywords = []
types = ['Rock','Paper','Critic']
with open(keywords_file) as f:
    keywords = json.load(f)
quotes_file = "/opt/ncbot/quotes.json"
quotes = []
with open(quotes_file) as f:
    quotes = json.load(f)

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

def getQuote():
    the_script = ""
    script_file = "/opt/ncbot/the_script.txt"
    with open(script_file,"r") as f:
        the_script = f.readlines()
        the_script = [x for x in the_script if x != "\n"]
    random_index = random.randrange(0,len(the_script))
    return the_script[random_index]

def getImage():
    image_dir = "/opt/ncbot/Images/"
    files = os.listdir(image_dir)
    good_to_go = False
    json_data = {}
    random_index = 0
    f = ""
    # generate an unowned frame
    while not good_to_go:
        random_index = random.randrange(0,len(files))
        f = image_dir+files[random_index]
        with open(stat_tracker_file) as g:
            json_data = json.load(g)
            good_to_go = True
            for user in json_data.keys():
                if type(json_data[user]) == dict and f in json_data[user]['Owns']:
                    good_to_go = False

    with open(image_tracker_file) as g:
        json_data = json.load(g)
        if f not in json_data.keys():
            random_index = random.randrange(0,len(types))
            random_type = types[random_index]
            json_data[f] = random_type
    with open(image_tracker_file,'w') as g:
        json.dump(json_data,g)
    unseen_images = len(files) - len(json_data.keys())
    return discord.File(f),unseen_images,f,random_type

def createMotivational(user_id):
    image_dir = "/opt/ncbot/Images/"
    files = os.listdir(image_dir)
    json_data = {}
    with open(stat_tracker_file) as f:
        json_data = json.load(f)
    #random_index = random.randrange(0,len(json_data[user_id]['Owns']))
    #f = json_data[user_id]['Owns'][random_index]
    random_index = random.randrange(0,len(files))
    f = image_dir+files[random_index]
    my_image = Image.open(f)
    my_font = ImageFont.truetype("/opt/ncbot/fonts/comic.ttf", 50)
    random_index = random.randrange(0,len(quotes))
    random_quote = quotes[random_index]
    image_editable = ImageDraw.Draw(my_image)
    colors = [(245,78,66),(255,0,0),(0,255,0),(0,0,255),(255,255,255)]
    color = colors[random.randrange(0,len(colors))]
    image_editable.text((13, 13), random_quote, font=my_font, fill=(0,0,0))
    image_editable.text((17, 13), random_quote, font=my_font, fill=(0,0,0))
    image_editable.text((13, 17), random_quote, font=my_font, fill=(0,0,0))
    image_editable.text((17, 17), random_quote, font=my_font, fill=(0,0,0))
    image_editable.text((15,15), random_quote, color, font=my_font)
    my_image.save("/opt/ncbot/output/motivation.jpg")
    return discord.File("/opt/ncbot/output/motivation.jpg")

# Rock < Paper
# Paper < Critic
# Critic < Rock
def resolveCombat(challenger, starter, cards):
    if str(cards[challenger]) == str(cards[starter]):
        return "tie"
    else:
        if cards[challenger] == 'Paper':
            if cards[starter] == 'Rock':
                return "challenger"
            else: 
                return "starter"
        elif cards[challenger] == 'Rock':
            if cards[starter] == 'Paper':
                return "starter"
            else:
                return "challenger"
        else:
            if cards[starter] == 'Rock':
                return "starter"
            else:
                return "challenger"

@client.event
async def on_message(message):
    response = ""
    json_data = {}
    with open(stat_tracker_file) as f:
        json_data = json.load(f)
    my_id = str(message.author.id)

    # Handle user level/points
    if message.author == client.user:
        return
    if my_id not in json_data.keys():
        json_data[my_id] = {'Points': 0,'DougCoin': 100,'Owns':[],'Wins':0,'Level': ranks[0]}
    json_data[my_id]['name'] = message.author.display_name
    if 'Losses' not in json_data[my_id].keys():
        json_data[my_id]['Losses'] = 0
    if 'Ties' not in json_data[my_id].keys():
        json_data[my_id]['Ties'] = 0
    if message.content == "!stats":
        msg = "You currently have: %d xp and %d DougCoin. You are a %s. You own %d frames and have %d wins. Your W/L/T ratio is %d/%d/%d" % (json_data[my_id]['Points'],json_data[my_id]['DougCoin'],json_data[my_id]['Level'],len(json_data[my_id]['Owns']),json_data[my_id]['Wins'],json_data[my_id]['Wins'],json_data[my_id]['Losses'],json_data[my_id]['Ties'])
        await message.channel.send(msg)
    for word in message.content.split(' '):
        if word in keywords:
            json_data[my_id]['Points'] = json_data[my_id]['Points'] + 10
            json_data[my_id]['DougCoin'] = json_data[my_id]['DougCoin'] + 10

    # Dueling
    if message.content.split(' ')[0] == "!duel":
        if len(json_data[my_id]['Owns']) > 0:
            if json_data['isduel'] == "true" and json_data['starter'] != my_id:
                starter = json_data['starter']
                random_starter_card_index = random.randrange(len(json_data[starter]['Owns'])) 
                random_starter_card = json_data[starter]['Owns'][random_starter_card_index]
                random_challenger_card_index = random.randrange(len(json_data[my_id]['Owns'])) 
                random_challenger_card = json_data[my_id]['Owns'][random_challenger_card_index]
                result = ""
                with open(image_tracker_file,"r") as f:
                    cards = json.load(f)
                    await message.channel.send("%s throws out %s" % (json_data[starter]['name'],cards[random_starter_card]))
                    time.sleep(2)
                    await message.channel.send("%s throws out %s" % (json_data[my_id]['name'],cards[random_challenger_card]))
                    result = resolveCombat(random_challenger_card,random_starter_card,cards)
                if result == "tie":
                    await message.channel.send("Both players drew the same kind of frame.")
                    json_data[starter]['Ties'] = json_data[starter]['Ties']+1
                    json_data[my_id]['Ties'] = json_data[my_id]['Ties']+1
                elif result == "starter":
                    await message.channel.send("%s wins this frame: " % json_data[starter]['name'], file = discord.File(random_challenger_card))
                    json_data[starter]['Owns'].append(random_challenger_card)
                    json_data[starter]['Wins'] = json_data[starter]['Wins']+1
                    json_data[my_id]['Losses'] = json_data[my_id]['Losses']+1
                    json_data[my_id]['Owns'].remove(random_challenger_card)
                else:
                    await message.channel.send("%s wins this frame:" % json_data[my_id]['name'],file = discord.File(random_starter_card))
                    json_data[my_id]['Owns'].append(random_starter_card)
                    json_data[my_id]['Wins'] = json_data[my_id]['Wins']+1
                    json_data[starter]['Losses'] = json_data[starter]['Losses']+1
                    json_data[starter]['Owns'].remove(random_starter_card)
                json_data['isduel'] = "false"
                json_data['starter'] = ""
            else:
                json_data['isduel'] = "true"
                json_data['starter'] = my_id
        else:
            await message.channel.send("You do not have enough frames for this. Buy some first.")

    # Handle quotes
    if message.content == "!quote":
        if json_data[my_id]['DougCoin'] >= 10:
            json_data[my_id]['Points'] = json_data[my_id]['Points'] + 100
            json_data[my_id]['DougCoin'] = json_data[my_id]['DougCoin'] - 10
            response = getQuote()
            await message.channel.send(response)
        else:
            await message.channel.send("You do not have enough DougCoin for this. Use !mine to get more")

    if message.content == "!inventory":
        cards = {}
        num_rock,num_paper,num_crit = 0,0,0
        with open(image_tracker_file,"r") as f:
            cards = json.load(f)
        for frame in json_data[my_id]['Owns']:
            if cards[frame] == "Rock":
                num_rock = num_rock + 1
            if cards[frame] == "Paper":
                num_paper = num_paper + 1
            if cards[frame] == "Critic":
                num_crit = num_crit + 1
        await message.channel.send("You have %d / %d / %d | Rock / Paper / Critic" % (num_rock,num_paper,num_crit))


    # Create motivational
    if message.content == "!motivate":
        if json_data[my_id]['DougCoin'] >= 20:
            #if len(json_data[my_id]['Owns']) == 0:
            #    await message.channel.send("You may only create motivationals of images you own.")
            #else:
            image_file = createMotivational(my_id)
            json_data[my_id]['Points'] = json_data[my_id]['Points'] + 1000
            json_data[my_id]['DougCoin'] = json_data[my_id]['DougCoin'] - 20
            await message.channel.send(file=image_file)
        else:
            await message.channel.send("You do not have enough DougCoin for this. Use !mine to get more.")

    # Handle frames
    if message.content == "!frame":
        if json_data[my_id]['DougCoin'] >= 15:
            image_file,unsent_images,frame_name,frame_type = getImage()
            msg = ""
            if unsent_images == 0:
                json_data[my_id]['Points'] = json_data[my_id]['Points'] + 10000000
                msg = "This is a %s frame. Wow! There are no new frames remaining. You are insane!" % frame_type
            else:
                json_data[my_id]['Points'] = json_data[my_id]['Points'] + 1000
                msg = "This is a %s frame. There are %d new frames remaining." % (frame_type,unsent_images)
            json_data[my_id]['DougCoin'] = json_data[my_id]['DougCoin'] - 15
            json_data[my_id]['Owns'].append(frame_name)
            await message.channel.send(msg,file=image_file)
        else:
            await message.channel.send("You do not have enough DougCoin for this. Use !mine to get more.")

    # Handle mining
    if message.content == "!mine":
        random_number = random.randrange(1,10) * 10
        json_data[my_id]['DougCoin'] = json_data[my_id]['DougCoin'] + random_number
        await message.channel.send("You just mined %d DougCoin!" % random_number)

    if message.content == "!drewbie":
        await message.channel.send("increased odds in your next duel. Maybe.")

    # help message
    if message.content == "!help":
        response = "Hello I'm the Nostalgia Bot. I quote it so you don't have to. Simply use !quote and I will repeat a line from Nostalgia Critic: The Wall...or is it Nostalgia Critic's The Wall? I never know where to put the 's' there. If you type !frame I will send a random still from the movie! !stats will display a user's current cult status. !motivate will create a motivational image to get you through the day. !mine will grant you more DougCoin. !duel will challenge another player for one of your frames. !inventory will display the makeup of your frames."
        await message.channel.send(response)

    points = json_data[my_id]['Points']
    level = ranks[0]
    # J A N K
    for i in range(len(ranks),0,-1):
        num = 10
        for g in range(i):
            num = num*10
        if points >= num:
            level = ranks[i-1]
            break
    json_data[my_id]['Level'] = level
    json_data[my_id]['Points'] = points
    with open(stat_tracker_file,"w") as f:
        json.dump(json_data,f)

client.run(TOKEN)

