import sqlite3
import pandas as pd
import os


def Excel():
    try:
        os.remove("fonlar.db")
    except FileNotFoundError:
        pass
    con = sqlite3.connect("fonlar.db")
    df = pd.read_excel("fonlar.xlsx", sheet_name=None,  names=["fonadi", "poz", "fonkodu"])
    try:
        for sheet in df:
            df[sheet].to_sql("tefas", con, schema=None, index=False)
            con.commit()
            con.close()
            print("Fon listesi başarıyla veritabanına eklendi\n")
    except Exception as hata:
        print("Dosya veritabanına yazılamadı", hata)
