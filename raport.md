# Raport Laborator 6 - Forensics și Steganografie

## Lucrarea A: Decoderul Universal
- **Mesaj codificat (`probe/mesaj.txt`)**: Structurat în 3 straturi de codare (`base64` -> `base64` -> `hex`). Text clar: `FLAG{straturi_de_encoding}`.
- **Fișier XOR (`probe/xor.bin`)**: Criptat cu cheia pe 1 octet `128` (`0x80`). Text clar: `Un singur octet tine tot secretul... gaseste-l! FLAG{xor_un_octet}`.

## Lucrarea B: Forensics pe fișiere și Steganografie
- **Tipul real al fișierelor**:
  - `foto.jpg`: `jpeg`
  - `ascuns.png`: `png`
- **Metadate EXIF & GPS (`foto.jpg`)**:
  - Model telefon: `iPhone 13`
  - Coordonate GPS: Latitudine 47.016667 N, Longitudine 28.8575 E (Chișinău)
- **File Carving (`ascuns.png`)**:
  - Arhiva ZIP lipită a fost găsită la offset-ul `781` și extrasă în `probe/gasit.zip`.
  - Fișierul `secret.txt` din interior conține: `FLAG{ascuns_prin_carving}`.
- **Steganografie LSB**:
  - Mesajul ascuns în imaginea `stego.png` și extras cu succes este: `FLAG{ascuns_in_pixeli}`.
