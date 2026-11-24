import { login, listarVehiculos, listarCompradores, crearComprador, crearVenta } from './api.js';

const $ = (s) => document.querySelector(s);
const estado = { token: sessionStorage.getItem('ape04.jwt') || '', vehiculos: [], compradores: [] };
const mensaje = (texto, tipo = 'neutro') => { $('#mensaje').textContent = texto; $('#mensaje').className = `mensaje ${tipo}`; };
const texto = (v) => v ?? '—';

function pintarVehiculos() {
  const contenedor = $('#vehiculos'); contenedor.replaceChildren();
  $('#contador').textContent = `${estado.vehiculos.length} vehículo(s)`;
  $('#vehiculoId').replaceChildren(new Option('Seleccione…', ''));
  for (const v of estado.vehiculos) {
    const id = v.idVehiculo ?? v.id;
    const tarjeta = document.createElement('article'); tarjeta.className = 'vehiculo';
    tarjeta.innerHTML = '<div class="vehiculo-cabecera"><div><h3 class="vehiculo-titulo"></h3><span class="vehiculo-id"></span></div><span class="estado"></span></div><div class="datos"></div>';
    tarjeta.querySelector('h3').textContent = `${texto(v.marca)} ${texto(v.modelo)}`;
    tarjeta.querySelector('.vehiculo-id').textContent = `ID: ${id}`;
    tarjeta.querySelector('.estado').textContent = texto(v.estado);
    tarjeta.querySelector('.datos').textContent = `Placa ${texto(v.placa)} · Precio $${texto(v.precio)}`;
    contenedor.append(tarjeta);
    if (String(v.estado).toUpperCase() === 'DISPONIBLE') $('#vehiculoId').add(new Option(`${id} · ${v.marca} ${v.modelo}`, id));
  }
  if (!estado.vehiculos.length) contenedor.textContent = 'No hay vehículos registrados.';
}

function pintarCompradores() {
  const select = $('#compradorId'); select.replaceChildren(new Option('Seleccione…', ''));
  for (const c of estado.compradores) select.add(new Option(`${c.id} · ${c.nombre}`, c.id));
}

function mostrarVista(nombre) {
  $('#loginPanel').classList.add('oculto');
  $('#menuWrap').classList.remove('oculto');
  $('#dashboard').classList.toggle('oculto', nombre !== 'dashboard');
  $('#vistaCatalogo').classList.toggle('oculto', nombre !== 'catalogo');
  $('#vistaCompradores').classList.toggle('oculto', nombre !== 'compradores');
  $('#vistaVentas').classList.toggle('oculto', nombre !== 'ventas');
  $('#menuOpciones').classList.add('oculto');
  $('#menuBtn').setAttribute('aria-expanded', 'false');
}

function actualizarResumen() {
  $('#resumenVehiculos').textContent = estado.vehiculos.filter(v => String(v.estado).toUpperCase() === 'DISPONIBLE').length;
  $('#resumenCompradores').textContent = estado.compradores.length;
}

function activarDashboard() {
  $('#loginPanel').classList.add('oculto');
  $('#menuWrap').classList.remove('oculto');
  $('#dashboard').classList.remove('oculto');
  $('#saludo').textContent = `Bienvenido, ${$('#usuario').value || 'operador'}`;
  mostrarVista('dashboard');
  actualizarResumen();
}

async function refrescar() {
  if (!estado.token) throw new Error('Primero inicie sesión.');
  const [v, c] = await Promise.all([listarVehiculos(estado.token), listarCompradores(estado.token)]);
  estado.vehiculos = v.vehiculos; estado.compradores = c; pintarVehiculos(); pintarCompradores(); actualizarResumen();
}

