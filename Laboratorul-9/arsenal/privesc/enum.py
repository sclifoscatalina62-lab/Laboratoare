import argparse
import json
import os

GTFO = {
    "find", "vim.basic", "vim", "nmap", "cp",
    "bash", "less", "awk", "python3", "perl"
}


def citeste_linii(cale):
    with open(cale, encoding="utf-8") as f:
        return [
            linie.strip()
            for linie in f
            if linie.strip() and not linie.strip().startswith("#")
        ]


def nume(cale):
    return cale.rsplit("/", 1)[-1]


def suid_constatari(cale):
    cai = citeste_linii(cale)
    out = []

    for c in sorted(set(cai)):
        out.append({
            "cale": c,
            "nume": nume(c),
            "risc": "mare" if nume(c) in GTFO else "normal"
        })

    return out


def sudo_constatari(cale):
    out = []

    for ln in citeste_linii(cale):
        user, drept = ln.split(" : ", 1)

        out.append({
            "user": user.strip(),
            "drept": drept.strip(),
            "risc": "mare" if "NOPASSWD" in drept else "normal"
        })

    return out


def cron_constatari(cale):
    out = []

    for ln in citeste_linii(cale):
        campuri = ln.split()
        user = campuri[5]
        comanda = " ".join(campuri[6:])

        out.append({
            "user": user,
            "comanda": comanda
        })

    return out


def enumereaza(d):
    return {
        "suid": suid_constatari(os.path.join(d, "suid.txt")),
        "sudo": sudo_constatari(os.path.join(d, "sudo.txt")),
        "cron": cron_constatari(os.path.join(d, "crontab.txt"))
    }


def main():
    p = argparse.ArgumentParser()

    p.add_argument("capturi")
    p.add_argument("--json", action="store_true")

    a = p.parse_args()
    raport = enumereaza(a.capturi)

    if a.json:
        print(json.dumps(raport, indent=2, ensure_ascii=False))
        return

    for categorie, lista in raport.items():
        mari = [
            c for c in lista
            if c.get("risc") == "mare"
        ]

        print(
            f"{categorie}: {len(lista)} gasite, "
            f"{len(mari)} cu risc mare"
        )

    utilizatori = (
        {c["user"] for c in raport["sudo"]}
        | {c["user"] for c in raport["cron"]}
    )

    print("utilizatori implicati:", ", ".join(sorted(utilizatori)))

    cale_json = os.path.join(os.path.dirname(__file__), "enum.json")

    with open(cale_json, "w", encoding="utf-8") as f:
        json.dump(raport, f, indent=2, ensure_ascii=False)

    print("Raport salvat in enum.json")


if __name__ == "__main__":
    main()
