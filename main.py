import os
import robin_stocks as rs
import rh_auth as auth
import messages as msg
import time
import queue

# Methods
# 
# #
# Description: changes the format of the api string to a more comparable string
# Input: open_dict, a dictionary from the robinhood api about the open positions
# Return: option_string, a reduced ready to compare to evas, ex: "SPY 400.0000 call 2023-01-12"
# #
def format_open_position_dict(open_dict):
    float_strike = float(open_dict['strike_price'])
    return f"{open_dict['chain_symbol']} {float_strike:.2f} {open_dict['type']} {open_dict['expiration_date']}"

# 
# #
# Description: authenticates user login to robinhood with sms code
# Returns: Discord token
# #
def login():
    #Robinhood Login
    robin_user = os.environ.get("robinhood_username")
    robin_pass = os.environ.get("robinhood_password")
    discord_token = os.environ.get("discord_token")
    sms = True
    auth.login(robin_user, robin_pass, sms)
    return discord_token

#
# #
# Description: logout user
# #
def logout():
    auth.logout()

# 
# #
# Descriptions: gets my open positions from rh account, must be logged in
# Returns: list, with users positions
# # 
def get_open_option_positions():
    acc_open_data = rs.robinhood.options.get_open_option_positions()
    my_positions = []
    for open_opt in acc_open_data:
        opt_id = open_opt['option_id']
        open_opt_data = rs.robinhood.options.get_option_instrument_data_by_id(opt_id)
        open_opt_str = format_open_position_dict(open_opt_data)
        my_positions += [open_opt_str]
    return my_positions

# 
# #
# Description: Open position if its available on RH
# Input: list, list
# #
def open_pos_if_available(pos, my_positions):
    pos_split = pos.split(" ")
    symbol, strike, type, exp_date, price = pos_split[2],format(float(pos_split[3]), '.4f'),pos_split[4],pos_split[5],pos_split[6]
    if symbol == 'SPX':
        symbol = 'SPY'
        strike = format(float(strike)/10, '.4f')
    pos_str = f"{symbol} {strike} {type} {exp_date}"
    if pos_str not in my_positions:
        print("To open: "+ pos_str)
        try:
            rs.robinhood.options.find_options_by_expiration_and_strike(symbol,exp_date,strike,type)
            availbl = True
        except:
            availbl = False
        #Open the position, with size of 1 for now
        if availbl:
            # BTO to open, buying is debit, STC to close, selling is credit
            # Example: rs.robinhood.orders.order_buy_option_limit('open','debit', price, symbol, 1, expiration_date, strike, type, 'ioc', True)
            answer = input("Confirm to open "+pos_str+"? y/n\n")
            if answer == 'y':
                print("Opened: "+pos_str)
                resp = rs.robinhood.orders.order_buy_option_limit('open','debit', price, symbol, 1, exp_date, strike, type, 'ioc', True)
                print(resp)
            else:
                return False
        else:
            return False

#Main

print("Initializing eva trades capture...")
discord_tk = login()
trades_seen = []
q1 = queue.Queue()
while True:
    #Gets evas open positions from discord, format:'2023-01-10 20:51:47.370000 CAT 200 put 2023-03-17 1.58'
    evas_positions = msg.retrieve_option_messages('1022585814183575603', discord_tk)
    my_options = get_open_option_positions()

    #Capture unseen positions from eva and queue them
    for eva_pos in evas_positions:
        if eva_pos not in trades_seen:
            q1.put(eva_pos)
    
    print(f"Positions to process: {list(q1.queue)}")

    #Dequeue to process 
    while not q1.empty():
        position = q1.get()
        if open_pos_if_available(position, my_options):
            print("Confirmed position open!")
        else:
            print("Cancelled position open!")
        #add to seen positions
        trades_seen.append(position)
    time.sleep(5)
