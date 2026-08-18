const net = require('net');

const HOST = '127.0.0.1';
const PORT = 5001;

const client = new net.Socket();

client.connect(PORT, HOST, () => {

    console.log('[*] Conectado exitosamente al Servidor en Python');

    const payload = "Hola servidor, probando la comunicación inicial";

    const trama = {
        tipo: "SALUDO",
        longitud: payload.length,
        datos: payload
    };

    const mensajeEnvio = JSON.stringify(trama) + '\n';

    client.write(mensajeEnvio);

    console.log('[*] Trama enviada:');
    console.log(mensajeEnvio.trim());
});


client.on('data', (data) => {

    const mensaje = data.toString().trim();

    console.log('\n[+] Trama recibida del servidor:');
    console.log(mensaje);

    try {

        const respuesta = JSON.parse(mensaje);

        console.log('\n[*] Datos de la respuesta:');
        console.log('    - Tipo     :', respuesta.tipo);
        console.log('    - Longitud :', respuesta.longitud);
        console.log('    - Payload  :', respuesta.datos);

    } catch (error) {

        console.log('[-] Error: respuesta no válida.');

    }

    client.destroy();
});


client.on('close', () => {
    console.log('[*] Conexión cerrada limpiamente.');
});


client.on('error', (err) => {
    console.error('[-] Error en el cliente:', err.message);
});