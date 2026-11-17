# -*- coding: utf-8 -*-
import argparse
import base64
import hashlib
import json
import re
from urllib.parse import unquote

# A2: Ghicește stratul de codare[cite: 1]
def ghici_strat(s):
    if "%" in s:
        return "url"
    if re.fullmatch(r"[0-9a-fA-F]+", s) and len(s) % 2 == 0:
        return "hex"
    if re.fullmatch(r"[A-Za-z0-9+/=]+", s):
        return "base64"
    return "necunoscut"

# A3: Desface un singur strat[cite: 1]
def desfa(s):
    strat = ghici_strat(s)
    try:
        if strat == "base64":
            return strat, base64.b64decode(s)
        elif strat == "hex":
            return strat, bytes.fromhex(s)
        elif strat == "url":
            return strat, unquote(s).encode("utf-8")
    except Exception:
        pass
    return "necunoscut", s.encode("utf-8")

# A4: Verifică dacă toți octeții sunt caractere ASCII imprimabile (32..126)[cite: 1]
def citibil(b):
    return len(b) > 0 and all(32 <= c < 127 for c in b)

# A4: Decodificare în buclă până la text clar[cite: 1]
def decodifica_straturi(val_initiala):
    val = val_initiala
    straturi_aplicate = []
    for _ in range(8):
        strat, b = desfa(val)
        if strat == "necunoscut":
            break
        straturi_aplicate.append(strat)
        try:
            val_text = b.decode("utf-8")
        except UnicodeDecodeError:
            return straturi_aplicate, b.hex()
        # Când următorul pas nu mai este o codare cunoscută, am ajuns la textul clar
        if ghici_strat(val_text) == "necunoscut":
            return straturi_aplicate, val_text
        val = val_text
    return straturi_aplicate, val

# A5: Sparge XOR cu cheie de 1 octet (ignore cheia 0 dacă nu e cazul)[cite: 1]
def sparge_xor(date_binare):
    for k in range(1, 256):  # Incepem de la 1, deoarece 0 nu schimba datele
        clar = bytes(b ^ k for b in date_binare)
        if citibil(clar):
            return k, clar.decode("utf-8")
    return None, None

# A6: Sparge hash prin dicționar (MD5/SHA1/SHA256)[cite: 1]
def sparge_hash(hash_tinta, cale_wordlist):
    lungime = len(hash_tinta)
    try:
        with open(cale_wordlist, "r", encoding="latin1") as f:
            for linie in f:
                cuv = linie.strip()
                cuv_bytes = cuv.encode("utf-8")
                if lungime == 32:
                    h = hashlib.md5(cuv_bytes).hexdigest()
                elif lungime == 40:
                    h = hashlib.sha1(cuv_bytes).hexdigest()
                elif lungime == 64:
                    h = hashlib.sha256(cuv_bytes).hexdigest()
                else:
                    continue
                if h == hash_tinta:
                    return cuv
    except FileNotFoundError:
        pass
    return None

# A7: Interfață din linia de comandă și salvare JSON[cite: 1]
def main():
    p = argparse.ArgumentParser(description="Decoder universal forensics")
    p.add_argument("intrare", help="Sirul de caractere sau calea catre fisier")
    p.add_argument("--fisier", action="store_true", help="Trateaza intrarea ca fisier")
    args = p.parse_args()
    rezultat_fisa = {}
    if args.fisier:
        with open(args.intrare, "rb") as f:
            continut = f.read()
        text_str = continut.decode("utf-8", errors="ignore").strip()
        # 1. Incearca mai intai decodificarea pe straturi
        straturi, text_clar = decodifica_straturi(text_str)
        if straturi:
            rezultat_fisa = {
                "tip": "straturi",
                "straturi": straturi,
                "rezultat": text_clar
            }
        # 2. Daca nu s-au gasit straturi, incearca spargerea hash-ului
        if not rezultat_fisa and len(text_str) in (32, 40, 64) and re.fullmatch(r"[0-9a-fA-F]+", text_str):
            parola = sparge_hash(text_str, "probe/wordlist.txt")
            if parola:
                rezultat_fisa = {
                    "tip": "hash",
                    "hash": text_str,
                    "rezultat": parola
                }
        # 3. Daca nu este nici strat, nici hash, incearca XOR cu cheie (1..255)
        if not rezultat_fisa:
            cheie, text_xor = sparge_xor(continut)
            if cheie is not None:
                rezultat_fisa = {
                    "tip": "xor",
                    "cheie": cheie,
                    "rezultat": text_xor
                }
    else:
        straturi, text_clar = decodifica_straturi(args.intrare)
        rezultat_fisa = {
            "tip": "straturi",
            "straturi": straturi,
            "rezultat": text_clar
        }
    # Salveaza fisa.json[cite: 1]
    with open("arsenal/forensics/fisa.json", "w", encoding="utf-8") as f:
        json.dump(rezultat_fisa, f, indent=4)
    print("Rezultat procesare:")
    print(json.dumps(rezultat_fisa, indent=4))

if __name__ == "__main__":
    main()
