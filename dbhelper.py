import sqlite3
import pandas as pd


class DBHelper:

    def __init__(self, dbname="moti.sqlite"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname, isolation_level=None)

    def setup(self):
        tblstmt = "CREATE TABLE IF NOT EXISTS quotes (description text)"
        quoteidx = "CREATE INDEX IF NOT EXISTS quoteIndex ON quotes (description ASC)"
        self.conn.execute(tblstmt)
        self.conn.execute(quoteidx)
        tblstmt2 = "CREATE TABLE IF NOT EXISTS owners (owner text, last_quote text, time text DEFAULT '2100')"
        owneridx = "CREATE UNIQUE INDEX IF NOT EXISTS ownerIndex on owners (owner ASC)"
        self.conn.execute(tblstmt2)
        self.conn.execute(owneridx)
        self.conn.commit()

    def add_quote(self, quote_text):
        stmt = "INSERT INTO quotes (description) VALUES (?)"
        args = (quote_text,)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def delete_quote(self, quote_text):
        stmt = "DELETE FROM quotes WHERE description = (?)"
        args = (quote_text,)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def get_quotes(self):
        stmt = "SELECT description FROM quotes"
        return [x[0] for x in self.conn.execute(stmt)]

    def get_random_quote(self):
        stmt = "SELECT description FROM quotes ORDER BY RANDOM() LIMIT 1"
        return self.conn.execute(stmt).fetchone()[0]

    def clear_all_quotes(self):
        self.conn.execute("DELETE FROM quotes")

    def add_user(self, owner):
        stmt = "INSERT INTO owners (owner) VALUES (?)"
        args = (owner,)
        try:
            self.conn.execute(stmt, args)
        except sqlite3.IntegrityError:
            return
        self.conn.commit()

    def get_users(self):
        stmt = "SELECT owner FROM owners"
        return [x[0] for x in self.conn.execute(stmt)]

    def get_last_quote(self, owner):
        stmt = "SELECT last_quote FROM owners WHERE owner = (?)"
        args = (owner,)
        return self.conn.execute(stmt, args).fetchone()[0]

    def update_last_quote(self, owner, quote_text):
        stmt = "UPDATE owners SET last_quote = (?) WHERE owner = (?)"
        args = (quote_text, owner)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def get_time_to_send(self, owner):
        stmt = "SELECT time FROM owners WHERE owner = (?)"
        args = (owner,)
        return [x[0] for x in self.conn.execute(stmt, args)]

    def set_time_to_send(self, owner, time):
        stmt = "UPDATE owners SET time = (?) WHERE owner = (?)"
        args = (time, owner)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def print_tables(self):
        print(pd.read_sql_query("SELECT * FROM quotes", self.conn))
        print()
        print(pd.read_sql_query("SELECT * FROM owners", self.conn))
        print()
