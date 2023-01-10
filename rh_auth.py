#macos commands to store auth as environment variables
#   export robinhood_username="your_username_here"
#   export robinhood_password="your_password_here"

import robin_stocks as rs

def login(robin_user, robin_pass, sms):
    try:
        rs.robinhood.authentication.login(username=robin_user,
                password=robin_pass,
                expiresIn=86400,
                by_sms=sms)
    except NameError:
        print("Error logging in")
def logout():
    rs.robinhood.authentication.logout()

