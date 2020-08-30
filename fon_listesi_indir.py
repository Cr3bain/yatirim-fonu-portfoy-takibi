import requests
import urllib
from urllib.request import urlretrieve


def __dir__():
    url = "https://www.takasbank.com.tr/plugins/ExcelExportTefasFundsTradingInvestmentPlatform?language=tr"
    r = requests.get(url, allow_redirects=True)
    if r.headers["Content-Type"] == "application/octet-stream":
        with open("fonlar.xlsx", "wb") as f:
            f.close()
        print("Fon excel dosyası oluşturuldu")

    urllib.request.urlretrieve(url, "fonlar.xlsx")
