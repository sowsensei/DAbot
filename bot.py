import CONFIG
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

    #user = api.user(access_token)
    donation_list = api.donations_list(access_token)
    donations = {}
    startPage = 1
    lastPage = donation_list.objects['meta']['last_page']
    for currentPage in range(startPage, lastPage, 1):
        donation_list = api.donations_list(access_token, page=currentPage)
        
        for item in donation_list.objects['data']:
            username = item['username']
            amount = item['amount_in_user_currency']
            # Если получатель уже есть в словаре, добавляем к его сумме
            if username in donations:
                donations[username] += amount
            # Иначе создаем новую запись в словаре
            else:
                donations[username] = amount

    return donation_list.objects

if __name__ == "__main__":
    app.run(debug=True)