import subprocess, tempfile, shutil, os, sys, json, re
 
d = tempfile.mkdtemp(); shutil.copy("medik_center.py", d)
def run(inputs):
    r = subprocess.run([sys.executable, "medik_center.py"], input="\n".join(inputs) + "\n", capture_output=True, text=True, cwd=d, timeout=20)
    return r.stdout
def archivo(): 
    p = os.path.join(d, "expedientes.txt"); return open(p, encoding="utf-8").read().strip().splitlines() if os.path.exists(p) else []
def reg(dni, nom, tipo): return ["1", "1", dni, nom, tipo, "0", "0"]
R = []
def caso(cod, entrada, esperado, obtenido, ok): R.append((cod, entrada, esperado, obtenido, ok))
 
o = run(reg("45871236", "juan perez ruiz", "1"))
caso("CP01", "DNI 45871236, juan perez ruiz, tipo 1 (carta de garantía)", "Registro correcto con código", "Código asignado EXP001; archivo: " + archivo()[0], "EXP001" in o and len(archivo()) == 1)
o = run(reg("1234", "juan", "9"))
caso("CP02", "DNI 1234, nombre de 1 palabra, tipo 9", "Mensaje de validación; no registra", "“Datos inválidos…”; el archivo sigue con %d registro" % len(archivo()), "Datos inválidos" in o and len(archivo()) == 1)
o = run(reg("45871236", "Ana|Luz Ruiz", "1"))
caso("CP02b", "Nombre con el carácter “|”", "Rechazado por validación", "“Datos inválidos…”", "Datos inválidos" in o and len(archivo()) == 1)
run(reg("70123456", "ana torres quispe", "3")); run(reg("20512345", "luis diaz mamani", "2"))
o = run(["1", "2", "EXP001", "0", "0"])
caso("CP03", "Consultar EXP001 (existente)", "Registro localizado", "Muestra EXP001 con el DNI enmascarado *****236", "Juan Perez Ruiz" in o and "*****236" in o)
o = run(["1", "2", "EXP999", "0", "0"])
caso("CP04", "Consultar EXP999 (inexistente)", "Mensaje de no encontrado", "“No se encontró el expediente.”", "No se encontró el expediente" in o)
o = run(["2", "1234", "3", "2", "0", "0"])
nombres = [m[1] for m in re.findall(r"(EXP\d+) \| \*+\d{3} \| (.+?) \| ", o)]
caso("CP05", "Trabajador: listar ordenado por nombre", "Registros ordenados A-Z", " < ".join(nombres), nombres == sorted(nombres, key=str.lower) and len(nombres) == 3)
o = run(["2", "1234", "3", "1", "0", "0"])
cods = [m[0] for m in re.findall(r"(EXP\d+) \| \*+\d{3} \| (.+?) \| ", o)]
caso("CP06", "Cerrar y abrir el programa; listar por código", "Datos guardados disponibles", "Recuperó " + ", ".join(cods), cods == ["EXP001", "EXP002", "EXP003"])
o = run(["1", "2", "exp001", "0", "0"])
caso("CP07", "Consultar “exp001” en minúscula", "Registro localizado", "Encontró EXP001", "Juan Perez Ruiz" in o)
o = run(["2", "0000", "1111", "2222", "0"])
caso("CP08", "Trabajador con clave incorrecta (3 intentos)", "Acceso denegado", "3 veces “Clave incorrecta.” y vuelve al menú principal", o.count("Clave incorrecta.") == 3 and "===== TRABAJADOR" not in o)
o = run(["2", "1234", "1", "", "2", "0", "0"])
caso("CP09", "Atender siguiente pendiente (Enter) y elegir “En proceso”", "EXP001 pasa a En proceso", "Archivo: " + archivo()[0].split("|")[-1], archivo()[0].endswith("En proceso") and "Estado actualizado a: En proceso" in o)
o = run(["2", "1234", "1", "EXP003", "3", "0", "0"])
caso("CP10", "Atender EXP003 por código y elegir “Atendido”", "EXP003 pasa a Atendido", "Archivo: " + archivo()[2].split("|")[-1], archivo()[2].endswith("Atendido"))
o = run(["2", "1234", "4", "0", "0"])
caso("CP11", "Reporte por estado", "Conteo correcto", "Pendiente 1, En proceso 1, Atendido 1, Total 3", all(x in o for x in ["Pendiente  : 1", "En proceso : 1", "Atendido   : 1", "Total      : 3"]))
run(["2", "1234", "1", "", "4", "0", "0"])
o = run(["2", "1234", "1", "", "0", "0"])
caso("CP12", "Atender (Enter) sin solicitudes pendientes", "Mensaje informativo", "“No hay solicitud para atender.”", "No hay solicitud para atender" in o)
o = run(["9", "0"])
caso("CP13", "Opción 9 en el menú principal", "Mensaje de opción inválida", "“Opción inválida.”", "Opción inválida" in o)
for r in R: print(r[0], "OK " if r[4] else "FALLA", "|", r[1], "|", r[3])
print("TOTAL", sum(r[4] for r in R), "de", len(R))
json.dump(R, open("resultados_v3.json", "w"), ensure_ascii=False, indent=1)
print(open(os.path.join(d, "expedientes.txt"), encoding="utf-8").read())
shutil.rmtree(d)