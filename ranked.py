import discord
import json, urllib.request, requests
from ratelimit import limits, sleep_and_retry

async def ranked_search(account_name,account_id,summoner_id,key,message):
    player_ranking_URL = "https://na1.api.riotgames.com/lol/league/v4/entries/by-summoner/"+ summoner_id +"?api_key=" + key 
    player_ranking_info = requests.get(player_ranking_URL).json()
    for queue_type in player_ranking_info:
        if queue_type['queueType'] == 'RANKED_SOLO_5x5':
            await message.channel.send(account_name + f'\'s current rank is: {queue_type["tier"].capitalize()} {queue_type["rank"]}')
            break
    else:
        await message.channel.send("Hmm, " + account_name + " isn\'t ranked in solo/duo right now. There might be some results from earlier seasons though.")
    await message.channel.send("Loading results...")
    match_history_url = 'https://na1.api.riotgames.com/lol/match/v4/matchlists/by-account/' + account_id + '?queue=420&endIndex=90&api_key=' + key
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
        try:
            match_details['participantIdentities']
        except:
            await message.channel.send("Unable to get the recent player's matches. Most likely the API call limit was reached, so wait at least two minutes and try again.")
            return 
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
        if player_list[player_key] in [1,2]:
            del edited_player_list[player_key]
    ordered_player_list = sorted(edited_player_list.items(), key=lambda x: x[1], reverse=True)  
    if len(ordered_player_list) == 0:
        await message.channel.send("You haven't played with anyone recently...damn")
        return
    total_duoed_games = 0
    for x in ordered_player_list:
        await message.channel.send(f'Summoner Name: {x[0]} | Total Games Duoed: {x[1]} | Percent Duoed With This Person: {round(((x[1]/len(match_id_list)) * 100),2)}%')
        total_duoed_games += x[1]
    if 100 * total_duoed_games/len(match_id_list) > 100:
        await message.channel.send(f'Overall, {account_name} has duoed 100% of his/her games.')
        return
    await message.channel.send(f'Overall, {account_name} has duoed {round(100 * total_duoed_games/len(match_id_list), 2)}% of his/her games.')
    await message.channel.send('Disclaimer: a person only shows up if they duoed more than 2 games. There\'s also a chance (especially in higher elos) that some people who show up are just random players \
who happened to be on the same team multiple times.')