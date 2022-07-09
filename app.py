import os
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, send_from_directory
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from configparser import ConfigParser
from helpers import *

# Configure application
app = Flask(__name__, static_folder="static")

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show project readme"""
    return render_template("index.html")


@app.route("/static/favicon.ico")
@login_required
def fav():
    print(os.path.join(app.root_path, 'static'))
    return send_from_directory(app.static_folder, 'favicon.ico')


@app.route("/evaluatedFormatTesting")
@login_required
def evaluatedFormatTesting():
    return render_template("evaluatedFormatTesting.html")


# @app.route("/historicalData", methods=["GET", "POST"])
# @login_required
# def historicalData():
#     if request.method == "GET":
#         return render_template("historicalData.html")


@app.route("/evaluate", methods=["GET", "POST"])
@login_required
def evaluate():
    """Lookup/calculate company price, growth rate, management numbers, and sticker price"""
    if request.method == "GET":
        return render_template("evaluate.html")

    if request.method == "POST":
        sym = request.form.get("symbol")

        if iex_get_quote(request.form.get("symbol")):
            stock_quote = iex_get_quote(request.form.get("symbol"))
            name = stock_quote["name"]
            price = float(stock_quote["price"])
        else:
            flash("Request failed. Is symbol valid?")        

        # get financial reports dataframe
        df = read_financial_reports(sym)

        # plug parsed json files into helper functions
        management_check, df_mgt = management(df)
        df_history, df_growth = growth(df)
        df_growth.drop("EPS", inplace=True)
        df_growth.fillna("-", inplace=True)
        df_overview = read_overview(sym)
        stickerPrice, safePrice, analystGrowthRate, growthRate = sticker_price(df, df_overview)

        # TODO what does this do?
        df_mgt.index.name = None
        df_growth.index.name = None

        # Calculate some final evaluation figures and buy rating
        discount = 1 - (price / stickerPrice)

        if stickerPrice > 0 and discount > 0:
            undervalued = True
        else:
            undervalued = False

        if price < safePrice:
            fullyDiscounted = True
        else:
            fullyDiscounted = False

        # Company growth and mgt checks: 
        growth_check = df_growth["pass"].all()

        if growth_check:
            growth_message = "Wonderful!"
        else:
            growth_message = "Not wonderful"

        if management_check:
            management_message = "Wonderul!"
        else:
            management_message = "Not wonderful"

        # Calculate buy rating
        rating = "Uncertain"
        
        if growth_check and management_check:
            if discount >= .5:
                rating = "Fully Discounted! Very Strong Buy!"
            elif discount >= .3:
                rating = "Strong Buy"
            elif discount >= .15:
                rating = "Buy"
            elif discount >= .05:
                rating = "Consider Buying"
            elif -.10 < discount < .05:
                rating = "Hold"
            else:
                rating = "Consider Selling"



        # Send all the data to evaluated.html
        return render_template('evaluated.html', name=name, price=usd(price), sym=sym.upper(), rating=rating,
                               growth_message=growth_message, management_message=management_message,
                               discount=pct(discount), analystGrowthRate=pct(analystGrowthRate), 
                               growthRate=pct(growthRate), tables=[df_mgt.to_html(classes='data'), 
                               df_growth.to_html(classes='data'), df_history.to_html(classes='data')],
                               titles=["na", "Management", "Growth", "History"], stickerPrice=usd(stickerPrice), 
                               safePrice=usd(safePrice), undervalued=undervalued, 
                               fullyDiscounted=fullyDiscounted)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        flash("You logged in successfully")
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    # User reached route via GET (as by clicking a link or via redirect)
    if request.method == "GET":
        return render_template("register.html")

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure password was confirmed
        elif not request.form.get("confirmation"):
            return apology("must provide password confirmation", 400)

        # Ensure password and password confirmation match
        elif request.form.get("confirmation") != request.form.get("password"):
            return apology("passwords do not match", 400)

        else:
            # Query database to see if username already exists
            un = request.form.get("username")
            pw = request.form.get("password")
            pw_hash = generate_password_hash(pw)

            if db.execute("SELECT * FROM users WHERE username = ?", un):
                return apology("username already exists", 400)
            else:
                # create new user, saving username and hashed password
                db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", un, pw_hash)
                rows = db.execute("SELECT * FROM users WHERE username = ?", un)
                session["user_id"] = rows[0]["id"]

                # flash a welcome message to the new user
                flash("Welcome, new user!")
                # Redirect user to home page
                return redirect("/")