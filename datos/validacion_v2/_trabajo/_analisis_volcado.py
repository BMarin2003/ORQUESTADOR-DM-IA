import json, sys, re, collections, random
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
L = [json.loads(x) for x in open(Path(__file__).with_name("_volcado_v4.jsonl"), encoding="utf-8")]
print("hallazgos (sin R1):", len(L))
c = collections.Counter((x["brazo"], x["cat"], x["motivo"] or "CUENTA") for x in L)
for k, v in sorted(c.items()):
    print(f"  {v:5d} {k}")
print("\nsin tirada:", collections.Counter((x["brazo"], x["cat"]) for x in L if not x["d20"]))
print("\nCOGNICION lemas (todas):", collections.Counter(x["lema"] for x in L if x["cat"] == "COGNICION").most_common(25))
print("\nVOLICION lemas:", collections.Counter((x["lema"], x["motivo"]) for x in L if x["cat"] == "VOLICION").most_common(25))
print("\nHABLA lemas:", collections.Counter((x["lema"], x["motivo"]) for x in L if x["cat"] == "HABLA").most_common(15))
EMO = re.compile(r"\b(miedo|temor|terror|panico|angustia|ansiedad|inquietud|nerviosismo|frustracion|decepcion|alivio|satisfaccion|"
                 r"esperanza|alegria|euforia|tristeza|desaliento|impotencia|sorpresa|asombro|asco|repugnancia|nausea|rabia|ira|furia|"
                 r"odio|rencor|desprecio|amor|carino|ternura|gratitud|admiracion|compasion|lastima|culpa|verguenza|orgullo|remordimiento|"
                 r"celos|envidia|lealtad|confianza|desconfianza|vulnerab\w*|soledad|nostalgia|melancolia|calma|serenidad|tension|"
                 r"pavor|horror|escalofrio|vertigo|determinacion|resolucion|duda\w*|curiosidad|fascinacion|incomodidad|desasosiego)\b")
import unicodedata
def pl(s): return "".join(ch for ch in unicodedata.normalize("NFD", s.lower()) if unicodedata.category(ch) != "Mn")
emo = collections.Counter()
for x in L:
    if x["cat"] == "EMOCION":
        m = EMO.findall(pl(x["ctx"][80:]))
        emo[(m[0] if m else "?", x["motivo"] or "CUENTA")] += 1
print("\nEMOCION sustantivo (primer match tras el disparador):", emo.most_common(40))
random.seed(1)
cu = [x for x in L if x["motivo"] is None]
print("\nMUESTRA de los que CUENTAN en v4 (12):")
for x in random.sample(cu, min(12, len(cu))):
    print(f" [{x['par']} {x['brazo']} t{x['t']}] {x['cat']} {x['lema']} d20={x['d20']} {x['hab']}\n    DM: …{x['ctx']}…\n    ACC: {x['accion'][:160]!r}")
