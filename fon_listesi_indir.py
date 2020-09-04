
"""

İPTAL

import requests
import urllib
from urllib.request import urlretrieve


def Indir():
    url = "https://www.takasbank.com.tr/plugins/ExcelExportTefasFundsTradingInvestmentPlatform?language=tr"
    r = requests.get(url, allow_redirects=True)
    if r.headers["Content-Type"] == "application/octet-stream":
        with open("fonlar.xlsx", "wb") as f:
            f.close()
        print("Fon excel dosyası oluşturuldu")

    urllib.request.urlretrieve(url, "fonlar.xlsx")

import pandas as pd
import requests
from bs4 import BeautifulSoup


def Liste():
    url = f"https://www.tefas.gov.tr/FonAnaliz.aspx"
    r = requests.get(url)
    if r.status_code == 200:
        soup = BeautifulSoup(r.content, "html.parser")
        fonkodu = (soup.find("div", id="MainContent_PanelFundList")).find_next("ul").find_all("a", FonKod="")
        fon = (soup.find("div", id="MainContent_PanelFundList")).find_next("ul").text.splitlines()
        str_list = filter(None, fon)
        str_list = filter(bool, str_list)
        str_list = filter(len, str_list)
        str_list = filter(lambda item: item, str_list)
        str_list = list(filter(None, str_list))
        kodlar = []
        for a in fonkodu:
            kodlar.append(a['href'][-3:])
        liste = list(zip(str_list, kodlar))

        pd.DataFrame(liste).to_excel('fonlar.xlsx', header=["fonadi", "fonkodu"], index=False)
        print("Fon listesi dosyası başarıyla oluşturuldu.")
    else:
        print("tefas.gov.tr sitesine bağlanılamıyor. Lütfen daha sonra tekrar deneyin.")
"""
