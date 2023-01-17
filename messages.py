import requests
import re
import json
import time
from datetime import datetime

# retrieve_option_messages(string:channelid)
# 
# Desc:This method only works to retrieve Evapandas discord alerts for the current trading day
#
# Input: channelid, discord channel id as a string
# Output: evas_positions, array of robin-stocks api friendly strings with option order information
# ------------
def retrieve_option_messages(channelid, dis_token):
    open_positions =[]
    headers={
        'authorization': dis_token
    }
    r = requests.get(
        f'https://discord.com/api/v9/channels/{channelid}/messages?limit=50',headers=headers)
    
    jsonn = json.loads(r.text)
    
    for value in jsonn:
        embed = value['embeds']
        if embed != []:
            post_time = value['edited_timestamp']
            if post_time == None:
                post_time = value['timestamp']
            post_time = post_time.replace('+','T')
            post_time_arr = post_time.split('T')
            post_time = post_time_arr[0]+" "+post_time_arr[1]
            if post_time_arr[0] == datetime.now().strftime("%Y-%m-%d"):
                past_flag = False
            else:
                past_flag = True
            title = embed[0]['title']
            content = embed[0]['description'].split()
            if title == 'Open' and not past_flag:
                position = content[0]
                tcker = content[1]
                option = content[2]
                option_price = option[:-1]
                
                option_dir = option[-1:]
                if option_dir == "C":
                    option_dir = "call"
                else:
                    option_dir = "put"
                
                date = content[3]
                slashes = date.count('/')
                if slashes == 1:
                    date += "/2023"
                dd = datetime.strptime(date,'%m/%d/%Y').strftime('%Y-%m-%d')
                cost = content[5]
                open_positions += [f"{post_time} {tcker} {option_price} {option_dir} {dd} {cost}"]
    return open_positions

    # 1.check a list of open positions, if not there call method to robinstock to place order,
    # 2.wait for confirmation and add to the list of current orders
    # 3.else ignore the processing


#TODO: 
# DONE separate the string to get all the necessary info for option trading
# -run a while loop constantly requesting, check per timestamp
# -keep track of what is open and closed 
# -edge case where the order doesnt get filled at the price and it gets closed before it even opens 
# -also the volume issue, having multiple closes for the same ticker, targets should be set by me. 
