from datetime import date, timedelta
import pandas as pd
from pytefas import Crawler

FON_KODLARI = [
    "ILH", "YPT", "IOO", "VK6", "TI1", "HLL", "CFO", "YLB",
    "HPV", "HKV", "YVD", "ZP8", "DCB", "GTL", "GJH", "TZL",
    "YP4", "YJY", "BKY",
]

tefas = Crawler()


def araliktaki_veri(baslangic: date, bitis: date) -> pd.DataFrame:
    parcalar = []
    for kind in ["YAT", "EMK", "BYF"]:
        try:
            df = tefas.fetch(
                start=baslangic.isoformat(),
                end=bitis.isoformat(),
                columns="info",
                kind=kind,
            )
            df = df[df["fund_code"].isin(FON_KODLARI)]
            if not df.empty:
                parcalar.append(df)
        except Exception as e:
            print(f"{kind} çekilirken hata: {e}")
    return pd.concat(parcalar, ignore_index=True) if parcalar else pd.DataFrame()


bugun = date.today()
baslangic_1ay = bugun - timedelta(days=35)

veri = araliktaki_veri(baslangic_1ay, bugun)

if veri.empty:
    raise SystemExit("Son 35 gün içinde hiçbir fon için veri bulunamadı.")

veri = veri.sort_values(["fund_code", "date"]).reset_index(drop=True)
veri["gunluk_getiri_%"] = veri.groupby("fund_code")["price"].pct_change() * 100

bulunanlar = set(veri["fund_code"].unique())
bulunamayanlar = set(FON_KODLARI) - bulunanlar
if bulunamayanlar:
    print(f"UYARI: şu kodlar bulunamadı: {sorted(bulunamayanlar)}\n")

veri.to_csv("fonlar_1aylik_gecmis.csv", index=False)
print(f"'fonlar_1aylik_gecmis.csv' kaydedildi ({len(veri)} satır).")

son_veri = veri.sort_values("date").groupby("fund_code").tail(1).sort_values("fund_code")
son_veri.to_csv("fonlar_gunluk_getiri.csv", index=False)
print(f"'fonlar_gunluk_getiri.csv' kaydedildi ({len(son_veri)} satır).")

print()
print(son_veri[["date", "fund_code", "fund_name", "price", "gunluk_getiri_%"]].to_string(index=False))
