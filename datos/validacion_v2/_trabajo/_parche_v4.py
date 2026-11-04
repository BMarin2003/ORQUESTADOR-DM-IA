from pathlib import Path
f = Path(r"C:\BMARIN2003\DEV\proyecto\experimento\scripts\reporte_v2\recalcular_persona2_v4.py")
s = f.read_text(encoding="utf-8-sig")
lines = s.split("\n")
out = []
for ln in lines:
    if ln.startswith("RAYAS = "):
        out.append('RAYAS = ("\\u2014", "\\u2013", "\\u2015")   # raya, semirraya, barra horizontal (diálogo)')
        out.append('PERSP_PNJ = re.compile(r"\\b(saben?|comprenden?|comprender|entienden?|entender|creen?|piensan?|dicen?|'
                   'asumen?|suponen?|intuyen?|notan?|ven)\\b(?:\\s+\\w+){0,3}?\\s+que\\b[^.;:!?]*$")')
    else:
        out.append(ln)
s = "\n".join(out)
assert "PERSP_PNJ = re" in s and 'return "R9"' in s
f.write_text(s, encoding="utf-8")
print("ok")
