#!/usr/bin/env python3
"""
Script indépendant : Alerte POCSAG en cas de dépassement du seuil X-Ray
+ Alerte de fin d'orage avec durée totale.

F4IGV + ChatGPT 😉
"""

import requests
import xml.etree.ElementTree as ET
import json
import os
from datetime import datetime, timezone

# ----------------------------------------
# CONFIGURATION
# ----------------------------------------

HAMQSL_XML_URL = "https://www.hamqsl.com/solarxml.php"

XRAY_THRESHOLD = "M5.0"

STATE_FILE = "xray_alert_state.txt"
START_FILE = "xray_alert_start.txt"

DAPNET_USER = "f4abc"                   #your username here
DAPNET_PASS = "123456"                  #your password here

DAPNET_CALLSIGN = ["f4abc", "f4def"]    # multiple callsigns here
DAPNET_TRANSMITTER_GROUP = "f-53"       # your transmitter group here


# ----------------------------------------
# XRAY UTILS
# ----------------------------------------

def xray_to_value(xray: str) -> float:
    if not xray or len(xray) < 2:
        return 0.0

    scale = xray[0].upper()
    number = float(xray[1:])

    multipliers = {
        "A": 1e-8,
        "B": 1e-7,
        "C": 1e-6,
        "M": 1e-5,
        "X": 1e-4
    }

    return number * multipliers.get(scale, 0)


def is_above_threshold(xray):
    return xray_to_value(xray) >= xray_to_value(XRAY_THRESHOLD)


# ----------------------------------------
# XML + DAPNET
# ----------------------------------------

def fetch_xray_value():
    try:
        r = requests.get(HAMQSL_XML_URL, timeout=10)
        r.raise_for_status()

        root = ET.fromstring(r.text)
        xray = root.findtext(".//xray")

        if xray:
            return xray.strip()

    except Exception as e:
        print(f"[ERREUR] Impossible de récupérer le flux X-Ray : {e}")

    return None


def send_dapnet_message(text, emergency=False):
    payload = {
        "text": text,
        "callSignNames": [DAPNET_CALLSIGN],
        "transmitterGroupNames": [DAPNET_TRANSMITTER_GROUP],
        "emergency": emergency
    }

    try:
        r = requests.post(
            "https://hampager.de/api/calls",
            auth=(DAPNET_USER, DAPNET_PASS),
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload),
            timeout=10
        )
        r.raise_for_status()
        print("[OK] Message envoyé :", text)
        return True

    except Exception as e:
        print(f"[ERREUR] Impossible d'envoyer le message DAPNET : {e}")
        return False


# ----------------------------------------
# GESTION ÉTAT + DURÉE
# ----------------------------------------

def load_state():
    if not os.path.exists(STATE_FILE):
        return "ok"
    return open(STATE_FILE).read().strip()


def save_state(state):
    with open(STATE_FILE, "w") as f:
        f.write(state)


def save_start_time():
    now = datetime.now(timezone.utc).isoformat()
    with open(START_FILE, "w") as f:
        f.write(now)


def load_start_time():
    if not os.path.exists(START_FILE):
        return None
    try:
        return datetime.fromisoformat(open(START_FILE).read().strip())
    except:
        return None


def format_duration(seconds: int) -> str:
    minutes = seconds // 60
    hours = minutes // 60
    days = hours // 24

    if minutes < 60:
        return f"{minutes} min"

    if hours < 24:
        return f"{hours}h {minutes % 60}min"

    return f"{days}j {hours % 24}h"


# ----------------------------------------
# ALERTE XRAY
# ----------------------------------------

def send_alert_start(xray):
    return send_dapnet_message(
        f"ALERTE XRAY : {xray} (seuil {XRAY_THRESHOLD})  DEBUT ORAGE SOLAIRE",
        emergency=True
    )


def send_alert_end(xray, duration):
    return send_dapnet_message(
        f"FIN ORAGE SOLAIRE  XRAY : {xray}  Duree : {duration}",
        emergency=False
    )


# ----------------------------------------
# MAIN
# ----------------------------------------

def main():
    print("Récupération flux X-Ray…")

    xray = fetch_xray_value()
    if not xray:
        print("[ERREUR] Pas de donnée X-Ray — arrêt.")
        return

    print(f"Flux X-Ray détecté : {xray}")

    above = is_above_threshold(xray)
    previous_state = load_state()

    # --- DÉBUT ORAGE ---
    if above and previous_state == "ok":
        print(f"[ALERTE] Orage solaire détecté !")
        save_start_time()
        if send_alert_start(xray):
            save_state("alert")

    # --- FIN ORAGE ---
    elif not above and previous_state == "alert":
        print("[INFO] Fin d'orage solaire détectée.")

        start_time = load_start_time()
        if start_time:
            now = datetime.now(timezone.utc)
            duration_sec = int((now - start_time).total_seconds())
            duration_txt = format_duration(duration_sec)
        else:
            duration_txt = "durée inconnue"

        if send_alert_end(xray, duration_txt):
            save_state("ok")

    else:
        print("[INFO] Aucun changement d’état.")

if __name__ == "__main__":
    main()

