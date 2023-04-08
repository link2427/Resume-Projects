import os
import discord
import config
import random
import pytarkov
import pyowm
import time
import threading
import uberduckapi as ud
from google.cloud import vision_v1
from google.cloud.vision_v1 import types
from discord.ext import commands
from yahoo_fin import stock_info as si
from datetime import datetime

#API CALLS
os.environ[
    'GOOGLE_APPLICATION_CREDENTIALS'] = 'link-bot-346204-235b6a0a4e81.json'
tarkovclient = pytarkov.PyTarkov(config.tarkov_API_key)
visionclient = vision_v1.ImageAnnotatorClient()
uduck = ud.UberDuck(os.environ['UBERDUCK_Key'], os.environ['UBERDUCK_Secret'])
OpenWMap = pyowm.OWM(config.weather_API_key)
mgr = OpenWMap.weather_manager()
global lukemuted
lukemuted = 0
intents = discord.Intents().all()
bot = commands.Bot(command_prefix='!', intents=intents)


#READY EVENT
@bot.event
async def on_ready():
    print('We have logged in as %s' % bot.user)
    print(__file__)
    #config.threadname.clear()
    # OFFLINE MODE: 
    #await bot.change_presence(status=discord.Status.offline)


#INVALID COMMAND ERROR HANDLING
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        msg = await ctx.send('Invalid Command')
        time.sleep(2)
        await ctx.message.delete()
        await msg.delete()


@bot.command()
async def join(ctx):
    await ctx.author.voice.channel.connect()
    await ctx.send('Joined: %s' %ctx.author.voice.channel)


@bot.command()
async def leave(ctx):
    await ctx.guild.voice_client.disconnect() 


@bot.command()
async def invite(ctx):
    await ctx.send(
        'https://discord.com/api/oauth2/authorize?client_id=958910996699807787&permissions=8&scope=bot'
    )


@bot.command()
async def grongle(ctx):
    await ctx.send(random.choice(config.joshroasts))


#UBERDUCK VOICE COMMAND
@bot.command()
async def voice(ctx, *arg1):

    userid = ctx.message.author.id
    channelid = ctx.channel.id

    if userid in config.threadname:
        await ctx.message.delete()
        await ctx.channel.send('You are already computing a voice!')
    else:
        config.threadname.append(userid)
        userid = threading.Thread(target=voicethread,
                                  args=(ctx, arg1, channelid, userid))
        userid.start()
        await ctx.channel.send('Computing...')
        await ctx.message.delete()


#VOICE THREAD
def voicethread(ctx, arg1, channelid, userid):
    print('In thread')
    try:

        threadNumber = threading.activeCount()
        activeThreads = str(threadNumber)
        print('Current Active Threads ' + (activeThreads))

        soundName = arg1[0] + ".mp3"
        sound = uduck.get_voice(arg1[0].lower(), " ".join(arg1[1:]))

        if sound:
            sound.save(soundName)
            channel = bot.get_channel(channelid)
            bot.loop.create_task(channel.send(file=discord.File(soundName)))
            os.remove(soundName)
            config.threadname.remove(userid)
    except Exception as a:
        print("```\nError: %s\n```" % a)
        config.threadname.remove(userid)


#UBERDUCK VOICE HELP COMMAND
@bot.command()
async def voicehelp(ctx):
    await ctx.channel.send('Voice Options: https://app.uberduck.ai/quack-help')


#IMAGE DETECTION COMMAND
@bot.command()
async def image(message):
    await message.delete()
    try:
        url = message.attachments[
            0].url  # If the user's message has an image attached -> return image url
        #print (url) # Debug print statement

        # Static Vars
        image = types.Image()
        image.source.image_uri = url
        v_dataLabel = visionclient.label_detection(image=image)
        v_dataFace = visionclient.face_detection(image=image)
        embed = discord.Embed(color=0x60D9FF)
        embed.set_image(url=url)

        try:
            filterStrength = float(message.content.split()[1])
        except Exception as a:
            if len(message.content.split()) > 1:
                await message.channel.send("```\nError: %s\n```" % a)
            filterStrength = 0.8

        for label in v_dataLabel.label_annotations:
            if label.score >= filterStrength:  # Checking for high certainty
                embed.add_field(name=label.description,
                                value=round(label.score, 2),
                                inline=True)

        #will only run if a face is detected
        for face_detection in v_dataFace.face_annotations:
            facial_expressions = {
                #'key' : value
                'Expression Certainty': face_detection.detection_confidence,
                'Happiness': face_detection.joy_likelihood,
                'Sadness': face_detection.sorrow_likelihood,
                'Surprise': face_detection.surprise_likelihood,
                'Anger': face_detection.anger_likelihood
            }

            for key in facial_expressions:
                if round(facial_expressions[key], 2) >= 3:
                    embed.add_field(name="Facial Expression",
                                    value=key,
                                    inline=True)

        await message.channel.send(embed=embed)
    except IndexError:
        pass  # Doesn't need a message because it checks everytime there is an instance of "image"
    except discord.errors.HTTPException:
        await message.channel.send(
            'Exceeded API rate limit. Please wait before sending anotehr image.'
        )


