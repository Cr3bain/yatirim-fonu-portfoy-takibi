import sqlite3
import pandas as pd
import os


def __dir__():
    os.remove("fonlar.db")
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

__dir__()
