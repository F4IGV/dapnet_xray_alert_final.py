#!/usr/bin/env python3
"""
F4IGV et son amis Chat GPT présentent:
Version XML stable — HamQSL vers DAPNET
Récupère les données solaires depuis le flux XML HamQSL
et les envoie sur DAPNET vers plusieurs callsigns.
"""

import requests
import xml.etree.ElementTree as ET
import json
from dateutil import parser as dateparser

# --------------- CONFIG ----------------
DAPNET_URL = "https://hampager.de/api/calls"
DAPNET_USER = "f4abc"               # ton login hampager
DAPNET_PASS = "123456"           # ton mot de passe hampager
CALLSIGNS = ["f4abc", "f4def"]      # <<< plusieurs callsigns ici
TX_GROUP = "all"                   # groupe DAPNET

# URL XML HamQSL
HAMQSL_XML_URL = "https://www.hamqsl.com/solarxml.php"
# ----------------------------------------------------


def fetch_hamqsl_xml(url=HAMQSL_XML_URL, timeout=10):
    """Télécharge et parse le XML HamQSL."""
    headers = {"User-Agent": "Mozilla/5.0 (compatible; hamqsl-dapnet-bot/1.0)"}
    try:
        r = requests.get(url, headers=headers, timeout=timeout)
        r.raise_for_status()
        return ET.fromstring(r.text)
    except Exception as e:
        print(f"[WARN] Erreur HTTP/XML lors de la récupération HamQSL : {e}")
        return None


def extract_solar_info(xml_root):
    """Extrait les données utiles depuis le XML HamQSL."""
    if xml_root is None:
        return {}

    info = {
        "solar_flux": "",
        "sunspots": "",
        "a_index": "",
        "k_index": "",
        "xray_flux": "",
        "geomagfield": "",
        "signalnoise": "",
        "timestamp": "",
    }

    data = xml_root.find("solardata")
    if data is None:
        print("[WARN] Pas de balise <solardata> dans le XML.")
        return info

    info["solar_flux"] = data.findtext("solarflux", "").strip()
    info["sunspots"] = data.findtext("sunspots", "").strip()
    info["a_index"] = data.findtext("aindex", "").strip()
    info["k_index"] = data.findtext("kindex", "").strip()
    info["xray_flux"] = data.findtext("xray", "").strip()
    info["signalnoise"] = data.findtext("signalnoise", "").strip()
    info["geomagfield"] = data.findtext("geomagfield", "").strip()

    return info


def build_pocsag_message(info, max_len=80):
    """Construit un message POCSAG compact."""
    parts = []
    add = lambda k, v: parts.append(f"{k}:{v}") if v else None

    add("SFI", info.get("solar_flux"))
    add("SN", info.get("sunspots"))
    add("A", info.get("a_index"))
    add("K", info.get("k_index"))
    add("X", info.get("xray_flux"))
    add("Noise", info.get("signalnoise"))
    add("Geomag", info.get("geomagfield"))

    if info.get("timestamp"):
        try:
            dt = dateparser.parse(info["timestamp"])
            parts.append(dt.strftime("%m-%d %H:%M"))
        except Exception:
            parts.append(info["timestamp"])

    msg = " ".join(parts)
    return msg[:max_len].rstrip()


def send_dapnet_call(message):
    """Envoie le message sur DAPNET à plusieurs callsigns."""
    payload = {
        "text": message,
        "callSignNames": CALLSIGNS,             # <<< MULTIPLE CALLSIGNS ICI
        "transmitterGroupNames": [TX_GROUP],
        "emergency": False
    }

    headers = {"Content-Type": "application/json"}

    try:
        r = requests.post(
            DAPNET_URL,
            auth=(DAPNET_USER, DAPNET_PASS),
            headers=headers,
            data=json.dumps(payload),
            timeout=10
        )
        r.raise_for_status()
        print("[OK] Message envoyé à DAPNET :", r.status_code, r.text)
        return True
    except requests.HTTPError as he:
        print(f"[ERROR] HTTP : {he} / {getattr(he.response, 'text', None)}")
    except Exception as e:
        print(f"[ERROR] Exception Python : {e}")
    return False


def main():
    print("Récupération XML HamQSL…")
    xml_root = fetch_hamqsl_xml()
    info = extract_solar_info(xml_root)
    print("Données extraites :", info)

    message = build_pocsag_message(info)
    print("Message POCSAG :", repr(message))

    if not message.strip():
        print("[ERROR] Message vide — arrêt.")
        return

    if send_dapnet_call(message):
        print("[DONE] Envoi effectué.")
    else:
        print("[FAILED] Envoi échoué.")


if __name__ == "__main__":
    main()
