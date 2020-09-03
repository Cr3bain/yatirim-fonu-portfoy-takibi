import sqlite3
import pandas as pd
import os


def Excel():
    try:
        os.remove("fonlar.db")
    except FileNotFoundError:
        pass
    con = sqlite3.connect("fonlar.db")
    df = pd.read_excel("fonlar.xlsx", sheet_name=None,  names=["fonadi", "fonkodu"])
    try:
        for sheet in df:
            df[sheet].to_sql("tefas", con, schema=None, index=False)
    except ValueError:
        print("Dosya tekrar oluşturuluyor")

    finally:
        con.commit()
        con.close()
        print("Fon veritabanı dosyası oluşturuldu\n")