#TARKOV PRICE COMMAND
@bot.command()
async def price(ctx, *arg):
    try:
        arg = ' '.join(arg)
        item = tarkovclient.get_item_by_name(arg)
        embed = discord.Embed()
        embed.set_author(name=item.name, url=item.wiki_link)
        embed.set_image(url=item.img_big)
        embed.add_field(name='**Market Price**',
                        value=('₽ %s' % item.price),
                        inline=True)
        embed.add_field(
            name='**Trader Sell Price**',
            value=('%s %s' % (item.trader_price_currency, item.trader_price)),
            inline=True)
        embed.add_field(name='**Avg Price Over 7d**',
                        value=('₽ %s' % item.avg_7d_price),
                        inline=True)
        await ctx.send(embed=embed)
    except pytarkov.pytarkov.PyTarkov.InvalidItem:
        msg = await ctx.send('Invalid Input')
        time.sleep(1)
        await ctx.message.delete()
        await msg.delete()


#WEATHER COMMAND
@bot.command()
async def weather(ctx, *arg):

    await ctx.message.delete()
    arg = ' '.join(arg)
    Weather = mgr.weather_at_place(arg)
    WeatherData = Weather.weather
    temp = WeatherData.temperature('fahrenheit')
    status = WeatherData.detailed_status
    #prcp = WeatherData.rain
    humid = WeatherData.humidity

    embed = discord.Embed()
    embed.set_author(name='Weather in %s' % arg)
    embed.add_field(name='**Temperature: **',
                    value=('%s' % temp.get("temp")),
                    inline=True)
    embed.add_field(name='**Humidity: **', value=('%s' % humid), inline=True)
    embed.add_field(name='**Status: **', value=('%s' % status), inline=True)
    await ctx.send(embed=embed)


#SAY COMMAND
@bot.command()
async def say(ctx, *arg):
    await ctx.send(' '.join(arg))
    await ctx.message.delete()


#DICE COMMAND
@bot.command()
async def dice(ctx, arg):
    sides = int(arg)
    roll = (random.randint(1, sides))
    await ctx.send(roll)


#COINFLIP COMMAND
@bot.command()
async def coinflip(ctx):
    coinside = random.randint(0, 1)
    if coinside:
        embed = discord.Embed()
        embed.title = 'Result:'
        embed.set_image(
            url=
            'https://www.streamscheme.com/wp-content/uploads/2020/08/5Head-Emote.png'
        )
        await ctx.send(embed=embed)

    elif not coinside:
        embed = discord.Embed()
        embed.title = 'Result:'
        embed.set_image(
            url=
            'https://static.wikia.nocookie.net/sega/images/4/49/Tails-Sonic-Forces-Speed-Battle.png/revision/latest/top-crop/width/360/height/450?cb=20210915183529'
        )
        await ctx.send(embed=embed)


#STOCKPRICE COMMAND
@bot.command()
async def stockprice(ctx, arg):
    arg = arg.upper()
    embed = discord.Embed()
    embed.title = arg
    embed.description = ("currentvalue: $%.2f" % si.get_live_price(arg))
    await ctx.send(embed=embed)


@bot.command()
async def togglelukemute(ctx):
    global lukemuted
    if (lukemuted == 0):
        lukemuted = 1
        await ctx.send('SILENCE MONGREL!')
    else:
        lukemuted = 0
        await ctx.send('-50 BRAIN CELLS')


#LISTENER
@bot.listen()
async def on_message(message):

    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    msgStr = message.content
    msgList = msgStr.lower().split()

    if message.author == bot.user:
        return

    if "/image" in msgList:
        await image(message)

    if 'hello' in msgList:
        await message.channel.send('Hello!')

    wordLower = msgStr.lower()
    if any(word in wordLower for word in config.sad_words):
        await message.channel.send(random.choice(config.encouragements))

    #LOGGING
    logFile = open("log.txt", "a")
    if (message.author.id == config.lastID):
        logFile.write("%s\n" % (message.content))
    else:
        logFile.write("\n%s\t%s\n%s\n" %
                      (message.author.name, current_time, message.content))
    logFile.close()

    config.lastID = message.author.id

    if (lukemuted == 1):
        if (message.author.id == 216661523219742720):
            await message.delete()


bot.run(config.botToken)
