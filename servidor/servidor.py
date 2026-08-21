import socket
import json


HOST = '127.0.0.1'
PORT = 5000


def iniciar_servidor():

    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:

        server_socket.bind((HOST, PORT))
        server_socket.listen()

        print(f"[*] Servidor iniciado.")
        print(f"[*] Escuchando en {HOST}:{PORT}...")

        conn, addr = server_socket.accept()

        with conn:

            print(f"[*] Conexión establecida desde {addr}")

            buffer = ""

            while True:

                
                data = conn.recv(1024)

                if not data:
                    print("[*] Cliente desconectado.")
                    break

                buffer += data.decode('utf-8')

                while '\n' in buffer:

                    mensaje_raw, buffer = buffer.split('\n', 1)

                    print("\n[+] Trama recibida:")
                    print(mensaje_raw)

                    try:

                      
                        trama = json.loads(mensaje_raw)

                        tipo = trama.get("tipo")
                        longitud = trama.get("longitud")
                        payload = trama.get("datos")

                        print("    - Tipo     :", tipo)
                        print("    - Longitud :", longitud)
                        print("    - Payload  :", payload)

                        
                        respuesta_texto = (
                            f"Servidor recibió '{payload}' correctamente!"
                        )

                        trama_respuesta = {
                            "tipo": "RESPUESTA_OK",
                            "longitud": len(respuesta_texto),
                            "datos": respuesta_texto
                        }

                      
                        mensaje_envio = (
                            json.dumps(trama_respuesta) + '\n'
                        )

                      
                        conn.sendall(
                            mensaje_envio.encode('utf-8')
                        )

                        print("[*] Respuesta enviada.")

                    except json.JSONDecodeError:

                        print(
                            "[-] Error: la trama no tiene "
                            "un formato JSON válido."
                        )


if __name__ == "__main__":
    iniciar_servidor()