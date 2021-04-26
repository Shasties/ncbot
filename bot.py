#!/opt/ncbot/python36/bin/python3
import random,os,discord,json
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()

image_tracker_file = "/opt/ncbot/tracker.json"

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

@client.event
async def on_message(message):
    response = ""
    if message.author == client.user:
        return
    if message.content == "!quote":
        response = getQuote()
        await message.channel.send(response)
    if message.content == "!frame":
        image_file,times_seen,unsent_images = getImage()
        msg = ""
        if times_seen == 1 and unsent_images == 0:
            msg = "This is a new frame! Wow! There are no new frames remaining. You are a Nostalgia Freak!"
        elif times_seen == 1:
            msg = "This is a brand spankin' new frame! There are %d new frames remaining!" % unsent_images
        else:
            msg = "This frame has been seen %d times. There are %d new frames remaining." % (times_seen,unsent_images)
        await message.channel.send(msg,file=image_file)
    if message.content == "!help":
        response = "Hello I'm the Nostalgia Bot. I quote it so you don't have to. Simply use !quote and I will repeat a line from Nostalgia Critic: The Wall...or is it Nostalgia Critic's The Wall? I never know where to put the 's' there. If you type !frame I will send a random still from the movie!"
        await message.channel.send(response)

client.run(TOKEN)

