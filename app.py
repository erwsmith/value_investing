import os
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

'''
export API_KEY=pk_5030d7a395ab442aaf83ee26aae059ef

DELETE FROM holdings;
UPDATE users SET cash = 10000 WHERE id=11;
'''

# finance.db schema:
# CREATE TABLE users (
# id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
# username TEXT NOT NULL,
# hash TEXT NOT NULL,
# cash NUMERIC NOT NULL DEFAULT 10000.00);
# CREATE TABLE sqlite_sequence(name,seq);
# CREATE UNIQUE INDEX username ON users (username);

# CREATE TABLE holdings
# (symbol TEXT NOT NULL,
# cost NUMERIC NOT NULL,
# shares INTEGER NOT NULL,
# value NUMERIC NOT NULL,
# owner_id INTEGER NOT NULL,
# FOREIGN KEY(owner_id) REFERENCES users(id));

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
        if lookup(request.form.get("symbol")):
            stock_quote = lookup(request.form.get("symbol"))
            name = stock_quote["name"]
            price = usd(stock_quote["price"])
            symbol = stock_quote["symbol"]
            return render_template("evaluated.html", name=name, price=price, symbol=symbol)
        else:
            # flash("Enter a valid symbol.")
            return apology("Not a valid symbol", 400)


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


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    if request.method == "GET":
        return render_template("quote.html")

    if request.method == "POST":
        if lookup(request.form.get("symbol")):
            stock_quote = lookup(request.form.get("symbol"))
            name = stock_quote["name"]
            price = usd(stock_quote["price"])
            symbol = stock_quote["symbol"]
            return render_template("quoted.html", name=name, price=price, symbol=symbol)
        else:
            # flash("Enter a valid symbol.")
            return apology("Not a valid symbol", 400)


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


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "GET":
        symbols = db.execute("SELECT symbol FROM holdings WHERE owner_id = ?", session["user_id"])
        return render_template("sell.html", symbols=symbols)

    if request.method == "POST":
        if lookup(request.form.get("symbol")):
            stock_quote = lookup(request.form.get("symbol"))
            name = stock_quote["name"]
            symbol = stock_quote["symbol"]
            price = float(stock_quote["price"])
            shares = float(request.form.get("shares"))
            ext_cost = float(shares * price)
            cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])[0]["cash"]
            shares_owned = db.execute("SELECT shares FROM holdings WHERE owner_id = ? AND symbol = ?",
                                      session["user_id"], symbol)[0]["shares"]
            owned_shares_value = db.execute("SELECT value FROM holdings WHERE owner_id = ? AND symbol = ?",
                                            session["user_id"], symbol)[0]["value"]

            # check if user can afford stocks
            if shares > shares_owned:
                return apology("Not enough shares")
            else:
                # successful sale, update db: add ext_cost to cash
                cash += ext_cost
                db.execute("UPDATE users SET cash = ? WHERE id = ?", cash, session["user_id"])
                # decrease number of shares held and update value in db
                shares_owned -= shares
                owned_shares_value -= ext_cost
                # get new total value of stocks + cash from db
                db.execute("UPDATE holdings SET shares = ?, value = ? WHERE owner_id = ? AND symbol = ?",
                           shares_owned, owned_shares_value, session["user_id"], symbol)
                db.execute("DELETE FROM holdings WHERE shares = 0")
                value_of_stocks = db.execute("SELECT SUM(value) FROM holdings WHERE owner_id = ?",
                                             session["user_id"])[0]['SUM(value)']
                total = cash + value_of_stocks

                rows = db.execute("SELECT * FROM holdings where owner_id = ?", session["user_id"])
                # flash message when rendering index/portfolio page
                flash(f"You have successfully sold {int(shares)} shares of {name} for {usd(ext_cost)}!")
                # redirect user to index/portfolio page
                return render_template("index.html", cash=usd(cash), total=usd(total), rows=rows)