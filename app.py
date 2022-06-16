import os
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from configparser import ConfigParser
from helpers import apology, login_required, usd, lookup, read_financial_reports, management, growth, iex_get_quote


# Configure application
app = Flask(__name__)

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


@app.route("/evaluate", methods=["GET", "POST"])
@login_required
def evaluate():
    if request.method == "GET":
        return render_template("evaluate.html")

    if request.method == "POST":
        sym = request.form.get("symbol")

    if iex_get_quote(request.form.get("symbol")):
        stock_quote = iex_get_quote(request.form.get("symbol"))
        name = stock_quote["name"]
        price = usd(stock_quote["price"])
    else:
        flash("Request failed. Is symbol valid?")        

        # lookup_functions = ["BALANCE_SHEET", "CASH_FLOW", "INCOME_STATEMENT", "OVERVIEW"]
        # for func in lookup_functions:
        #     lookup(sym, func)

        # read company json files
        b, i, c = read_financial_reports(sym)

        # plug parsed json files into mangement and growth functions
        management_check, df_mgt = management(b, i, c)
        growth_check, df_growth = growth(b, i, c)

        # TODO what does this do?
        df_mgt.index.name = None
        df_growth.index.name = None

        if growth_check:
            growth_message = "WONDERFUL!"
        else:
            growth_message = "NOT GOOD"

        if management_check:
            management_message = "WONDERFUL!"
        else:
            management_message = "NOT GOOD"

        return render_template('evaluated.html', name=name, price=price, sym=sym.upper(), growth_message=growth_message,
                               management_message=management_message, tables=[df_mgt.to_html(classes='data'), 
                               df_growth.to_html(classes='data')], titles=["na",
                               f"{sym.upper()} Management", "Growth"])


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


# @app.route("/quote", methods=["GET", "POST"])
# @login_required
# def quote():
#     """Get stock quote."""

#     if request.method == "GET":
#         return render_template("quote.html")

#     if request.method == "POST":
#         if lookup(request.form.get("symbol")):
#             stock_quote = lookup(request.form.get("symbol"))
#             name = stock_quote["name"]
#             price = usd(stock_quote["price"])
#             symbol = stock_quote["symbol"]
#             return render_template("quoted.html", name=name, price=price, symbol=symbol)
#         else:
#             # flash("Enter a valid symbol.")
#             return apology("Not a valid symbol", 400)


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