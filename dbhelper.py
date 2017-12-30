import sqlite3


class DBHelper:

    def __init__(self, dbname="moti.sqlite"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname, isolation_level=None)

    def setup(self):
        tblstmt = "CREATE TABLE IF NOT EXISTS quotes (description text, owner text)"
        quoteidx = "CREATE INDEX IF NOT EXISTS quoteIndex ON quotes (description ASC)"
        ownidx = "CREATE INDEX IF NOT EXISTS ownIndex ON quotes (owner ASC)"
        self.conn.execute(tblstmt)
        self.conn.execute(quoteidx)
        self.conn.execute(ownidx)
        self.conn.commit()

    def add_quote(self, quote_text, owner):
        stmt = "INSERT INTO quotes (description, owner) VALUES (?, ?)"
        args = (quote_text, owner)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def delete_quote(self, quote_text):
        stmt = "DELETE FROM quotes WHERE description = (?)"
        args = (quote_text,)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def get_quotes(self, owner):
        stmt = "SELECT description FROM quotes WHERE owner = (?)"
        args = (owner,)
        return [x[0] for x in self.conn.execute(stmt, args)]

    def get_random_quote(self):
        stmt = "SELECT description FROM quotes ORDER BY RANDOM() LIMIT 1"
        return [x[0] for x in self.conn.execute(stmt)]

    def clear_all(self):
        self.conn.execute("DELETE FROM quotes")
