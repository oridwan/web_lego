import sqlite3

con = sqlite3.connect('test.db') #, timeout=600)
cur = con.cursor()
cur.execute('SELECT * from Materials where rowid=1')
print(cur.fetchall())
#cur.execute("vacuum")
con.close()
                        
