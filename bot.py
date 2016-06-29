import pyowm
import time
import random
import datetime
import telepot
import wikipedia
import json
import os
from pyshorteners import Shortener
import subprocess
import bs4
import requests
import youtube_dl

api = ''  # API Key for OpenWaetherMap 
api_key = '' #API key for Google(Url shortening) 
owm = pyowm.OWM(api)
forecast = owm.daily_forecast("Delhi,in") # Weather forecast details
tomorrow = pyowm.timeutils.tomorrow()
forecast.will_be_sunny_at(tomorrow)
observation = owm.weather_at_place('Delhi,in')  #Hardcoding the weather place to be delhi,Soon add functionality to autodetect location
w = observation.get_weather() 
def handle(msg):
    chat_id = msg['chat']['id']  # Stores chat id for referencing message
    command = msg['text'] # Filters text from the message sent

    print ('Got command: %s' % command)
   # Here Starts the command interpretation
    if command == '/roll':
        bot.sendMessage(chat_id, random.randint(1,6))
    
    elif command == '/time':
        bot.sendMessage(chat_id, str(datetime.datetime.now()))
    
    elif command == '/hi':
        bot.sendMessage(chat_id, "Hello")
    
    elif command == '/weather':
        bot.sendMessage(chat_id,"New Delhi,India\n" + w.get_detailed_status() + "\n\nTemperature Detials:\n" + str(w.get_temperature(unit='celsius'))+ "\n\nWind Speed Details:\n" + str(w.get_wind())+"\n\nCloud Coverage: \n" + str(w.get_clouds())+"%"+"\n\nHumidity: \n" + str(w.get_humidity())+"%"+"\n\nPressure Details :\n" + str(w.get_pressure())+"\n\nData fetched by openweathermap API.All copyrights reserved")
    
    elif '/wiki' in command :
        ny = wikipedia.summary(command[5:len(str(command))],sentences = 7)
        bot.sendMessage(chat_id,ny)
    
    elif command == '/help' :
        bot.sendMessage(chat_id,"""List of supported commands is\n
/hi - Greet Your Device\n
/roll - Rolls a dice\n
/weather - Tells detailed current weather report of Raspberry Pi's location\n
/time - Tells current date and time\n
/wiki <Topic Name> - Does a topic search on wikipedia and gives a summary of the topic.Try long tapping /wiki in autofill\n
/torrent <magnet link/torrent url/infohash> - Adds and downloads torrent to your raspberry pi remotely\n
/torrent_status - Give the detailed status of your torrent(s) you have added/downloaded\n
/url <URL> - Shorten the given URL using Google API(goo.gl).\n
/url_exp <Shortened URL> - Expands the given shortened url made using Google API\n
/speedtest - Does a detailed network speed test using ookla's speedtest API\n
/yt <Youtube video link> - Creates the shortened download link for given youtube video\n
/news <Topic> - Displays top 10 latest headlines fetched by Google News API about given toipc using Beautiful soup py Library.
\n\nSee your autofill for quick selection of command or tap '/' icon on right side of your chat textbox.\n
For Commands with parameters,you can long tap the autosuggestion for quick typing and type your parameter followed by a space.""")
    
    elif '/torrent ' in command :
        os.system("deluge-console add Desktop "+command[8:len(str(command))])
        bot.sendMessage(chat_id,"Torrent Successfully added")  
    
    elif command == '/torrent_status':
        p = os.popen("deluge-console info")
        q = p.read()
        bot.sendMessage(chat_id,str(q))
        p.close()
    
    elif '/url ' in command :
        url = str(command[5:len(command)])
        bot.sendMessage(chat_id,"Shortened URL is\n" + str(shortener.short(url)))
    
    elif '/url_exp ' in command:
        url = str(command[9:len(command)])
        bot.sendMessage(chat_id,"Expanded URL is\n" + shortener.expand(url))
    
    elif command == '/speedtest':
        bot.sendMessage(chat_id,"""Wait for a while until we check and measure speed of system's network.
If result does'nt come in 30 seconds,Try again.Little patience is appreciated...""")
        p = str(subprocess.check_output(["speedtest-cli"]))
        q = p[2:len(p)-1]
        r = q.replace("\\r","")
        s = r.split("\\n")
        bot.sendMessage(chat_id,'\n'.join(s))
    
    elif '/news ' in command :
        headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'}

        tempurl = "https://www.google.com/search?q=%s&num=10&start=10&tbm=nws#q=%s&tbas=0&tbs=sbd:1&tbm=nws&gl=d"
        news_topic = command[6:]
        url = tempurl % (news_topic,news_topic)

        ahrefs = []
        titles = []


        req = requests.get(url, headers=headers)
        soup = bs4.BeautifulSoup(req.text, "html.parser")

        #you don't even have to process the div container
        #just go strait to <a> and using indexing get "href"
        #headlines
        ahref  = [a["href"] for a in soup.find_all("a", class_="_HId")]
        #"buckets"
        ahref += [a["href"] for a in soup.find_all("a", class_="_sQb")]
        ahrefs.append(ahref)

        #or get_text() will return the array inside the hyperlink
        #the title you want
        title =  [a.get_text() for a in soup.find_all("a", class_="_HId")]
        title += [a.get_text() for a in soup.find_all("a", class_="_sQb")]
        titles.append(title)

        #print(ahrefs)
        titles = str(titles)
        titles = titles.strip("[[]]")
        titles = titles.replace("u'",'u"')
        titles = titles.split('u"')
        bot.sendMessage(chat_id, "Top 10 latest news headlines for the given topic are\n"+ "\n\n->".join(map(str,titles)))

    elif '/yt ' in command :
        bot.sendMessage(chat_id,"Wait until we create the download link,Sitback and relax..")
        url = command[4:len(command)]
        ydl = youtube_dl.YoutubeDL({'outtmpl': '%(id)s%(ext)s'})

        with ydl:
             result = ydl.extract_info(url,download=False) # We just need the info

        if 'entries' in result:
          # Can be a playlist or a list of videos
          video = result['entries'][0]
        else:
           # Just a video
           video = result
           video_url = video['url']
           p = shortener.short(video_url)
           bot.sendMessage(chat_id,"Download link for given youtube video is:\n" + p)

    else :
        bot.sendMessage(chat_id,"Type /help for list of supported commands till now,There are many more to come!!")

# Here is the Telegram Bot API key

key = '' # API key for telegram bot
bot = telepot.Bot(key) 
bot.message_loop(handle) # Calling bot and keeping it active infinitely
print ('I am listening ...')

while 1:
    time.sleep(10)
    
