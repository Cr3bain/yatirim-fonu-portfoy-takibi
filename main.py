# -*- coding:utf-8 -*-

import requests
from bs4 import BeautifulSoup
import colorama
import os.path
from datetime import datetime
import locale
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date, FLOAT
from sqlalchemy.orm import sessionmaker
import sqlite3
import pandas as pd
import numpy as np
from turkce_karakter import turkish_upper


locale.setlocale(locale.LC_ALL, "tr_TR")

veritabani = "fonlarim.db"
engine = create_engine('sqlite:///{}?check_same_thread=False'.format(veritabani))
Base = declarative_base()


class Table(Base):
    __tablename__ = 'fon'
    id = Column(Integer, primary_key=True)
    kullanici = Column(String(length=255), default='default_value')
    fonkodu = Column(String(length=255), default='default_value')
    fiyat = Column(FLOAT, nullable=True)
    tarih = Column(Date, default=datetime.today().date())

    def __repr__(self):
        return self.hesap


Base.metadata.create_all(engine)

fon_listesi = ("İŞ PORTFÖY ROBOFON TEMKİNLİ DEĞİŞKEN FON (İŞ PORTFÖY BİRİNCİ DEĞİŞKEN FON)",
               "İŞ PORTFÖY ROBOFON DENGELİ DEĞİŞKEN FON (İŞ PORTFÖY İKİNCİ DEĞİŞKEN FON)",
               "İŞ PORTFÖY ROBOFON ATAK DEĞİŞKEN FON (İŞ PORTFÖY ÜÇÜNCÜ DEĞİŞKEN FON)",
               "İŞ PORTFÖY PARA PİYASASI FONU",
               "İŞ PORTFÖY ODEABANK PARA PİYASASI FONU",
               "İŞ PORTFÖY PRİVİA BANKACILIK DEĞİŞKEN ÖZEL FON",
               "İŞ PORTFÖY KUMBARA HESABI KARMA ÖZEL FON",
               "İŞ PORTFÖY ELEKTRİKLİ ARAÇLAR KARMA FON")