$('#loginForm').addEventListener('submit', async (e) => {
  e.preventDefault(); $('#loginBtn').disabled = true;
  try {
    estado.token = await login({ usuario: $('#usuario').value, clave: $('#clave').value,
      cliente: $('#cliente').value, secreto: $('#secreto').value });
    sessionStorage.setItem('ape04.jwt', estado.token); $('#clave').value = ''; $('#secreto').value = '';
    activarDashboard();
    refrescar().catch((ex) => mensaje(`Sesión iniciada; no se pudieron cargar los datos: ${ex.message}`, 'error'));
    mensaje('Sesión iniciada. Bienvenido.', 'exito');
  } catch (ex) { estado.token = ''; sessionStorage.removeItem('ape04.jwt'); mensaje(ex.message, 'error'); }
  finally { $('#loginBtn').disabled = false; }
});

$('#logout').addEventListener('click', () => {
  estado.token = ''; sessionStorage.removeItem('ape04.jwt'); estado.vehiculos = []; estado.compradores = [];
  pintarVehiculos(); pintarCompradores(); $('#menuWrap').classList.add('oculto'); $('#dashboard').classList.add('oculto'); $('#loginPanel').classList.remove('oculto');
  $('#clave').value = ''; $('#secreto').value = ''; $('#menuOpciones').classList.add('oculto');
  $('#loginPanel').classList.remove('oculto');
  mostrarVista('login'); actualizarResumen(); mensaje('Sesión cerrada.');
});
$('#salirBtn').addEventListener('click', () => $('#logout').click());
$('#menuBtn').addEventListener('click', () => {
  const opciones = $('#menuOpciones'); opciones.classList.toggle('oculto');
  $('#menuBtn').setAttribute('aria-expanded', String(!opciones.classList.contains('oculto')));
});
document.querySelectorAll('[data-vista]').forEach(boton => boton.addEventListener('click', () => mostrarVista(boton.dataset.vista)));
$('#actualizar').addEventListener('click', async () => {
  try { await refrescar(); mensaje('Catálogo actualizado.', 'exito'); } catch (ex) { mensaje(ex.message, 'error'); }
});
$('#compradorForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  try {
    if (!estado.token) throw new Error('Inicia sesión para continuar.');
    await crearComprador(estado.token, { documento: $('#documento').value, nombre: $('#nombre').value, correo: $('#correo').value });
    await refrescar(); e.target.reset(); mensaje('Comprador creado.', 'exito');
  } catch (ex) { mensaje(ex.message, 'error'); }
});
$('#ventaForm').addEventListener('submit', async (e) => {
  e.preventDefault(); const boton = $('#vender'); boton.disabled = true;
  const clave = $('#idempotencia').value || crypto.randomUUID().replaceAll('-', '');
  $('#idempotencia').value = clave;
  try {
    if (!estado.token) throw new Error('Inicia sesión para continuar.');
    const venta = await crearVenta(estado.token, { vehiculoId: Number($('#vehiculoId').value), compradorId: Number($('#compradorId').value) }, clave);
    await refrescar(); mensaje(`Venta ${venta.id}: ${venta.estado}; notificación ${venta.notificacion}.`, 'exito');
  } catch (ex) { mensaje(`Venta no completada: ${ex.message}. Reintente con la misma clave.`, 'error'); }
  finally { boton.disabled = false; }
});

$('#conexion').textContent = navigator.onLine ? 'Navegador conectado' : 'Sin conexión';
if (estado.token) refrescar().then(activarDashboard).catch(() => {
  estado.token = ''; sessionStorage.removeItem('ape04.jwt');
  $('#loginPanel').classList.remove('oculto'); $('#dashboard').classList.add('oculto'); $('#menuWrap').classList.add('oculto');
  mensaje('La sesión venció o no se pudo validar. Inicia sesión nuevamente.', 'error');
});
else {
  $('#loginPanel').classList.remove('oculto'); $('#dashboard').classList.add('oculto'); $('#menuWrap').classList.add('oculto');
  $('#vistaCatalogo').classList.add('oculto'); $('#vistaCompradores').classList.add('oculto'); $('#vistaVentas').classList.add('oculto');
}
if ('serviceWorker' in navigator && window.isSecureContext) navigator.serviceWorker.register('/sw.js').catch(() => {});
