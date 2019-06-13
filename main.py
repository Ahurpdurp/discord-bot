import discord
import json, urllib.request, requests
from ratelimit import limits, sleep_and_retry

TOKEN = 'NTg4NTExMzcxNDE5OTc1NzI2.XQGOTA.xinDTyeelyEpcC9qNo-mUi4OotY'

client = discord.Client()

key = 'RGAPI-95b049b8-974b-4335-9137-ceaaa236e3f7'


@sleep_and_retry
@limits(calls = 95, period = 120) 
@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if message.content == '!expose':
        await message.channel.send('Make sure you enter a summoner name after typing the !expose command')
        return    

    if message.content.startswith('!expose'):
        account_name = message.content[8:]        
        sum_id_URL = 'https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/'+ account_name + '?api_key=' + key 
        try:
            summoner_info = requests.get(sum_id_URL).json()
            account_id = summoner_info['accountId']
            summoner_id = summoner_info['id']
        except:
            await message.channel.send('Hmm, that summoner doesn\'t exist. Try again :(')
            return

        player_ranking_URL = "https://na1.api.riotgames.com/lol/league/v4/entries/by-summoner/"+ summoner_id +"?api_key=" + key 
        player_ranking_info = requests.get(player_ranking_URL).json()

        for queue_type in player_ranking_info:
            if queue_type['queueType'] == 'RANKED_SOLO_5x5':
                await message.channel.send(account_name + f'\'s current rank is: {queue_type["tier"].capitalize()} {queue_type["rank"]}')
                break
        else:
            await message.channel.send("Hmm, " + account_name + " isn\'t ranked in solo/duo right now. There might be some results from earlier seasons though.")
        await message.channel.send("Loading results...")
        match_history_url = 'https://na1.api.riotgames.com/lol/match/v4/matchlists/by-account/' + account_id + '?queue=420&endIndex=50&api_key=' + key
        match_history_data = requests.get(match_history_url).json()
        match_id_list = []
        for match in match_history_data['matches']:
            match_id_list.append(match['gameId'])
        print(match_id_list)
        player_list = {}
        for match in match_id_list:
            match_id = match
            match_url = 'https://na1.api.riotgames.com/lol/match/v4/matches/' + str(match_id) + '?api_key=' + key
            match_details = requests.get(match_url).json()
            team_side = []
            for player in match_details['participantIdentities']:
                if player['player']['accountId'] == account_id:
                    if player['participantId'] in [1,2,3,4,5]:
                        team_side = [0,1,2,3,4]
                    else:
                        team_side = [5,6,7,8,9]
            for participantId in team_side:
                if match_details['participantIdentities'][participantId]['player']['accountId'] != account_id:
                    player_name = match_details['participantIdentities'][participantId]['player']['summonerName']
                    player_list[player_name] = player_list.get(player_name,0) + 1
        edited_player_list = player_list.copy()
        for player_key in player_list:
            if player_list[player_key] == 1:
                del edited_player_list[player_key]
        ordered_player_list = sorted(edited_player_list.items(), key=lambda x: x[1], reverse=True)  
        if len(ordered_player_list) == 0:
            await message.channel.send("You haven't duoed with anyone recently...damn")
            return
        total_duoed_games = 0
        for x in ordered_player_list:
            await message.channel.send(f'Summoner Name: {x[0]} | Total Games Duoed: {x[1]} | Percent Duoed With This Person: {round(((x[1]/len(match_id_list)) * 100),2)}%')
            total_duoed_games += x[1]
        if 100 * total_duoed_games/len(match_id_list) > 100:
            await message.channel.send(f'Overall, {account_name} has duoed 100% of his/her games.')
            return
        await message.channel.send(f'Overall, {account_name} has duoed {round(100 * total_duoed_games/len(match_id_list), 2)}% of his/her games.')

    
@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run(TOKEN)