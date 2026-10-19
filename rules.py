"""Basis pengetahuan (knowledge base) untuk validasi jadwal kuliah.

Fakta awal dari jadwal:
    ("class", code, lecturer, group, day, hour, room, students, capacity, is_lab, room_is_lab)
Fakta turunan tingkat-1 (dari data mentah):
    ("capacity_violation", code)          ("lab_violation", code)
    ("friday_prayer", code)               ("late_class", code)
    ("oversized_room", code)              ("lecturer_load", lecturer, day)
    ("lecturer_back_to_back", lecturer, day)   ("group_load", group, day)
Fakta turunan tingkat-2 (dari fakta tingkat-1, ini yang membuat "chaining"):
    ("ERROR", pesan)  ("WARNING", pesan)  ("SUGGESTION", pesan)
Fakta tingkat-3:
    ("VERDICT", "LAYAK" | "LAYAK DENGAN CATATAN" | "TIDAK LAYAK")
"""
from collections import defaultdict
from engine import Rule

HOURS_ORDER = ["07:00", "09:00", "11:00", "13:00", "15:00"]
LAST_HOUR = "15:00"
MAX_LECTURER_PER_DAY = 3
MAX_GROUP_PER_DAY = 3
OVERSIZED_MARGIN = 20          # kapasitas - mahasiswa > 20 -> ruangan terlalu besar


def _classes(facts):
    return [f for f in facts if f[0] == "class"]


# ---------------- Tingkat 1: deteksi kondisi dari data ----------------
def r1(facts):
    return [("capacity_violation", f[1]) for f in _classes(facts) if f[8] < f[7]]


def r2(facts):
    return [("lab_violation", f[1]) for f in _classes(facts) if f[9] != f[10]]


def r3(facts):
    return [("friday_prayer", f[1]) for f in _classes(facts)
            if f[4] == "Jum" and f[5] == "11:00"]


def r4(facts):
    return [("late_class", f[1]) for f in _classes(facts) if f[5] == LAST_HOUR]


def r5(facts):
    return [("oversized_room", f[1]) for f in _classes(facts)
            if f[8] - f[7] > OVERSIZED_MARGIN and not f[9]]


def r6(facts):
    cnt = defaultdict(int)
    for f in _classes(facts):
        cnt[(f[2], f[4])] += 1
    return [("lecturer_load", l, d) for (l, d), n in cnt.items() if n >= MAX_LECTURER_PER_DAY]


def r7(facts):
    by = defaultdict(list)
    for f in _classes(facts):
        by[(f[2], f[4])].append(HOURS_ORDER.index(f[5]))
    out = []
    for (l, d), idx in by.items():
        idx.sort()
        if any(b - a == 1 for a, b in zip(idx, idx[1:])):
            out.append(("lecturer_back_to_back", l, d))
    return out


def r8(facts):
    cnt = defaultdict(int)
    for f in _classes(facts):
        cnt[(f[3], f[4])] += 1
    return [("group_load", g, d) for (g, d), n in cnt.items() if n >= MAX_GROUP_PER_DAY]


# ---------------- Tingkat 2: kesimpulan & saran ----------------
def r9(facts):
    return [("ERROR", f"{f[1]}: kapasitas ruangan kurang dari jumlah mahasiswa")
            for f in facts if f[0] == "capacity_violation"] + \
           [("SUGGESTION", f"{f[1]}: pindahkan ke ruangan berkapasitas lebih besar")
            for f in facts if f[0] == "capacity_violation"]


def r10(facts):
    return [("ERROR", f"{f[1]}: praktikum/teori tidak sesuai jenis ruangan (lab vs non-lab)")
            for f in facts if f[0] == "lab_violation"] + \
           [("SUGGESTION", f"{f[1]}: tukar ke ruangan dengan jenis yang sesuai")
            for f in facts if f[0] == "lab_violation"]


