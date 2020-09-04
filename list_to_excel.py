import pandas as pd
import requests
from bs4 import BeautifulSoup


def Liste():
    fonlar = []
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
        for i in str_list:
            if str(i).find("EMEKLİLİK") > 0:
                fonlar.append([i, "EMK"])
            else:
                fonlar.append([i, "YAT"])
        i = 0
        for a in fonkodu:
            fonlar[i].append(a['href'][-3:])
            i += 1

        pd.DataFrame(fonlar).to_excel('fonlar.xlsx', header=["fonadi", "poz", "fonkodu"], index=False)
        print("Fon listesi başarıyla oluşturuldu.")
    else:
        print("Güncelleme için siteye erişilemiyor.")
