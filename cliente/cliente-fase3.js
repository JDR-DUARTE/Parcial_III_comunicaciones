//
const net = require("net");
const crypto = require("crypto");

const HOST = "127.0.0.1";
const PORT = 5000;
const MAX_REINTENTOS = 3;
const TIMEOUT_MS = 2000;

let intentos = 0;
let temporizador = null;
let client = null;

const payload = "Hola servidor, probando la comunicación inicial";

// Función para crear la huella digital
function calcularHash(texto) {
  return crypto.createHash("sha256").update(texto, "utf8").digest("hex");
}

// TRAMA
const tramaOriginal = {
  tipo: "SALUDO",
  longitud: payload.length,
  datos: payload,
  hash: calcularHash(payload),
};

function conectarYEnviar() {
  intentos++;
  console.log(
    `\n[>>>] Intento de comunicación ${intentos}/${MAX_REINTENTOS}...`,
  );

  client = new net.Socket();
  configurarEventosCliente();

  client.connect(PORT, HOST, () => {
    const mensajeEnvio = JSON.stringify(tramaOriginal) + "\n";
    client.write(mensajeEnvio);
    console.log("[*] Trama enviada. Esperando confirmación...");

    //  CONTROL DE FLUJO
    clearTimeout(temporizador);
    temporizador = setTimeout(() => {
      console.log(
        "[-] TIMEOUT: El servidor no respondió a tiempo (Posible pérdida o latencia).",
      );
      manejarFallo();
    }, TIMEOUT_MS);
  });
}

// RETRANSMISIÓN
function manejarFallo() {
  if (intentos < MAX_REINTENTOS) {
    console.log("[*] Iniciando retransmisión automática...\n");
    client.destroy();
    conectarYEnviar();
  } else {
    console.log(
      "[-] CRÍTICO: Límite de reintentos alcanzado. Abortando comunicación.",
    );
    client.destroy();
  }
}

function configurarEventosCliente() {
  client.on("data", (data) => {
    clearTimeout(temporizador); // Detenemos el reloj de arena ¡Llegó respuesta!
    const mensaje = data.toString().trim();

    console.log("[+] Respuesta recibida del servidor:");
    console.log(mensaje);

    try {
      const respuesta = JSON.parse(mensaje);

      // Bloque de Evaluación de respuesta
      if (respuesta.tipo === "ACK") {
        console.log(
          "\n[*] ÉXITO: El servidor confirmó la recepción correctamente (ACK).",
        );
        client.destroy();
      } else if (respuesta.tipo === "NACK") {
        //Retrasmitimos
        console.log(`\n[-] ERROR DEL SERVIDOR (NACK): ${respuesta.datos}`);
        manejarFallo();
      }
    } catch (error) {
      console.log("[-] Error al procesar la respuesta del servidor.");
      manejarFallo();
    }
  });

  client.on("close", () => {});
  //Manejo de errores
  client.on("error", (err) => {
    console.error(`[-] Error en la red: ${err.message}`);
    clearTimeout(temporizador);
    manejarFallo();
  });
}

conectarYEnviar();
