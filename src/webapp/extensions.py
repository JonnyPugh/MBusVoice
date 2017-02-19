import MySQLdb, MySQLdb.cursors
import config

def connect_to_database():
    options = {
        'host': config.env['host'],
        'user': config.env['user'],
        'passwd': config.env['password'],
        'db': config.env['db'],
        'cursorclass' : MySQLdb.cursors.DictCursor
      }
    db = MySQLdb.connect(**options)
    db.autocommit(True)
    return db
db = connect_to_database()

def execute_query(query):
    cur = db.cursor()
    cur.execute(query)
    results = cur.fetchall()
    cur.close()
    return results
