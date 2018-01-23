from urllib import parse
import psycopg2

parse.uses_netloc.append("postgres")


class DBHelper:

    def __init__(self,):
        # self.con = psycopg2.connect(database=, user=, password=, host=, port=) #fill this up with your own postgreSQL server
        self.con.autocommit = True
        self.conn = self.con.cursor()

    def setup(self):
        tblstmt = "CREATE TABLE IF NOT EXISTS quotes (description text)"
        quoteidx = "CREATE INDEX IF NOT EXISTS quoteIndex ON quotes (description ASC)"
        self.conn.execute(tblstmt)
        self.conn.execute(quoteidx)
        tblstmt2 = "CREATE TABLE IF NOT EXISTS owners (owner text, last_quote text, time text DEFAULT '2100')"
        owneridx = "CREATE UNIQUE INDEX IF NOT EXISTS ownerIndex on owners (owner ASC)"
        self.conn.execute(tblstmt2)
        self.conn.execute(owneridx)

    def add_quote(self, quote_text):
        stmt = "INSERT INTO quotes (description) VALUES (%s)"
        args = (quote_text,)
        self.conn.execute(stmt, args)

    def delete_quote(self, quote_text):
        stmt = "DELETE FROM quotes WHERE description = (%s)"
        args = (quote_text,)
        self.conn.execute(stmt, args)

    def get_quotes(self):
        stmt = "SELECT ALL description FROM quotes"
        self.conn.execute(stmt)
        return [x[0] for x in self.conn.fetchall()]

    def get_random_quote(self):
        stmt = "SELECT description FROM quotes ORDER BY RANDOM() LIMIT 1"
        self.conn.execute(stmt)
        try:
            return self.conn.fetchone()[0]
        except TypeError:
            raise TypeError

    def clear_all_quotes(self):
        self.conn.execute("DELETE FROM quotes")

    def add_user(self, owner):
        stmt = "INSERT INTO owners (owner) VALUES (%s)"
        args = (owner,)
        try:
            self.conn.execute(stmt, args)
        except psycopg2.IntegrityError:  # owner already exists
            return

    def get_users_and_time(self):
        stmt = "SELECT owner, time FROM owners"
        self.conn.execute(stmt)
        return [(x[0], x[1]) for x in self.conn.fetchall()]

    def get_last_quote(self, owner):
        stmt = "SELECT last_quote FROM owners WHERE owner = CAST ('%s' as text)"
        args = (owner,)
        self.conn.execute(stmt, args)
        return self.conn.fetchone()[0]

    def update_last_quote(self, owner, quote_text):
        stmt = "UPDATE owners SET last_quote = (%s) WHERE owner = CAST ('%s' as text)"
        args = (quote_text, owner)
        self.conn.execute(stmt, args)

    def set_time_to_send(self, owner, time):
        stmt = "UPDATE owners SET time = (%s) WHERE owner = CAST ('%s' as text)"
        args = (time, owner)
        self.conn.execute(stmt, args)
