import CONFIG
import time
from flask import Flask, redirect, request
from donationalerts import DonationAlertsAPI, Scopes

app = Flask(__name__)
api = DonationAlertsAPI(CONFIG.bot.CLIENT_ID, CONFIG.bot.CLIENT_SECRET,
                        "http://127.0.0.1:5000/login", [Scopes.USER_SHOW, Scopes.DONATION_INDEX])


@app.route("/", methods=["get"])
def index():
    return redirect(api.login())  # Log in your application


@app.route("/login", methods=["get"])
def login():
    code = request.args.get("code")
    access_token = api.get_access_token(code)

    # user = api.user(access_token)
    donation_list = api.donations_list(access_token)
    donations = {}
    startPage = 1
    lastPage = donation_list.objects['meta']['last_page']
    for currentPage in range(startPage, lastPage, 1):
        donation_list = api.donations_list(access_token, page=currentPage)

        for item in donation_list.objects['data']:
            username = item['username']
            amount = item['amount_in_user_currency']
            if username in donations:
                donations[username] += amount
            else:
                donations[username] = amount

    donations = {k: v for k, v in sorted(
        donations.items(), key=lambda item: item[1])}

    donation_strings = []
    for username in donations:
        if donations[username] % 1 == 0:
            amount_str = str(int(donations[username]))
        else:
            amount_str = "{:.2f}".format(donations[username])
        donation_strings.append("{} -  {}".format(username, amount_str))

    result = "<br>".join(donation_strings)
    return result


if __name__ == "__main__":
    app.run(debug=True)
