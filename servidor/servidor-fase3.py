import socket
import json
import hashlib

# Configuración inicial
HOST = '127.0.0.1'
PORT = 5000

def generar_hash(texto):
    """Genera una huella digital (Hash SHA-256) del texto."""
    return hashlib.sha256(texto.encode('utf-8')).hexdigest()

def enviar_respuesta(conn, tipo, mensaje):
    """Función para enviar respuestas estandarizadas (ACK / NACK)."""
    trama_respuesta = {
        "tipo": tipo,
        "longitud": len(mensaje),
        "datos": mensaje
    }
    mensaje_envio = json.dumps(trama_respuesta) + '\n'
    conn.sendall(mensaje_envio.encode('utf-8'))
    print(f"[*] Respuesta enviada: {tipo}")

def iniciar_servidor():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print(f"[*] Servidor Blindado (Fase 3) iniciado.")
        print(f"[*] Escuchando en {HOST}:{PORT}...")

        # Agregamos un bucle exterior para que el servidor nunca muera
        while True:
            conn, addr = server_socket.accept()
            with conn:
                print(f"\n[*] Conexión establecida desde {addr}")
                buffer = ""

                while True:
                    try:
                        # Recibir datos
                        data = conn.recv(1024)
                        if not data:
                            print("[*] Cliente desconectado limpiamente.")
                            break

                        # 1. MANEJO DE EXCEPCIONES: Atrapamos la basura de Clumsy
                        buffer += data.decode('utf-8')

                        # Procesar todos los mensajes completos
                        while '\n' in buffer:
                            mensaje_raw, buffer = buffer.split('\n', 1)
                            print("\n[+] Trama recibida:")
                            print(mensaje_raw)

                            try:
                                # Convertir JSON
                                trama = json.loads(mensaje_raw)
                                tipo = trama.get("tipo")
                                longitud = trama.get("longitud")
                                payload = trama.get("datos", "")
                                hash_recibido = trama.get("hash") # Nuevo campo esperado

                                print("    - Tipo     :", tipo)
                                print("    - Payload  :", payload)
                                print("    - Hash Rx  :", hash_recibido)

                                # 2. VERIFICACIÓN DE INTEGRIDAD
                                hash_calculado = generar_hash(payload)
                                
                                if hash_recibido and hash_calculado != hash_recibido:
                                    print("[-] ALERTA: Fallo de integridad. El mensaje fue alterado.")
                                    enviar_respuesta(conn, "NACK", "Error de integridad (Hash incorrecto)")
                                    continue # Ignoramos este paquete y seguimos escuchando

                                # 3. CONTROL DE FLUJO: Todo está perfecto, enviamos ACK
                                respuesta_texto = f"Servidor recibió '{payload}' intacto."
                                enviar_respuesta(conn, "ACK", respuesta_texto)

                            except json.JSONDecodeError:
                                print("[-] Error: la trama no tiene un formato JSON válido.")
                                enviar_respuesta(conn, "NACK", "Formato JSON inválido")

                    except UnicodeDecodeError:
                        print("[-] ERROR CRÍTICO ATRAPADO: Paquete corrupto a nivel de bits.")
                        enviar_respuesta(conn, "NACK", "Datos irreconocibles por interferencia.")
                        buffer = "" # Vaciamos la basura para que no trabe los siguientes mensajes
                        
                    except ConnectionResetError:
                        print("[-] El cliente cerró la conexión por timeout (Latencia alta).")
                        break

if __name__ == "__main__":
    iniciar_servidor()