import discord
import json, urllib.request, requests
from ratelimit import limits, sleep_and_retry
from ranked import ranked_search
from normals import normals_search
from win_trade import win_trade_search
import os



TOKEN = str(os.environ.get('discord_token'))

client = discord.Client()

key = str(os.environ.get('riot_api_key'))


@sleep_and_retry
@limits(calls = 95, period = 120) 
@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return
    author_id = message.author
    if message.content == '!rules':
        await message.channel.send('Type !rank, !flex, !norm, !wint (wintrade) or !aram followed by a summoner name to search their history and see who that person\'s \
played with for the last 90 games of the specified game mode. If you have any other questions ask me (ahurpdurp).')
        return  
    if message.content.startswith('!ranked'):
        await message.channel.send('Remember, start with !rank, not !ranked. Try again :)')
        return  
    if message.content.startswith('!wint') or message.content.startswith('!rank') or message.content.startswith('!norm') or message.content.startswith('!flex') or message.content.startswith('!aram'):
        account_name = message.content[6:]        
        sum_id_URL = 'https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/'+ account_name + '?api_key=' + key 
        try:
            summoner_info = requests.get(sum_id_URL).json()
            account_id = summoner_info['accountId']
            summoner_id = summoner_info['id']
        except:
            await message.channel.send('Hmm, that summoner doesn\'t exist. Try again :(')
            return
        if message.content.startswith('!rank'):
            await ranked_search(account_name,account_id,summoner_id,key,message)
        elif message.content.startswith('!wint'):
            await win_trade_search(account_name,account_id,summoner_id,key,message)
        elif message.content.startswith('!norm') or message.content.startswith('!flex') or message.content.startswith('!aram'):
            await normals_search(account_name,account_id,summoner_id,key,message,message.content[1:5])
@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run(TOKEN)