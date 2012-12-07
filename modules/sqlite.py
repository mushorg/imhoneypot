import sqlite3

class SQLiteDB():
    """
    Class to log events into a SQLite database
    """
    def __init__(self, logger):
        self.logger = logger

    def create(self):
        # Creates the database if it doesn't exist already.
        db = sqlite3.connect('db/sqlite.db')
        cursor = db.cursor()
        try:
            cursor.execute("CREATE TABLE IF NOT EXISTS log(id integer primary key, time text, attacker text, message text)")
        except sqlite3.DatabaseError, e:
            self.logger.log_console("SQLite error: %s " % e, "critical")
        else:
            db.commit()
            db.close()

    def drop(self):
        # Drops the whole database if it exists
        db = sqlite3.connect('db/sqlite.db')
        cursor = db.cursor()
        try:
            cursor.execute("DROP TABLE IF EXISTS log")
        except sqlite3.DatabaseError, e:
            self.logger.log_console("SQLite error: %s " % e, "critical")
        else:
            db.commit()
            db.close()

    def insert(self, attack_time, attacker, message):
        # Writes an event into the database
        db = sqlite3.connect('db/sqlite.db')
        cursor = db.cursor()
        sql = "INSERT INTO log values(NULL, ?, ?, ?)"
        try:
            cursor.execute(sql, (attack_time, attacker, message.encode('utf-8')))
        except sqlite3.DatabaseError, e:
            self.logger.log_console("SQLite error: %s" % e, "critical")
        else:
            db.commit()
            db.close()

    def show(self):
        # Shows the database content
        db = sqlite3.connect('db/sqlite.db')
        cursor = db.cursor()
        try:
            cursor.execute("SELECT * FROM log")
        except sqlite3.DatabaseError, e:
            self.logger.log_console("SQLite error: %s " % e, "critical")
        else:
            for row in cursor:
                print row
            db.commit()
            db.close()