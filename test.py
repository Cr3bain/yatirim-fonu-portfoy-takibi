import sqlite3
con = sqlite3.connect("fonlar.db")
cursor = con.execute("select fonadi from tefas WHERE fonkodu ='IPJ'")
print(cursor.fetchall()[0][0])