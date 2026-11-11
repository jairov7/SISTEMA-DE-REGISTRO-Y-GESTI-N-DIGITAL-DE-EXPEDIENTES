import os
from datetime import datetime
 
ARCHIVO = "expedientes.txt"
CAMPOS = ["codigo", "dni", "nombre", "tipo", "fecha", "estado"]
TIPOS = ["Carta de garantía", "Reclamo", "Solicitud de historia clínica", "Trámite administrativo"]
ESTADOS = ["Pendiente", "En proceso", "Atendido", "Rechazado"]
CLAVE_TRABAJADOR = "1234"
 
def cargar():
    if not os.path.exists(ARCHIVO):
        return []
    with open(ARCHIVO, "r", encoding="utf-8") as archivo:
        filas = [linea.strip().split("|") for linea in archivo]
    return [dict(zip(CAMPOS, fila)) for fila in filas if len(fila) == len(CAMPOS)]
 
def guardar(expedientes):
    with open(ARCHIVO, "w", encoding="utf-8") as archivo:
        for e in expedientes:
            archivo.write("|".join(e[campo] for campo in CAMPOS) + "\n")
 
def validar_datos(dni, nombre):
    return dni.isdigit() and len(dni) == 8 and len(nombre.split()) >= 2 and "|" not in nombre
 
def elegir(titulo, opciones):
    for i, opcion in enumerate(opciones, start=1):
        print(f"  {i}. {opcion}")
    n = input(titulo + ": ").strip()
    if n.isdigit() and 1 <= int(n) <= len(opciones):
        return opciones[int(n) - 1]
    print("Opción inválida.")
    return None
 
def mostrar(e):
    dni = "*" * 5 + e["dni"][-3:]
    print(f"  {e['codigo']} | {dni} | {e['nombre']} | {e['tipo']} | {e['fecha']} | {e['estado']}")
 
def buscar(expedientes, codigo):
    for e in expedientes:
        if e["codigo"] == codigo.strip().upper():
            return e
    return None
 
def registrar(expedientes):
    dni = input("DNI (8 dígitos): ").strip()
    nombre = input("Nombres y apellidos: ").strip()
    tipo = elegir("Tipo de trámite", TIPOS)
    if not validar_datos(dni, nombre) or tipo is None:
        print("Datos inválidos: revise el DNI, el nombre y el tipo de trámite.")
        return
    codigo = f"EXP{len(expedientes) + 1:03d}"
    fecha = datetime.now().strftime("%d/%m/%Y")
    expedientes.append(dict(zip(CAMPOS, [codigo, dni, nombre.title(), tipo, fecha, ESTADOS[0]])))
    guardar(expedientes)
    print("Solicitud registrada. Su código de trámite es:", codigo)
 
def consultar(expedientes):
    e = buscar(expedientes, input("Código de trámite: "))
    if e:
        mostrar(e)
    else:
        print("No se encontró el expediente.")
 
def siguiente_pendiente(expedientes):
    for e in expedientes:
        if e["estado"] == ESTADOS[0]:
            return e
    return None
 
def atender(expedientes):
    codigo = input("Código a atender (Enter = siguiente pendiente): ")
    e = buscar(expedientes, codigo) if codigo else siguiente_pendiente(expedientes)
    if e is None:
        print("No hay solicitud para atender.")
        return
    mostrar(e)
    nuevo = elegir("Nuevo estado", ESTADOS)
    if nuevo:
        e["estado"] = nuevo
        guardar(expedientes)
        print("Estado actualizado a:", nuevo)
 
def listar(expedientes):
    criterio = elegir("Ordenar por", ["codigo", "nombre", "estado"])
    if criterio:
        for e in sorted(expedientes, key=lambda x: x[criterio].lower()):
            mostrar(e)
 
def reporte(expedientes):
    for estado in ESTADOS:
        cantidad = len([e for e in expedientes if e["estado"] == estado])
        print(f"  {estado:<11}: {cantidad}")
    print(f"  {'Total':<11}: {len(expedientes)}")
 
def acceso_trabajador():
    for _ in range(3):
        if input("Clave de trabajador: ") == CLAVE_TRABAJADOR:
            return True
        print("Clave incorrecta.")
    return False
 
def menu(titulo, opciones, expedientes, salir="volver"):
    while True:
        print(f"\n===== {titulo} =====")
        for tecla, (texto, _) in opciones.items():
            print(f"{tecla}. {texto}")
        op = input(f"Opción (0 = {salir}): ").strip()
        if op == "0":
            return
        if op in opciones:
            opciones[op][1](expedientes)
        else:
            print("Opción inválida.")
 
def modo_paciente(expedientes):
    menu("PACIENTE", MENU_PACIENTE, expedientes)
 
def modo_trabajador(expedientes):
    if acceso_trabajador():
        menu("TRABAJADOR", MENU_TRABAJADOR, expedientes)
 
MENU_PACIENTE = {"1": ("Registrar solicitud", registrar), "2": ("Consultar mi trámite", consultar)}
MENU_TRABAJADOR = {"1": ("Atender solicitud", atender), "2": ("Buscar expediente", consultar),
                   "3": ("Listar expedientes ordenados", listar), "4": ("Reporte por estado", reporte)}
MENU_PRINCIPAL = {"1": ("Soy paciente", modo_paciente), "2": ("Soy trabajador", modo_trabajador)}
 
def main():
    menu("MEDIK CENTER SAN PABLO", MENU_PRINCIPAL, cargar(), "salir")
    print("Hasta luego.")
 
if __name__ == "__main__":
    main()