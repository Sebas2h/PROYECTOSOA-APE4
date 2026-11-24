async function solicitar(ruta, { token, method = 'GET', body, headers = {} } = {}, ejecutarFetch = fetch) {
  const h = new Headers({ Accept: 'application/json', ...headers });
  if (token) h.set('Authorization', `Bearer ${token}`);
  if (body !== undefined && !(body instanceof URLSearchParams)) h.set('Content-Type', 'application/json');
  if (body instanceof URLSearchParams) h.set('Content-Type', 'application/x-www-form-urlencoded');
  let respuesta;
  try {
    respuesta = await ejecutarFetch(ruta, {
      method, headers: h, body: body === undefined ? undefined :
        body instanceof URLSearchParams ? body : JSON.stringify(body), cache: 'no-store',
    });
  } catch { throw new Error('No se pudo conectar con los servicios.'); }
  const texto = await respuesta.text();
  let datos = null;
  if (texto) { try { datos = JSON.parse(texto); } catch { datos = { mensaje: texto }; } }
  if (!respuesta.ok) {
    const detalle = datos?.detail || datos?.mensaje || datos?.title || 'solicitud rechazada';
    const error = new Error(`HTTP ${respuesta.status}: ${detalle}`);
    error.codigoHttp = respuesta.status;
    throw error;
  }
  return { codigoHttp: respuesta.status, datos };
}

export function normalizarToken(token = '') { return String(token).trim().replace(/^Bearer\s+/i, '').trim(); }
export async function login({ usuario, clave, cliente, secreto }, ejecutarFetch) {
  const form = new URLSearchParams({ grant_type: 'password', username: usuario, password: clave });
  const basic = btoa(`${cliente}:${secreto}`);
  const r = await solicitar('/oauth/token', { method: 'POST', body: form,
    headers: { Authorization: `Basic ${basic}` } }, ejecutarFetch);
  if (!r.datos?.access_token) throw new Error('La autenticación no devolvió access_token.');
  return normalizarToken(r.datos.access_token);
}
export async function listarVehiculos(token, ejecutarFetch) {
  const r = await solicitar('/api/vehiculos', { token: normalizarToken(token) }, ejecutarFetch);
  if (!Array.isArray(r.datos)) throw new Error('La API debe devolver un arreglo JSON de vehículos.');
  return { codigoHttp: r.codigoHttp, vehiculos: r.datos };
}
export async function listarCompradores(token) {
  return (await solicitar('/api/compradores', { token })).datos;
}
export async function crearComprador(token, datos) {
  return (await solicitar('/api/compradores', { token, method: 'POST', body: datos })).datos;
}
export async function crearVenta(token, datos, clave) {
  return (await solicitar('/api/ventas', { token, method: 'POST', body: datos,
    headers: { 'Idempotency-Key': clave } })).datos;
}
export async function listarVentas(token) {
  const r = await solicitar('/api/ventas', { token: normalizarToken(token) });
  if (!Array.isArray(r.datos)) throw new Error('La API debe devolver un arreglo JSON de ventas.');
  return r.datos;
}
