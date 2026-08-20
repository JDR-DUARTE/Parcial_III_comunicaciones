# Parcial III: Diseño, Adversidad y Robustecimiento de Protocolos de Comunicación

Este repositorio contiene la implementación de un protocolo de comunicación cliente-servidor de capa de aplicación, diseñado para tolerar fallos e interferencias en la red.

## Equipo de Trabajo (Roles)

- Jessica Ramírez
- Enderson Chávez
- Mauro León

---

## Requisitos del Entorno

Para ejecutar este proyecto y replicar las pruebas, es necesario contar con:

- **Node.js** (v14 o superior) para ejecutar el Cliente.
- **Python** (v3.8 o superior) para ejecutar el Servidor.
- **Clumsy 0.3** (Solo Windows) para la inyección de fallas en localhost.
- **Wireshark** (Opcional) para el monitoreo y análisis de tramas a nivel de red.

---

## Instrucciones de Ejecución

El proyecto está diseñado para ejecutarse de manera local (Loopback: `127.0.0.1` en el puerto `5000`). Se recomienda abrir dos terminales independientes.

### 1. Iniciar el Servidor

Abre una terminal en la carpeta "servidor" del proyecto y ejecuta el servidor en Python:

```bash
python servidor_fase_3.py
```

El servidor indicará en consola que está escuchando conexiones.

### 2. Iniciar el Cliente

Abre una segunda terminal en la carpeta "cliente" y ejecuta el cliente en Node.js:

```bash
node cliente_fase_3.js
```

Al hacer esto el cliente calculará el hash SHA-256 del mensaje, iniciará su temporizador y enviará la trama al servidor.

---

## Guía de Pruebas de Adversidad

Esta serie de pasos se pueden realizar ejecutando los archivos "cliente.py" y "servidor.js" para ver fallos por una mala configuración de los protocolos, luego se pueden volver a hacer las pruebas, esta vez ejecutando "cliente-fase3.js" y "servidor-fase3.py" en sus respectivas terminales, para visualizar los efectos de hacer un sistema mas robusto.

Para evaluar la tolerancia a fallos del protocolo, abrir **Clumsy 0.3**, aplicar el filtro `outbound and loopback` y activa las siguientes funciones una por una:

1. **Prueba de Latencia (Lag):**
   - Configuración: Activar `Lag`, Delay: `1000` ms, Inbound & Outbound.
   - Resultado esperado: El cliente detectará el _Timeout_ a los 2000 ms y retransmitirá el paquete automáticamente.

2. **Prueba de Pérdida de Paquetes (Drop):**
   - Configuración: Activar `Drop`, Chance: `50%`, Inbound & Outbound.
   - Resultado esperado: Ante la pérdida, el cliente aplicará el mecanismo _Stop-and-Wait_ y reintentará la comunicación hasta un límite de 3 veces.

3. **Prueba de Corrupción de Datos (Tamper):**
   - Configuración: Activar `Tamper`, Chance: `50%`, activar `Redo Checksum`, Inbound & Outbound.
   - Resultado esperado: El servidor detectará que el Hash SHA-256 no coincide con el _payload_ alterado, rechazará la trama y enviará un "NACK" al cliente.

---

## Estructura del Repositorio

- `/src`
  - `cliente_fase_3.js`: Código fuente del cliente robustecido.
  - `servidor_fase_3.py`: Código fuente del servidor robustecido.
- `/docs`
  - `informe.pdf`: Especificación del protocolo, bitácora de adversidad y matriz de errores.
- `README.md`: Este archivo.
