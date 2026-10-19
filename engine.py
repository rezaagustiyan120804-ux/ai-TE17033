Fakta  : tuple, mis. ("class", "AI101", ...) atau ("heavy_day", "Dr. Andi", "Sen")
Rule   : IF kondisi(fakta) THEN tambah fakta baru.
Mesin  : ulangi semua rule sampai tidak ada fakta baru (fixed point).
Setiap fakta turunan mencatat rule mana yang menghasilkannya -> bisa dijelaskan.
"""
from dataclasses import dataclass
from typing import Callable


@dataclass
class Rule:
    rid: str
    description: str                      # teks IF ... THEN ... untuk ditampilkan
    apply: Callable[[set], list]          # (facts) -> list fakta baru


class ForwardChainingEngine:
    def __init__(self, rules):
        self.rules = rules
        self.facts = set()
        self.trace = []                   # (rule_id, fakta_baru)

    def assert_fact(self, fact):
        self.facts.add(fact)

    def run(self):
        changed = True
        while changed:
            changed = False
            for rule in self.rules:
                for fact in rule.apply(self.facts):
                    if fact not in self.facts:
                        self.facts.add(fact)
                        self.trace.append((rule.rid, fact))
                        changed = True
        return self.facts
