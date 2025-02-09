from pyftpdlib.servers import FTPServer
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler


def main():
    # Creamos un "authorizer" que gestiona usuarios virtuales
    authorizer = DummyAuthorizer()

    # Permisos que existen (el, r, a, d, f, m, w, M, T)
    authorizer.add_user("admin", "admin", "./resources", perm="elradfmwMT")

    # Configura el manejador FTP y asigna el authorizer
    handler = FTPHandler
    handler.authorizer = authorizer
    handler.banner = "[+] Bienvenido al servidor de archivos de idealistas"

    # Definimos la dirección y puerto en el que se escucharán conexiones
    address = ("127.0.0.1", 2121)

    server = FTPServer(address, handler)
    print(f"Servidor FTP en ejecución en el puerto {address[1]}")
    server.serve_forever()

if __name__ == "__main__":
    main()
