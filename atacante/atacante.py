import socket
import threading
import json

HOST = '127.0.0.1'

# Puerto donde se conectará el cliente
PUERTO_ATACANTE = 5001

# Puerto donde está escuchando el servidor
PUERTO_SERVIDOR = 5000


def modificar_trama(trama):
    """
    Modifica intencionalmente el contenido del payload.
    Esta será nuestra falla de corrupción de datos.
    """

    try:
        mensaje = json.loads(trama)

        datos_originales = mensaje.get("datos", "")

        # Alteramos el payload
        datos_corruptos = datos_originales.replace(
            "comunicación",
            "comunicacxón"
        )

        # Si la palabra no aparece, hacemos otra modificación
        if datos_corruptos == datos_originales:
            datos_corruptos = datos_originales + " [CORRUPTO]"

        mensaje["datos"] = datos_corruptos

        trama_corrupta = json.dumps(mensaje)

        print("[ATACANTE] ⚠️ Trama modificada.")
        print("[ATACANTE] Original :")
        print(trama)

        print("[ATACANTE] Corrupta :")
        print(trama_corrupta)

        return trama_corrupta

    except json.JSONDecodeError:

        print("[ATACANTE] ❌ La trama no es JSON válido.")
        return trama


def cliente_a_servidor(cliente, servidor):
    """
    Intercepta las tramas del cliente, las modifica
    y luego las envía al servidor.
    """

    buffer = ""

    try:
        while True:

            datos = cliente.recv(1024)

            if not datos:
                break

            buffer += datos.decode("utf-8")

            while "\n" in buffer:

                trama, buffer = buffer.split("\n", 1)

                print("\n[ATACANTE] Trama interceptada:")
                print(trama)

                # CORRUPCIÓN DE DATOS
                trama_corrupta = modificar_trama(trama)

                mensaje = trama_corrupta + "\n"

                servidor.sendall(
                    mensaje.encode("utf-8")
                )

                print("[ATACANTE] Trama corrupta enviada al servidor.")

    except ConnectionResetError:

        print("[ATACANTE] Conexión cerrada por el cliente.")

    finally:

        try:
            servidor.shutdown(socket.SHUT_WR)
        except:
            pass


def servidor_a_cliente(servidor, cliente):
    """
    Reenvía las respuestas del servidor al cliente
    sin modificarlas.
    """

    try:
        while True:

            datos = servidor.recv(1024)

            if not datos:
                break

            cliente.sendall(datos)

            print("[ATACANTE] Respuesta del servidor reenviada al cliente.")

    except ConnectionResetError:

        print("[ATACANTE] Conexión cerrada por el servidor.")

    finally:

        try:
            cliente.shutdown(socket.SHUT_WR)
        except:
            pass


def iniciar_atacante():

    print("=" * 60)
    print("           ATACANTE - CORRUPCIÓN DE DATOS")
    print("=" * 60)

    print(f"[*] Escuchando en {HOST}:{PUERTO_ATACANTE}")
    print(f"[*] Servidor real en {HOST}:{PUERTO_SERVIDOR}")
    print()

    # Socket del atacante
    with socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    ) as atacante_socket:

        atacante_socket.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1
        )

        atacante_socket.bind(
            (HOST, PUERTO_ATACANTE)
        )

        atacante_socket.listen(1)

        print("[*] Esperando conexión del cliente...")

        cliente, direccion = atacante_socket.accept()

        print(f"[*] Cliente conectado desde {direccion}")

        # Conectar con el servidor real
        servidor = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        servidor.connect(
            (HOST, PUERTO_SERVIDOR)
        )

        print("[*] Conexión establecida con el servidor real.")
        print()

        # Hilo para cliente -> servidor
        hilo_cliente = threading.Thread(
            target=cliente_a_servidor,
            args=(cliente, servidor)
        )

        # Hilo para servidor -> cliente
        hilo_servidor = threading.Thread(
            target=servidor_a_cliente,
            args=(servidor, cliente)
        )

        hilo_cliente.start()
        hilo_servidor.start()

        hilo_cliente.join()
        hilo_servidor.join()

        cliente.close()
        servidor.close()

        print("[*] Atacante finalizado.")


if __name__ == "__main__":
    iniciar_atacante()