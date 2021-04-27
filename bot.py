#!/opt/ncbot/python36/bin/python3
import random,os,discord,json
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
    random_index = random.randrange(0,len(files))
    f = image_dir+files[random_index]
    json_data = {}
    with open(image_tracker_file) as g:
        json_data = json.load(g)
        if f not in json_data.keys():
            json_data[f] = 1
        else:
            json_data[f] = json_data[f] + 1
    with open(image_tracker_file,'w') as g:
        json.dump(json_data,g)
    unseen_images = len(files) - len(json_data.keys())
    return discord.File(f),json_data[f],unseen_images

def createMotivational():
    image_dir = "/opt/ncbot/Images/"
    files = os.listdir(image_dir)
    random_index = random.randrange(0,len(files))
    f = image_dir+files[random_index]
    my_image = Image.open(f)
    my_font = ImageFont.truetype("/opt/ncbot/fonts/comic.ttf", 50)
    random_index = random.randrange(0,len(quotes))
    random_quote = quotes[random_index]
    image_editable = ImageDraw.Draw(my_image)
    colors = [(245,78,66),(255,0,0),(0,255,0),(0,0,255),(255,255,255)]
    color = colors[random.randrange(0,len(colors))]
    image_editable.text((15,15), random_quote, color, font=my_font)
    my_image.save("/opt/ncbot/output/motivation.jpg")
    return discord.File("/opt/ncbot/output/motivation.jpg")

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
        json_data[my_id] = {'Points': 0}
    if message.content == "!level":
        msg = "You currently have: %d xp. You are a %s" % (json_data[my_id]['Points'],json_data[my_id]['Level'])
        await message.channel.send(msg)
    for word in message.content.split(' '):
        if word in keywords:
            json_data[my_id]['Points'] = json_data[my_id]['Points'] + 10

    # Handle quotes
    if message.content == "!quote":
        json_data[my_id]['Points'] = json_data[my_id]['Points'] + 100
        response = getQuote()
        await message.channel.send(response)

    # Create motivational
    if message.content == "!motivate":
        image_file = createMotivational()
        json_data[my_id]['Points'] = json_data[my_id]['Points'] + 1000
        await message.channel.send(file=image_file)

    # Handle frames
    if message.content == "!frame":
        image_file,times_seen,unsent_images = getImage()
        msg = ""
        if times_seen == 1 and unsent_images == 0:
            json_data[my_id]['Points'] = json_data[my_id]['Points'] + 10000000
            msg = "This is a new frame! Wow! There are no new frames remaining. You are insane!"
        elif times_seen == 1:
            json_data[my_id]['Points'] = json_data[my_id]['Points'] + 1000
            msg = "This is a brand spankin' new frame! There are %d new frames remaining!" % unsent_images
        else:
            json_data[my_id]['Points'] = json_data[my_id]['Points'] + 100
            msg = "This frame has been seen %d times. There are %d new frames remaining." % (times_seen,unsent_images)
        await message.channel.send(msg,file=image_file)

    # help message
    if message.content == "!help":
        response = "Hello I'm the Nostalgia Bot. I quote it so you don't have to. Simply use !quote and I will repeat a line from Nostalgia Critic: The Wall...or is it Nostalgia Critic's The Wall? I never know where to put the 's' there. If you type !frame I will send a random still from the movie! !level will display a user's current cult status. !motivate will create a motivational image to get you through the day"
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

