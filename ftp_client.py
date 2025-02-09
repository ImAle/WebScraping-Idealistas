import ftplib
import os

def conectar_ftp():
    host = "127.0.0.1"
    puerto = 2121
    usuario = input("Usuario: ")
    password = input("Contraseña: ")
    ftp = ftplib.FTP()
    ftp.connect(host, puerto)
    ftp.login(usuario, password)
    print(f"Conectado a {host}:{puerto}")
    return ftp

def crear_carpeta(ftp):
    carpeta = input("Nombre de la carpeta a crear: ")
    try:
        ftp.mkd(carpeta)
        print("Carpeta creada.")
    except Exception as e:
        print("Error:", e)

def borrar_carpeta(ftp):
    carpeta = input("Nombre de la carpeta a borrar: ")
    try:
        ftp.rmd(carpeta)
        print("Carpeta borrada.")
    except Exception as e:
        print("Error:", e)

def subir_archivo(ftp):
    ruta_local = input("Ruta del archivo local a subir: ")
    if not os.path.isfile(ruta_local):
        print("El archivo no existe.")
        return
    remoto = input("Nombre remoto (deje vacío para usar el mismo): ")
    if not remoto:
        remoto = os.path.basename(ruta_local)
    try:
        with open(ruta_local, "rb") as f:
            ftp.storbinary(f"STOR {remoto}", f)
        print("Archivo subido.")
    except Exception as e:
        print("Error:", e)

def descargar_archivo(ftp):
    remoto = input("Nombre del archivo remoto a descargar: ")
    local = input("Nombre local (deje vacío para usar el mismo): ")
    if not local:
        local = remoto
    try:
        with open(local, "wb") as f:
            ftp.retrbinary(f"RETR {remoto}", f.write)
        print("Archivo descargado.")
    except Exception as e:
        print("Error:", e)

def borrar_archivo(ftp):
    remoto = input("Nombre del archivo remoto a borrar: ")
    try:
        ftp.delete(remoto)
        print("Archivo borrado.")
    except Exception as e:
        print("Error:", e)

def listar_contenido(ftp):
    carpeta = input("Carpeta a listar (deje vacío para raíz): ")
    try:
        lista = ftp.nlst(carpeta) if carpeta else ftp.nlst()
        print("Contenido:")
        directorio_actual = ftp.pwd()
        for item in lista:
            try:
                ftp.cwd(item)
                # Si se pudo cambiar de directorio, es un directorio.
                print(f"[DIR]  {item}")
                ftp.cwd(directorio_actual)
            except ftplib.error_perm:
                # Si falla, asumimos que es un archivo.
                print(f"[FILE] {item}")
    except Exception as e:
        print("Error:", e)

def menu(ftp):
    while True:
        print("\n--- MENÚ FTP ---")
        print("1. Crear una carpeta")
        print("2. Borrar una carpeta")
        print("3. Subir un archivo")
        print("4. Descargar un archivo")
        print("5. Borrar un archivo")
        print("6. Listar contenido de una carpeta")
        print("7. Salir")
        opcion = input("Seleccione una opción: ")
        if opcion == "1":
            crear_carpeta(ftp)
        elif opcion == "2":
            borrar_carpeta(ftp)
        elif opcion == "3":
            subir_archivo(ftp)
        elif opcion == "4":
            descargar_archivo(ftp)
        elif opcion == "5":
            borrar_archivo(ftp)
        elif opcion == "6":
            listar_contenido(ftp)
        elif opcion == "7":
            break
        else:
            print("Opción inválida.")

def main():
    ftp = conectar_ftp()
    menu(ftp)
    ftp.quit()
    print("Conexión cerrada.")

if __name__ == "__main__":
    main()
