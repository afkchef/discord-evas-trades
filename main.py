import os
import robin_stocks as rs
import rh_auth as auth
import messages as msg
import time

robin_user = os.environ.get("robinhood_username")
robin_pass = os.environ.get("robinhood_password")
discord_token = os.environ.get("discord_token")
sms = True


auth.login(robin_user, robin_pass, sms)

positions = msg.retrieve_option_messages('1022585814183575603', discord_token)
play = positions[0].split(" ")
results = rs.robinhood.options.find_options_by_expiration_and_strike(play[2], play[5], play[3], optionType=play[4], info=None)
print(results)
auth.logout()
