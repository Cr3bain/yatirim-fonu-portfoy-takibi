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
    fonkodu = Column(String(length=255), default='default_value')
    fiyat = Column(FLOAT, nullable=True)
    adet = Column(Integer(), default=1)
    tarih = Column(Date, default=datetime.today().strftime('%d-%m-%Y'))
    kullanici = Column(String(length=255), default='default_value')

    def __repr__(self):
        return self.kullanici


Base.metadata.create_all(engine)


class isportfoy:
    def __init__(self):
        self.aciklama = "Tefaş Portföy Takip Programı"
        self.dosya = "fonlar.db"
        self.Session = sessionmaker(bind=engine)
        self.session = self.Session()
        self.kullanici = "ogün"

    def menu(self):
        print("1) Portföy Listem")
        print("2) Kar-Zarar Takibi")
        print("3) Fon Ekle")
        print("4) Fon Çıkar")
        print("5) Fon Bilgilerini Güncelle")
        try:
            print("9) Fon kodu güncellemesi " + colorama.Fore.RED + "(Son güncelleme: %s) " % datetime.fromtimestamp(
                os.path.getmtime(self.dosya)).strftime("%d-%m-%Y %H:%M:%S") + colorama.Fore.RESET)
        except:
            print(colorama.Fore.RED + "9) ÖNCE FON KODU GÜNCELLEMESİ ALIN." + colorama.Fore.RESET)
        print("0) Çıkış")

    def operator(self, giris):
        if giris == "1":
            return self.tum()
        elif giris == "2":
            return self.karzarar()
        elif giris == "3":
            return self.fonsecimi
        elif giris == "4":
            return self.sil()
        elif giris == "5":
            return self.fongucelle()
        elif giris == "9":
            return self.guncelleme()
        else:
            print("Giriş hatalı")

    @property
    def fonsecimi(self):
        sor = input(
            "Tefaş fon kodunu giriniz. (AAK şeklinde) \nListe için fon bilgisi girin veya tüm liste için boş bırakın. "
            "Geriye dönmek için 0 giriniz: ")
        con = sqlite3.connect("fonlar.db")
        cursor = con.execute("select * from tefas")
        # pd.options.display.max_columns = None
        pd.options.display.max_rows = None
        df = (pd.DataFrame(cursor, columns=["FON ADI", "FON KODU"]))
        df.index = np.arange(1, len(df) + 1)

        if sor == "":
            print(df, "\n")
            return self.fonsecimi
        elif sor == "0":
            return self.menu()
        elif len(sor) > 3:
            sor = turkish_upper(sor)
            sonuc = df[df["FON ADI"].str.contains(sor)]
            if sonuc.empty:
                print(colorama.Fore.RED + "Fon bulunamadı" + colorama.Fore.RESET)
                return self.fonsecimi
            else:
                print(sonuc)
                # print(sonuc.index)
                return self.fonsecimi

        else:
            sor = sor.upper()
            sonuc = df[df["FON KODU"].str.contains(sor)]
            if sonuc.empty:
                print(colorama.Fore.RED + "Girdiğiniz kod ile fon bulunamadı" + colorama.Fore.RESET)
                return self.fonsecimi
            else:
                print(sonuc)
                fonkodu = (sonuc.iloc[0, 1])
                print("TEFAŞ'dan fonun bilgileri alınıyor...")

                print(self.tefasbilgi(fonkodu, "tablo"), "\n")
                ekle = input("Fon portföyünüze eklensin mi ? E/H ").upper()
                if "E" == ekle:
                    return self.fonekle(fonkodu, self.tefasbilgi(fonkodu, "fiyat"))
                else:
                    return self.menu()

        # count_row = df.shape[0]

    def tefasbilgi(self, fonkodu, istek):
        url = f"https://www.tefas.gov.tr/FonAnaliz.aspx?FonKod={fonkodu}"
        r = requests.get(url)
        if r.status_code == 200:
            soup = BeautifulSoup(r.content, "lxml")
            fon = (
                soup.find("span", id="MainContent_FormViewMainIndicators_LabelFund").find_next("ul")).text.splitlines()

            str_list = filter(None, fon)
            str_list = filter(bool, str_list)
            str_list = filter(len, str_list)
            str_list = filter(lambda item: item, str_list)
            str_list = list(filter(None, str_list))
            # print(str_list)

            if istek == "tablo":
                lst = [str_list[1], str_list[3], str_list[5], str_list[7], str_list[9]]
                df = pd.DataFrame(lst, index=[str_list[0], str_list[2], str_list[4], str_list[6], str_list[8]],
                                  columns=['TEFAŞ Fon Bilgisi'])
                return df
            elif istek == "fiyat":
                return float(str_list[1].replace(",", "."))
            elif istek == "kategori":
                return str_list[8]
            else:
                print("istek hatası")
        else:
            return self.hata("TEFAŞ sitesine bağlanılamadı...")

    def fonekle(self, fonkodu, fiyat):
        # year, month, day = map(int, tarih.split('-'))  # Converting to database time format
        # date = datetime(year, month, day)
        date = datetime.today()
        adet = int(input("Portföyünüze kaç adet eklensin? "))
        fon = Table(kullanici=self.kullanici, fonkodu=fonkodu, fiyat=fiyat, tarih=date, adet=adet)
        self.session.add(fon)
        self.session.commit()

        print(f"{colorama.Fore.RED}Portföyünüze {fonkodu} kodlu fon, {fiyat} TL fiyatıyla, {adet} adet, "
              f"{date.strftime('%d-%m-%Y')} tarihli olarak eklenmiştir{colorama.Fore.RESET}\n")
        return self.menu()

    def tum(self):
        print("\nFon Portföyüm:")
        rows = self.session.query(Table).order_by(Table.id).all()
        if len(rows) != 0:
            con = sqlite3.connect("fonlar.db")
            for i in range(len(rows)):
                cursor = con.execute(f"select fonadi from tefas WHERE fonkodu ='{rows[i].fonkodu}'")
                print(
                    f'{i + 1}. Fon kodu: {rows[i].fonkodu} - {cursor.fetchall()[0][0]} \n'
                    f'Alış fiyatı: {colorama.Fore.RED}{rows[i].fiyat}{colorama.Fore.RESET}. '
                    f'Adet: {colorama.Fore.RED}{rows[i].adet}{colorama.Fore.RESET}. '
                    f'Alış Tarihi: {rows[i].tarih.strftime("%d-%m-%Y")}\n')

            return self.menu()
        else:
            return print("Nothing to do!\n"), self.menu()

    def sil(self):
        print("\nSilmek için bir sıra numarası seçin:")
        rows = self.session.query(Table).order_by(Table.id).all()
        if len(rows) != 0:
            for i in range(len(rows)):
                print(
                    f'{i + 1}. Fon kodu: {rows[i].fonkodu}. Alış fiyatı: {rows[i].fiyat}. '
                    f'Adet: {rows[i].adet}. Alış Tarihi: {rows[i].tarih.strftime("%d-%m-%Y")}')
            self.silelim(int(input("Sıra numarası girin: ")))
        else:
            print("Portföyünüzde fon bulunmamaktadır!\n")
            return

    def silelim(self, index):
        # burayı çoklu fonlarda kontrol et
        rows = self.session.query(Table).order_by(Table.id).all()
        self.session.query(Table).filter(Table.id == f"{rows[index - 1].id}").delete()
        self.session.commit()
        print("Fon girişi silindi!\n")
        return self.menu()

    def karzarar(self):
        rows = self.session.query(Table).order_by(Table.id).all()
        kolonlar = ["Fon Kodu", "Alış Fiyatı", "Tefaş Fiyatı", "Adet", "Tarih", "Kar-Zarar"]
        if len(rows) != 0:
            print("Tefaş'tan fon bilgilerini alıyor. Lütfen bekleyin...")
            satirlar = []
            for i in range(len(rows)):
                veriler = [rows[i].fonkodu, rows[i].fiyat, self.tefasbilgi(rows[i].fonkodu, "fiyat"), rows[i].adet,
                           rows[i].tarih.strftime("%d-%m-%Y"),
                           ((self.tefasbilgi(rows[i].fonkodu, "fiyat") - rows[i].fiyat) * rows[i].adet).__round__(2)]
                satirlar = pd.DataFrame([veriler], columns=kolonlar).append(satirlar)

            fontablosu = pd.concat([satirlar], ignore_index=True)
            # print(fontablosu.sum(axis = 0))
            print(fontablosu, "\n")
            kazanc = fontablosu['Kar-Zarar'].sum()
            portfoy_degeri = float(fontablosu['Tefaş Fiyatı'].sum()) * fontablosu['Adet'].sum()
            print("Portföyünüzün toplam değeri: ", float(portfoy_degeri.__round__(2)), " TL'dir. Kar-zarar durumu", float(kazanc).__round__(2), "TL'dir\n")
            return self.menu()
        else:
            return print("Portföyünüz boş. Önce fon ekleyin.\n"), self.menu()

    def fongucelle(self):
        print("\nFon Güncelleme:")
        rows = self.session.query(Table).order_by(Table.id).all()
        if len(rows) != 0:
            for i in range(len(rows)):
                print(
                    f'{i + 1}. Fon kodu: {rows[i].fonkodu}. Alış fiyatı: {rows[i].fiyat}. '
                    f'Adet: {rows[i].adet}. Alış Tarihi: {rows[i].tarih.strftime("%d-%m-%Y")}')
            print()
            self.guncelleyelim(int(input("Sıra numarası girin: ")))
        else:
            return print("Nothing to do!\n"), self.menu()

    def guncelleyelim(self, index):

        # try ve expect leri tek tek ata
        index -= 1
        rows = self.session.query(Table).order_by(Table.id).all()
        # rows = self.session.query(Table).filter(Table.id == index)
        f = self.session.query(Table).filter(Table.id == rows[index].id).one()
        try:
            print("Boş bırakıldığında değer değişmeyecektir...")
            f.fiyat = input(f"Adet fiyatı {rows[index].fiyat} TL. Yeni değer: ").replace(",", ".") or rows[index].fiyat
            self.session.commit()
            f.adet = input(f"Adet {rows[index].adet}. Yeni değer: ").replace(".", "") or rows[index].adet
            self.session.commit()
            tarih = input(f"Tarih {rows[index].tarih}. Yeni değer: YYYY-AA-GG olarak girin: ") or rows[index].tarih
            year, month, day = map(int, tarih.split('-'))
            f.tarih = datetime(year, month, day)
            self.session.commit()
        except:
            print("Güncelleme esnasında hata oluştur...")
        print("\n")
        print(f'{index + 1}. Fon kodu: {rows[index].fonkodu}. Alış fiyatı: {rows[index].fiyat} '
              f'Adet: {rows[index].adet}. Alış Tarihi: {rows[index].tarih.strftime("%d-%m-%Y")}')
        print("\n")
        # if len(rows) != 0:
        #    for i in range(len(rows)):
        #        print(
        #            f'{i + 1}. Fon kodu: {rows[i].fonkodu}. Alış fiyatı: {rows[i].fiyat}. '
        #            f'Adet: {rows[i].adet}. Alış Tarihi: {rows[i].tarih.strftime("%d-%m-%Y")}')
        #    print()
        #    return self.menu()
        # else:
        #    return print("Nothing to do!\n"), self.menu()
        return self.menu()

    def guncelleme(self):
        import fon_listesi_indir
        import excel_to_sql
        fon_listesi_indir.__dir__()
        excel_to_sql.__dir__()
        return self.menu()

    def hata(self, mesaj):
        print(mesaj)
        return self.menu()

    def baslat(self):
        # print("baslat")
        self.menu()
        while True:
            giris = str(input().lower())
            if giris != "0":
                self.operator(giris)

            elif giris == "0":
                print("Çıkış")
                break


isportfoy().baslat()
