# -*- coding: utf-8 -*-
import re, zipfile
from PIL import Image
from PIL.ExifTags import TAGS

# B1. Tip real dupa primii octeti
def tip_real(cale):
    cap = open(cale, "rb").read(8)
    for sig, tip in [(b"%PDF", "pdf"), (b"\x89PNG", "png"), (b"\xff\xd8", "jpeg"), (b"PK\x03\x04", "zip/docx")]:
        if cap.startswith(sig): return tip
    return cap.hex()

# B2. Strings: secventele citibile
def cauta_strings(cale):
    return [m.decode("latin1") for m in re.findall(rb"[ -~]{4,}", open(cale, "rb").read())]

# B3. Metadate EXIF & GPS
def extrage_exif_gps(cale):
    exif_raw = Image.open(cale)._getexif() or {}
    exif = {TAGS.get(k, k): v for k, v in exif_raw.items()}
    gps_info = exif_raw.get(34853, {})
    coord = {}
    if gps_info.get(2) and gps_info.get(4):
        lat, lon = gps_info[2], gps_info[4]
        lat_d = lat[0] + lat[1]/60 + lat[2]/3600
        lon_d = lon[0] + lon[1]/60 + lon[2]/3600
        if gps_info.get(1) == 'S': lat_d = -lat_d
        if gps_info.get(3) == 'W': lon_d = -lon_d
        coord = {"latitudine": lat_d, "longitudine": lon_d}
    return exif, coord

# B4. File Carving (ZIP)
def extrage_zip(cale_in, cale_out_zip):
    date = open(cale_in, "rb").read()
    i = date.find(b"PK\x03\x04")
    if i != -1:
        open(cale_out_zip, "wb").write(date[i:])
        zipfile.ZipFile(cale_out_zip).extractall("probe/")
    return i

# B5. Ascunde mesaj LSB
def ascunde_lsb(cale_foto, mesaj, cale_out):
    img = Image.open(cale_foto).convert("RGB")
    px = list(img.getdata())
    biti = "".join(f"{x:08b}" for x in (mesaj + b"\x00"))
    px_nou = []
    bit_idx = 0
    for r, g, b in px:
        canal = [r, g, b]
        for c in range(3):
            if bit_idx < len(biti):
                canal[c] = (canal[c] & ~1) | int(biti[bit_idx])
                bit_idx += 1
        px_nou.append(tuple(canal))
    img_nou = Image.new("RGB", img.size)
    img_nou.putdata(px_nou)
    img_nou.save(cale_out)

# B6. Dezvaluie mesaj LSB
def dezvaluie_lsb(cale_stego):
    px = list(Image.open(cale_stego).convert("RGB").getdata())
    biti = [str(canal & 1) for p in px for canal in p]
    octeti = []
    for i in range(0, len(biti) - 7, 8):
        val = int("".join(biti[i:i+8]), 2)
        if val == 0: break
        octeti.append(val)
    return bytes(octeti).decode("utf-8", errors="ignore")

if __name__ == "__main__":
    print("=== B1. Tip real ===")
    print("foto.jpg:", tip_real("probe/foto.jpg"))
    print("ascuns.png:", tip_real("probe/ascuns.png"))
    print("\n=== B2. Strings ===")
    print("Primele secvente:", cauta_strings("probe/ascuns.png")[:5])
    print("\n=== B3. EXIF & GPS ===")
    exif, gps = extrage_exif_gps("probe/foto.jpg")
    print("Model:", exif.get("Model"))
    print("GPS:", gps)
    print("\n=== B4. File Carving ===")
    offset = extrage_zip("probe/ascuns.png", "probe/gasit.zip")
    print(f"ZIP gasit la offset {offset}")
    print("Continut ZIP:", open("probe/secret.txt").read().strip())
    print("\n=== B5 & B6. Steganografie LSB ===")
    ascunde_lsb("probe/foto.jpg", b"FLAG{ascuns_in_pixeli}", "stego.png")
    print("Mesaj dezvaluit:", dezvaluie_lsb("stego.png"))
