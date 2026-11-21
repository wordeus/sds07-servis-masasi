"""Metin yardımcıları (katmandan bağımsız, saf fonksiyonlar)."""


def turkish_key(text: str) -> str:
    """Türkçe kurallı karşılaştırma anahtarı: "I"->"ı", "İ"->"i", sonra küçük harf; boşluklar sadeleşir.

    SQLite'ın büyük/küçük harf duyarsız karşılaştırması (`iexact`) yalnız ASCII harflerde
    çalışır; "DONANIM" ile "Donanım" eşleşmez (RSK-21). Python'un `lower()` işlevi de "I"yı
    "i" yapar. Bu yüzden Türkçe büyük harfler önce elle dönüştürülür.
    """
    lowered = text.replace("I", "ı").replace("İ", "i").lower()
    return " ".join(lowered.split())
