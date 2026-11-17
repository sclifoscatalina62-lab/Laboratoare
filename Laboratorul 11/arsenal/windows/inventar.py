
from dataclasses import dataclass, asdict
import json


CAI_SUSPECTE = ("\\Temp\\", "\\Roaming\\")
SUSPECTE_ID = {4625, 1102, 7045}


# A1. Clasa Proces
@dataclass
class Proces:
    pid: int
    nume: str
    user: str
    cale: str

    # A2. Metoda e_uspect
    def e_suspect(self):
        return any(c in self.cale for c in CAI_SUSPECTE)


# A3. Clasa Eveniment
@dataclass
class Eveniment:
    id: int
    nivel: str
    sursa: str
    cont: str
    mesaj: str

    def e_suspect(self):
        return self.id in SUSPECTE_ID or self.nivel == "critical"


# A4. Încărcarea proceselor din JSON
def procese_din_json(cale):
    with open(cale, encoding="utf-8") as f:
        return [Proces(**d) for d in json.load(f)]


def evenimente_din_json(cale):
    with open(cale, encoding="utf-8") as f:
        return [Eveniment(**d) for d in json.load(f)]


# B1. Clasa Inventar
@dataclass
class Inventar:
    procese: list

    @classmethod
    def din_json(cls, cale):
        with open(cale, encoding="utf-8") as f:
            return cls([Proces(**d) for d in json.load(f)])

    def __len__(self):
        return len(self.procese)

    # B2. Metodele de interogare
    def suspecte(self):
        return [p for p in self.procese if p.e_suspect()]

    def pe_user(self):
        rezultat = {}

        for p in self.procese:
            rezultat.setdefault(p.user, []).append(p.nume)

        return rezultat


# B3. Raportul JSON
def main():
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("capturi")
    p.add_argument("--json", action="store_true")
    a = p.parse_args()

    inv = Inventar.din_json(a.capturi + "/procese.json")
    ev = evenimente_din_json(a.capturi + "/evenimente.json")

    suspecte = inv.suspecte()
    alarma = [e for e in ev if e.e_suspect()]

    if a.json:
        raport = {
            "procese_suspecte": [asdict(p) for p in suspecte],
            "evenimente_alarma": [asdict(e) for e in alarma]
        }
        print(json.dumps(raport, indent=2, ensure_ascii=False))
    else:
        print(f"Procese: {len(inv)} | suspecte: {len(suspecte)}")

        for p in suspecte:
            print(f" [{p.pid}] {p.nume} ({p.user}) {p.cale}")

        print(f"Evenimente: {len(ev)} | alarma: {len(alarma)}")

        for e in alarma:
            print(f" {e.id} [{e.nivel}] {e.cont}: {e.mesaj}")


if __name__ == "__main__":
    main()
