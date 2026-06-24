import random

def GeneRateMsdk():
    chrs = "abcdefghijklmnopqrstuvwxyz"
    nms = "1234567890"
    lng = {"US": "en", "GB": "en", "CA": "en", "AU": "en", "SG": "en", "IN": "en", "FR": "fr", "BE": "fr", "CH": "fr","ES": "es", "MX": "es", "CO": "es","DZ": "ar", "SA": "ar", "EG": "ar", "MA": "ar", "IQ": "ar","DE": "de", "AT": "de","BR": "pt", "PT": "pt","RU": "ru", "TR": "tr","ID": "id", "MY": "ms","VN": "vi", "TH": "th","JP": "ja", "KR": "ko","IT": "it", "NL": "nl","PL": "pl", "SE": "sv",}
    country, language = random.choice(list(lng.items()))
    android_vrsn = random.randint(4,16)
    k2 = random.choice(chrs).upper() + ''.join(random.choice(nms) for _ in range(3)) + random.choice(chrs).upper()
    k3 = f"{random.randint(3,5)}.{random.randint(0,9)}.{random.randint(10,99)}{random.choice(chrs).upper()}{random.randint(1,9)}"
    return f"GarenaMSDK/{k3}({k2} ;Android {android_vrsn};{language};{country};)"
