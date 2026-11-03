import os

from arsenal.privesc.enum import nume, GTFO, citeste_linii


def cai(fisier):
    return set(citeste_linii(fisier))


folder = os.path.join(os.path.dirname(__file__), "start")

baza = cai(os.path.join(folder, "baza_suid.txt"))
acum = cai(os.path.join(folder, "suid.txt"))

print("baza:", len(baza), " acum:", len(acum))

noi = acum - baza

print(len(noi), "SUID noi fata de sistemul curat")

for c in sorted(noi):
    print(" ", c)

risc = {
    nume(c): ("mare" if nume(c) in GTFO else "normal")
    for c in noi
}

periculoase = [
    c for c in sorted(noi)
    if nume(c) in GTFO
]

print("periculoase NOI:", periculoase)