class isportfoy:
    def __init__(self):
        self.aciklama = "Tefaş Portföy Takip Programı"
        self.dosya = "isfonlar.txt"
        self.Session = sessionmaker(bind=engine)
        self.session = self.Session()
        self.menu_secimi = 0
        self.kullanici = "ogün"

    def menu(self):
        print("1) Portföyümü Yönet")
        print("2) Kar-Zarar Takibi")
        try:
            print("9) Fiyat Güncellemesi: " + colorama.Fore.RED + "(Son güncelleme: %s) " % datetime.fromtimestamp(
                os.path.getmtime(self.dosya)).strftime("%d-%m-%Y %H:%M:%S") + colorama.Fore.RESET)
        except:
            print(colorama.Fore.RED + "9) ÖNCE FİYAT GÜNCELLEMESİ ALIN." + colorama.Fore.RESET)

        print("0) Çıkış")


    def pmenu(self):
        print("1) Portföy Listem")
        print("2) Fon Ekle")
        print("3) Fon Çıkar")
        print("0) Geri")
        self.menu_secimi = 1


    def operator(self, giris):
        if giris == "1":
            return self.pmenu()
        elif giris == "2":
            return self.karzarar()
        elif giris == "9":
            return self.guncelleme()
        elif giris == "11":
            return self.tum()
        elif giris == "12":
            return self.fonsecimi()
        elif giris == "13":
            return self.sil()
        elif giris == "10":
            return self.menu()
        else:
            print("Giriş hatalı")

    def tum(self):
        print("\nAll Tasks:")
        rows = self.session.query(Table).order_by(Table.tarih).all()
        if len(rows) != 0:
            for i in range(len(rows)):
                print(f'{i + 1}. {rows[i].fonadi}. {rows[i].tarih.day} {rows[i].tarih.strftime("%b")}')
            print()
        else:
            return print("Nothing to do!\n"), self.pmenu()

    def fonsecimi(self):
        sor = input("Fon adı veya kodunu giriniz (SERBEST FON veya AAK şeklinde).\nListe için boş bırakın. Geriye dönmek için 0 giriniz: ")
        con = sqlite3.connect("fonlar.db")
        cursor = con.execute("select * from tefas")
        # pd.options.display.max_columns = None
        pd.options.display.max_rows = None
        df = (pd.DataFrame(cursor, columns=["FON ADI", "FON KODU"]))
        df.index = np.arange(1, len(df) + 1)

        if sor is None:
            print(df)
        elif sor == "0":
            return self.pmenu()
        elif len(sor) > 3:
            sor = turkish_upper(sor)
            sonuc = df[df["FON ADI"].str.contains(sor)]
            if sonuc.empty:
                print(colorama.Fore.RED +"Fon bulunamadı"+ colorama.Fore.RESET)
                return self.fonsecimi()
            else:
                print(sonuc)
        else:
            sor = sor.upper()
            sonuc = df[df["FON KODU"].str.contains(sor)]
            if sonuc.empty:
                print(colorama.Fore.RED +"Girdiğiniz kod ile fon bulunamadı"+ colorama.Fore.RESET)
                return self.fonsecimi()
            else:
                print(sonuc)
        #count_row = df.shape[0]


    def fonekle(self, fon, fiyat, tarih):
        year, month, day = map(int, tarih.split('-'))  # Converting to database time format
        date = datetime(year, month, day)
        fon = Table(hesap=self.kullanici, fonkodu=fon, fiyat=fiyat, tarih=date)
        self.session.add(fon)
        self.session.commit()
        print("The task has been added!\n")

    def sil(self):
        print("\nChoose the number of the task you want to delete:")
        rows = self.session.query(Table).order_by(Table.tarih).all()
        if len(rows) != 0:
            for i in range(len(rows)):
                print(f'{i + 1}. {rows[i].task}. {rows[i].tarih.day} {rows[i].tarih.strftime("%b")}')
            self.silelim(int(input()))
        else:
            print("Nothing to delete!\n")
            return

    def silelim(self, index):
        rows = self.session.query(Table).order_by(Table.tarih).all()
        self.session.query(Table).filter(Table.fon == f"{rows[index - 1]}").delete()
        self.session.commit()
        print("The task has been deleted!\n")


    def karzarar(self):
        aranan = "İŞ PORTFÖY ÜÇÜNCÜ SERBEST (DÖVİZ) FON"
        kodu = aranan.replace(" ", "")
        with open(self.dosya, "r", encoding="ISO-8859-9", ) as f:
            content = f.read()
            c = content.index(kodu)
            #  fonadi = content[c:c + int(len(kodu))]
            degeri = float(content[c + int(len(kodu)) + 15:c + int(len(kodu)) + 25])
            f.close()
        print(aranan)
        print(degeri)
        return self.menu()

    def guncelleme(self):
        url = "https://www.isportfoy.com.tr/tr/yatirim-fonlari"
        r = requests.get(url)
        print(r.status_code)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html5lib')
            fonlar = soup.findAll('table')[0].findAll("tr")[3:]
            with open(self.dosya, "w", encoding="ISO-8859-9") as f:
                # line = int(0)
                for fon in fonlar:
                    fon = str(fon.text)
                    f.writelines(fon.replace(" ", ""))
                # line += 1
            f.close()
        else:
            print("Fon fiyatlarının güncellemek için {} sitesine ulaşılamıyor".format(url))

    def baslat(self):
        # print("baslat")
        self.menu()
        while True:
            giris = str(input().lower())
            if giris != "0" and self.menu_secimi == 0:
                self.operator(giris)
            elif giris != "0" and self.menu_secimi == 1:
                self.operator(str("1" + giris))
            elif giris == "0" and self.menu_secimi == 1:
                self.menu_secimi = 0
                self.menu()
            elif giris == "0" and self.menu_secimi == 0:
                print("Çıkış")
                break



isportfoy().baslat()