def r11(facts):
    return [("ERROR", f"{f[1]}: bentrok dengan waktu sholat Jumat (Jum 11:00)")
            for f in facts if f[0] == "friday_prayer"] + \
           [("SUGGESTION", f"{f[1]}: pindahkan ke Jumat 13:00 atau hari lain")
            for f in facts if f[0] == "friday_prayer"]


def r12(facts):
    return [("WARNING", f"{f[1]}: kelas di jam terakhir ({LAST_HOUR}), mahasiswa/dosen rawan lelah")
            for f in facts if f[0] == "late_class"]


def r13(facts):
    return [("WARNING", f"{f[1]}: ruangan terlalu besar dari kebutuhan (pemborosan)")
            for f in facts if f[0] == "oversized_room"]


def r14(facts):
    """Chaining: beban tinggi DAN back-to-back -> peringatan kelelahan dosen."""
    heavy = {(f[1], f[2]) for f in facts if f[0] == "lecturer_load"}
    b2b = {(f[1], f[2]) for f in facts if f[0] == "lecturer_back_to_back"}
    out = []
    for l, d in heavy & b2b:
        out.append(("WARNING", f"{l} mengajar >= {MAX_LECTURER_PER_DAY} kelas berturut-turut di hari {d}"))
        out.append(("SUGGESTION", f"Pindahkan salah satu kelas {l} dari hari {d} ke hari lain"))
    for l, d in heavy - b2b:
        out.append(("WARNING", f"{l} mengajar >= {MAX_LECTURER_PER_DAY} kelas di hari {d}"))
    return out


def r15(facts):
    return [("WARNING", f"Kelas {f[1]} punya >= {MAX_GROUP_PER_DAY} mata kuliah di hari {f[2]} (padat)")
            for f in facts if f[0] == "group_load"]


# ---------------- Tingkat 3: keputusan akhir ----------------
def r16(facts):
    has_class = any(f[0] == "class" for f in facts)
    if not has_class:
        return []
    errors = any(f[0] == "ERROR" for f in facts)
    warns = any(f[0] == "WARNING" for f in facts)
    if errors:
        return [("VERDICT", "TIDAK LAYAK")]
    if warns:
        return [("VERDICT", "LAYAK DENGAN CATATAN")]
    return [("VERDICT", "LAYAK")]


RULES = [
    Rule("R1", "IF kapasitas ruangan < jumlah mahasiswa THEN capacity_violation", r1),
    Rule("R2", "IF jenis kelas (lab/non-lab) != jenis ruangan THEN lab_violation", r2),
    Rule("R3", "IF kelas di Jumat 11:00 THEN friday_prayer", r3),
    Rule("R4", f"IF kelas di jam {LAST_HOUR} THEN late_class", r4),
    Rule("R5", f"IF kapasitas - mahasiswa > {OVERSIZED_MARGIN} (non-lab) THEN oversized_room", r5),
    Rule("R6", f"IF dosen mengajar >= {MAX_LECTURER_PER_DAY} kelas sehari THEN lecturer_load", r6),
    Rule("R7", "IF dosen punya kelas di dua jam berurutan THEN lecturer_back_to_back", r7),
    Rule("R8", f"IF kelas mhs punya >= {MAX_GROUP_PER_DAY} MK sehari THEN group_load", r8),
    Rule("R9", "IF capacity_violation THEN ERROR + saran ganti ruangan", r9),
    Rule("R10", "IF lab_violation THEN ERROR + saran tukar ruangan", r10),
    Rule("R11", "IF friday_prayer THEN ERROR + saran pindah slot", r11),
    Rule("R12", "IF late_class THEN WARNING", r12),
    Rule("R13", "IF oversized_room THEN WARNING", r13),
    Rule("R14", "IF lecturer_load AND lecturer_back_to_back THEN WARNING + saran pindah hari", r14),
    Rule("R15", "IF group_load THEN WARNING", r15),
    Rule("R16", "IF ada ERROR THEN TIDAK LAYAK; ELIF ada WARNING THEN LAYAK DENGAN CATATAN; ELSE LAYAK", r16),
]
