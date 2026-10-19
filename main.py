"""Rule-Based Expert System: validasi & saran perbaikan jadwal kuliah.

Contoh:
    python main.py                                   # pakai hasil search-algorithm
    python main.py --input sample_schedule.json      # jadwal contoh yang sengaja bermasalah
    python main.py --input sample_schedule.json --trace   # tampilkan jejak inferensi
    python main.py --rules                           # tampilkan basis pengetahuan
"""
import argparse
import json
import os

from engine import ForwardChainingEngine
from rules import RULES

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_INPUT = os.path.join(HERE, "..", "search-algorithm", "output", "schedule.json")


def load_facts(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    facts = []
    for r in data["schedule"]:
        facts.append(("class", r["code"], r["lecturer"], r["group"], r["day"], r["hour"],
                      r["room"], r["students"], r["capacity"], r["is_lab"], r["room_is_lab"]))
    return data, facts


def main():
    ap = argparse.ArgumentParser(description="Expert system validasi jadwal kuliah")
    ap.add_argument("--input", default=DEFAULT_INPUT)
    ap.add_argument("--trace", action="store_true", help="tampilkan jejak forward chaining")
    ap.add_argument("--rules", action="store_true", help="tampilkan semua rule lalu keluar")
    args = ap.parse_args()

    if args.rules:
        for r in RULES:
            print(f"{r.rid:<4} {r.description}")
        return

    if not os.path.exists(args.input):
        raise SystemExit(f"File {args.input} tidak ada. Jalankan search-algorithm/main.py dulu "
                         f"atau pakai --input sample_schedule.json")

    data, facts = load_facts(args.input)
    engine = ForwardChainingEngine(RULES)
    for f in facts:
        engine.assert_fact(f)
    engine.run()

    print(f"Jadwal: {args.input} ({len(facts)} kelas, dari {data.get('algorithm', 'manual')})")
    for level in ("ERROR", "WARNING", "SUGGESTION"):
        items = sorted(f[1] for f in engine.facts if f[0] == level)
        if items:
            print(f"\n[{level}]")
            for m in items:
                print(f"  - {m}")
    verdict = [f[1] for f in engine.facts if f[0] == "VERDICT"][0]
    print(f"\nKESIMPULAN: {verdict}")

    if args.trace:
        print("\nJejak inferensi (urutan rule yang menyala):")
        for rid, fact in engine.trace:
            print(f"  {rid:<4} => {fact}")


if __name__ == "__main__":
    main()
