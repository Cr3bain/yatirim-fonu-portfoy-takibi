# -*- coding:utf-8 -*-

import requests
from bs4 import BeautifulSoup
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
print("  Tefaş Portföy Takibi v.1 (Ş.O.G)  ".center(50, "*"), "\n")


class Portfoy:
    def __init__(self):
        self.aciklama = "Tefaş Portföy Takip Programı"
        self.dosya = "fonlar.db"
        self.Session = sessionmaker(bind=engine)
        self.session = self.Session()
        self.kullanici = "user"
        self.poz = "YAT"  # YAT veya EMK

    def menu(self):
        print("1) Portföy Listem")
        print("2) Kar-Zarar Takibi")
        print("3) Fon Ekle")
        print("4) Fon Çıkar")
        print("5) Fon Bilgilerini Güncelle")
        try:
            print("9) Fon kodu güncellemesi (Son güncelleme: %s) " % datetime.fromtimestamp(
                os.path.getmtime(self.dosya)).strftime("%d-%m-%Y"))
        except FileNotFoundError:
            print("9) FON LİSTESİ DOSYASI YOK. ÖNCE TEFAŞ FON KODU GÜNCELLEMESİ ALIN.")
        print("B) Bilgi")
        print("0) Çıkış")

    def operator(self, giris):
        if giris == "1":
            return self.tum()
        elif giris == "2":
            return self.kar_zarar()
        elif giris == "3":
            return self.fon_secimi()
        elif giris == "4":
            return self.sil()
        elif giris == "5":
            return self.fon_guncelle()
        elif giris == "9":
            return self.guncelleme()
        elif giris == "B" or "b":
            return self.bilgi()
        else:
            print("Giriş hatalı")

    def bilgi(self):
        print("Program tefas.gov.tr adresi üzerinden çalışmaktadır ve fon bilgi ve fiyatlarını sadece bu sitede alır.\n"
              "Kullanımı: 9 ile güncel fon listesi tefaş üzerinden çekilir ve işlem yapabileceğiniz fonlar \n"
              "bilgisayarınıza indirilir. Sonraki adımda; tefaş fon kodu kullanarak veya fon adı  ile \n"
              "aratarak fonu portföyünüze ekleyebilirsiniz. Eklediğiniz fonları güncelleyebilir ve silebilirsiniz. \n"
              "web: https://github.com/Cr3bain   eposta: ogun.gundogdu@gmail.com\n")
        return self.menu()

    def fon_secimi(self):
        sor = input(
            "Tefaş fon kodunu giriniz. (AAK şeklinde)\n Fon kodu listesi için fon adı bilgisi girin "
            "veya tüm liste için boş bırakın. Geriye dönmek için 0 giriniz:")
        con = sqlite3.connect("fonlar.db")
        cursor = con.execute(f"select fonadi, fonkodu from tefas WHERE poz='{self.poz}'")
        pd.options.display.max_rows = None
        pd.options.display.width = 0
        df = (pd.DataFrame(cursor, columns=["FON ADI", "FON KODU"]))
        df.index = np.arange(1, len(df) + 1)
        sor = turkish_upper(sor)

        if sor == "":
            print(df, "\n")
            return self.fon_secimi()
        elif sor == "0":
            return self.menu()
        elif not df[df["FON KODU"].str.contains(sor)].empty:
            sonuc = df[df["FON KODU"].str.contains(sor)]
            print(sonuc)
            fonkodu = (sonuc.iloc[0, 1])
            print("TEFAŞ'dan fonun bilgileri alınıyor...")
            print(self.tefas_bilgi(fonkodu, "tablo"), "\n")
            ekle = input("Fon portföyünüze eklensin mi ? E/H ").upper()
            if "E" == ekle:
                return self.fon_ekle(fonkodu, self.tefas_bilgi(fonkodu, "fiyat"))
            else:
                return self.fon_secimi()
        elif not df[df["FON ADI"].str.contains(sor)].empty:
            print(df[df["FON ADI"].str.contains(sor)])
            print("Fon kodunu giriniz. AAK şeklinde.")
            return self.fon_secimi()
        else:
            print("Girdiğiniz kod ile fon bulunamadı")
            return self.fon_secimi()

    def tefas_bilgi(self, fonkodu, istek):
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

    def fon_ekle(self, fonkodu, fiyat):
        date = datetime.today()
        adet = int(input("Portföyünüze kaç adet eklensin? "))
        fon = Table(kullanici=self.kullanici, fonkodu=fonkodu, fiyat=fiyat, tarih=date, adet=adet)
        self.session.add(fon)
        self.session.commit()

        print(f"Portföyünüze {fonkodu} kodlu fon, {fiyat} TL fiyatıyla, {adet} adet, "
              f"{date.strftime('%d-%m-%Y')} tarihli olarak eklenmiştir.\n")
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
                    f'Alış fiyatı: {rows[i].fiyat}. '
                    f'Adet: {rows[i].adet}. '
                    f'Alış Tarihi: {rows[i].tarih.strftime("%d-%m-%Y")}\n')

            return self.menu()
        else:
            return print("Portföyünüzde fon bulunmamaktadır!\n"), self.menu()

    def sil(self):
        rows = self.session.query(Table).order_by(Table.id).all()
        if len(rows) != 0:
            print("Silmek için bir sıra numarası seçin.")
            for i in range(len(rows)):
                print(
                    f'{i + 1}. Fon: {rows[i].fonkodu} Alış fiyatı: {rows[i].fiyat}. '
                    f'Adet: {rows[i].adet}. Alış Tarihi: {rows[i].tarih.strftime("%d-%m-%Y")}')
            self.silelim(int(input("Sıra numarası girin. İptal için 0 yazın: ")))
        else:
            print("Portföyünüzde fon bulunmamaktadır!\n")
            return self.menu()

    def silelim(self, index):
        if index == 0:
            return self.menu()
        else:
            rows = self.session.query(Table).order_by(Table.id).all()
            self.session.query(Table).filter(Table.id == f"{rows[index - 1].id}").delete()
            self.session.commit()
            print("Fon girişi silindi!\n")
            return self.menu()

    def kar_zarar(self):
        con = sqlite3.connect("fonlar.db")
        rows = self.session.query(Table).order_by(Table.id).all()
        kolonlar = ["Kodu", "Fon Adı", "Alış (TL)", "Tefaş (TL)", "Adet", "Değeri (TL)", "Getiri (TL)", "Getiri (%)"]
        if len(rows) != 0:
            print("Tefaş.gov.tr'den fon bilgilerini alıyor. Lütfen bekleyin...")
            satirlar = []
            for i in range(len(rows)):
                sql = con.execute("select fonadi from tefas where fonkodu like ?", ('%' + str(rows[i].fonkodu) + '%',))
                fonadi = str([item for t in sql.fetchall() for item in t][0])[:20]
                tefasfiyat = float(self.tefas_bilgi(fonkodu=rows[i].fonkodu, istek='fiyat'))
                veriler = [rows[i].fonkodu, fonadi, rows[i].fiyat, tefasfiyat, rows[i].adet,
                        (tefasfiyat * rows[i].adet).__round__(2),
                        ((tefasfiyat - rows[i].fiyat) * rows[i].adet).__round__(2),
                        str(((tefasfiyat - rows[i].fiyat) / rows[i].fiyat * 100).__round__(2))]
                satirlar.append(veriler)
            fontablosu = pd.DataFrame(satirlar, columns=kolonlar)
            fontablosu.index = np.arange(1, len(fontablosu) + 1)
            pd.options.display.max_rows = None
            pd.options.display.width = 0
            print(fontablosu, "\n")
            kazanc = fontablosu['Getiri (TL)'].sum()
            toplam = (fontablosu['Tefaş (TL)'] * fontablosu['Adet']).sum()
            print("Portföyünüzün toplam değeri", float(toplam.__round__(2)), "TL, toplamı getirisi",
                float(kazanc).__round__(2), "TL'dir\n")
            return self.menu()
        else:
            return print("Portföyünüz boş. Önce fon eklemelisiniz.\n"), self.menu()

    def fon_guncelle(self):
        print("\nFon Güncelleme:")
        rows = self.session.query(Table).order_by(Table.id).all()
        if len(rows) != 0:
            for i in range(len(rows)):
                print(
                    f'{i + 1}. Fon kodu: {rows[i].fonkodu}. Alış fiyatı: {rows[i].fiyat}. '
                    f'Adet: {rows[i].adet}. Alış Tarihi: {rows[i].tarih.strftime("%d-%m-%Y")}')
            print()
            self.guncelleyelim(int(input("Sıra numarası girin. İptal için 0 girin : ")))
        else:
            return print("Portföyünüz boş. Önce fon ekleyin.\n"), self.menu()

    def guncelleyelim(self, index):
        if index != 0:
            # try ve expect leri tek tek ata
            index -= 1
            rows = self.session.query(Table).order_by(Table.id).all()
            f = self.session.query(Table).filter(Table.id == rows[index].id).one()
            try:
                print("Boş bırakıldığında değer değişmeyecektir...")
                f.fiyat = input(f"Adet fiyatı {rows[index].fiyat} TL. Yeni değer: ").replace(",", ".") or rows[
                    index].fiyat
                self.session.commit()
                f.adet = input(f"Adet {rows[index].adet}. Yeni değer: ").replace(".", "") or rows[index].adet
                self.session.commit()
                tarih = input(f"Tarih {rows[index].tarih}. Yeni değeri YYYY-AA-GG olarak girin: ") or rows[index].tarih
                year, month, day = map(int, tarih.split('-'))
                f.tarih = datetime(year, month, day)
                self.session.commit()
            except Exception as hata:
                print("Güncelleme esnasında hata oluştur...", hata)
            print("\n")
            print(f'{index + 1}. Fon kodu: {rows[index].fonkodu}. Alış fiyatı: {rows[index].fiyat} '
                  f'Adet: {rows[index].adet}. Alış Tarihi: {rows[index].tarih.strftime("%d-%m-%Y")}')
            print("\n")
            return self.menu()
        else:
            return self.menu()

    def guncelleme(self):
        import list_to_excel
        import excel_to_sql
        list_to_excel.Liste()
        excel_to_sql.Excel()
        return self.menu()

    def hata(self, mesaj):
        print(mesaj)
        return self.menu()

    def baslat(self):
        self.menu()
        while True:
            giris = str(input().lower())
            if giris != "0":
                self.operator(giris)

            elif giris == "0":
                print("Bol kazançlar")
                break


if __name__ == "__main__":
    Portfoy().baslat()
