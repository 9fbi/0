import requests
import random

def get_live_threats():
    attacks = ["DDoS", "Phishing", "Ransomware", "Botnet", "XSS"]
    countries = ["US", "CN", "RU", "IN", "DE"]

    data = []
    for _ in range(20):
        data.append({
            "ip": f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}",
            "attack": random.choice(attacks),
            "country": random.choice(countries),
            "severity": random.choice(["Low", "Medium", "High"])
        })
    return data


# 🔗 Example: AlienVault OTX (requires API key)
def get_otx_data(api_key):
    url = "https://otx.alienvault.com/api/v1/pulses/subscribed"
    headers = {"X-OTX-API-KEY": "78c774571775150052ac797d51c8e9c786cd33f3a081b66c08187dc76b3a7104"}
    response = requests.get(url, headers=headers)
    return response.json()