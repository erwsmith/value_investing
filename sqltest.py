from cs50 import SQL
db = SQL("sqlite:///finance.db")
# print(db.execute("SELECT SUM(value) FROM holdings WHERE owner_id = 11")[0]['SUM(value)'])
# print(db.execute("SELECT shares FROM holdings WHERE owner_id = ? AND symbol = ?", 11, "MSFT")[0]["shares"])
print(db.execute("SELECT value FROM holdings WHERE owner_id = ? AND symbol = ?", 11, "MSFT")[0]["value"])