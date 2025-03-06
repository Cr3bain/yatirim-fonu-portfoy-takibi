import pandas as pd
import requests
from bs4 import BeautifulSoup


def Liste():
    fonlar = []
    url = "https://www.tefas.gov.tr/FonAnaliz.aspx"
    r = requests.get(url)
    if r.status_code == 200:
        soup = BeautifulSoup(r.content, "html.parser")
        content = soup.find("div", id="MainContent_PanelFundList").find_next("ul")
        for a in content.find_all("a"):
            fon_adi = a.text.strip()
            fon_kodu = a['href'][-3:]
            if "EMEKLİLİK" in fon_adi:
                fonlar.append([fon_adi, "EMK", fon_kodu])
            else:
                fonlar.append([fon_adi, "YAT", fon_kodu])
        pd.DataFrame(fonlar).to_excel('fonlar.xlsx', header=["fonadi", "poz", "fonkodu"], index=False)
        print("Fon listesi başarıyla oluşturuldu.")
    else:
        print("Güncelleme için siteye erişilemiyor.")
