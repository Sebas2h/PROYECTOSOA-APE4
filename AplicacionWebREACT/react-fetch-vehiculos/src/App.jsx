import { useState } from 'react';
import { listarVehiculos, listarVentas } from './api/vehiculosApi.js';
import './App.css';

const dinero = new Intl.NumberFormat('es-EC', { style: 'currency', currency: 'USD' });

function mostrarPrecio(precio) {
  if (precio === null || precio === undefined || precio === '') return '—';
  const numero = Number(precio);
  return Number.isFinite(numero) ? dinero.format(numero) : String(precio);
}

function estadoVehiculo(estado) {
  const valor = String(estado ?? '—').toUpperCase();
  const vendido = valor.includes('VEND') || valor.includes('SOLD');
  return <span className={`state-pill${vendido ? ' sold' : ''}`}>{valor}</span>;
}

export default function App() {
  const [token, setToken] = useState('');
  const [mostrarToken, setMostrarToken] = useState(false);
  const [vehiculos, setVehiculos] = useState([]);
  const [ventas, setVentas] = useState([]);
  const [marca, setMarca] = useState('');
  const [seleccionado, setSeleccionado] = useState(null);
  const [cargando, setCargando] = useState(false);
  const [mensaje, setMensaje] = useState('Pega tu JWT para conectar con los servicios.');
  const [error, setError] = useState('');
  const [codigoHttp, setCodigoHttp] = useState(null);

  const visibles = vehiculos.filter((v) =>
    String(v.marca ?? '').toLowerCase().includes(marca.trim().toLowerCase()),
  );

  async function consultarVehiculos(evento) {
    evento.preventDefault();
    setCargando(true);
    setError('');
    setMensaje('Consultando vehículos y ventas...');
    setCodigoHttp(null);
    setVehiculos([]);
    setVentas([]);
    setSeleccionado(null);

    try {
      const [resultado, ventasResultado] = await Promise.all([
        listarVehiculos(token),
        listarVentas(token),
      ]);
      setVehiculos(resultado.vehiculos);
      setVentas(ventasResultado);
      setCodigoHttp(resultado.codigoHttp);
      setMensaje(`Consulta correcta: ${resultado.vehiculos.length} vehículos y ${ventasResultado.length} ventas.`);
    } catch (e) {
      setCodigoHttp(e.status ?? null);
      setError(e.message);
      setMensaje('La consulta no pudo completarse.');
    } finally {
      setCargando(false);
    }
  }

  function limpiarToken() {
    setToken('');
    setMostrarToken(false);
    setVehiculos([]);
    setVentas([]);
    setSeleccionado(null);
    setCodigoHttp(null);
    setError('');
    setMensaje('Pega tu JWT para conectar con los servicios.');
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <a className="brand" href="#inicio" aria-label="Vía Motor inicio">
          <span className="brand-mark">V</span>
          <span className="brand-copy"><small>APE 04 · GESTIÓN</small><strong>Vía Motor</strong></span>
        </a>
        <div className="top-status"><i className="status-dot" />Cliente web · React + Fetch</div>
      </header>

      <section className="hero" id="inicio">
        <div className="hero-copy">
          <span className="eyebrow">PLATAFORMA COMERCIAL <span>·</span> CLIENTE WEB</span>
          <h1>Todo el inventario,<br />a primera vista.</h1>
          <p>Consulta vehículos y ventas desde una interfaz clara conectada a los servicios de Vía Motor.</p>
        </div>
        <div className="hero-badge"><span className="badge-icon">⌁</span><span>Conexión segura<br /><b>Autenticación JWT</b></span></div>
      </section>

      <div className="workspace-grid">
        <div className="main-column">
          <section className="card" aria-labelledby="titulo-acceso">
            <div className="card-heading">
              <div className="heading-group"><span className="heading-icon">↗</span><div><h2 id="titulo-acceso">Conecta con la API</h2><p className="card-subtitle">Usa el token de operador o consulta que obtuviste desde Postman.</p></div></div>
            </div>
            <form onSubmit={consultarVehiculos}>
              <label className="form-label" htmlFor="jwt">Token JWT <span className="muted-label">(sin escribir Bearer)</span></label>
              <div className="token-row">
                <input id="jwt" type={mostrarToken ? 'text' : 'password'} autoComplete="off" spellCheck="false" placeholder="Pega aquí tu token de acceso" value={token} onChange={(e) => setToken(e.target.value)} />
                <button className="button button-outline button-small" type="button" onClick={() => setMostrarToken((actual) => !actual)} aria-label={mostrarToken ? 'Ocultar token' : 'Mostrar token'}>{mostrarToken ? 'Ocultar' : 'Mostrar'}</button>
              </div>
              <div className="actions">
                <button className="button button-primary" type="submit" disabled={cargando || !token.trim()}>{cargando ? 'Consultando…' : 'Consultar información'} <span aria-hidden="true">→</span></button>
                <button className="button button-soft" type="button" disabled={cargando} onClick={limpiarToken}>Limpiar sesión</button>
              </div>
            </form>
            <div className={`request-status${error ? ' error' : ''}`} role="status" aria-live="polite"><span>{error || mensaje}</span>{codigoHttp !== null && <strong>HTTP {codigoHttp}</strong>}</div>
            <p className="privacy-note"><span>◆</span> El token solo vive en esta pestaña y no se guarda en archivos.</p>
          </section>

          <section className="card" aria-labelledby="titulo-listado">
            <div className="card-heading catalog-toolbar">
              <div className="heading-group"><span className="heading-icon">▤</span><div><h2 id="titulo-listado">Catálogo de vehículos</h2><p className="card-subtitle">Inventario recibido desde la API. Filtra por marca o selecciona un ID para ver el detalle.</p></div></div>
              <span className="count-pill">{visibles.length} {visibles.length === 1 ? 'unidad' : 'unidades'}</span>
            </div>
            <div className="filter-wrap"><label className="filter-label" htmlFor="filtroMarca">Filtrar por marca</label><input className="filter-input" id="filtroMarca" type="search" placeholder="Ejemplo: Toyota" value={marca} onChange={(e) => setMarca(e.target.value)} disabled={cargando} /></div>
            <div className="table-wrap"><table><thead><tr><th scope="col">ID</th><th scope="col">Marca</th><th scope="col">Modelo</th><th scope="col">Precio</th><th scope="col">Estado</th></tr></thead>
              <tbody>{visibles.map((v, indice) => <tr key={v.idVehiculo ?? v.id ?? indice}>
                <td><button className="id-button" type="button" onClick={() => setSeleccionado(v)} aria-label={`Ver detalle del vehículo ${v.idVehiculo ?? v.id ?? ''}`}>#{v.idVehiculo ?? v.id ?? '—'}</button></td>
                <td>{v.marca ?? '—'}</td><td>{v.modelo ?? '—'}</td><td>{mostrarPrecio(v.precio)}</td><td>{estadoVehiculo(v.estado)}</td>
              </tr>)}
              {visibles.length === 0 && <tr><td className="empty-cell" colSpan="5">{cargando ? 'Cargando vehículos…' : vehiculos.length === 0 ? 'Conecta tu sesión para consultar el inventario.' : 'No hay vehículos que coincidan con esa marca.'}</td></tr>}</tbody>
            </table></div>
          </section>

          <section className="card section-space" aria-labelledby="titulo-ventas">
            <div className="card-heading"><div className="heading-group"><span className="heading-icon">↗</span><div><h2 id="titulo-ventas">Ventas registradas</h2><p className="card-subtitle">Historial de operaciones visibles para esta cuenta.</p></div></div><span className="count-pill">{ventas.length} {ventas.length === 1 ? 'venta' : 'ventas'}</span></div>
            <div className="table-wrap"><table><thead><tr><th scope="col">Venta</th><th scope="col">Vehículo</th><th scope="col">Comprador</th><th scope="col">Estado</th><th scope="col">Notificación</th></tr></thead>
              <tbody>{ventas.map((v) => <tr key={v.id}><td>#{v.id}</td><td>Unidad #{v.vehiculoId}</td><td>Comprador #{v.compradorId}</td><td>{estadoVehiculo(v.estado)}</td><td>{v.notificacion ?? '—'}</td></tr>)}
              {!ventas.length && <tr><td className="empty-cell" colSpan="5">{cargando ? 'Consultando ventas…' : 'No hay ventas visibles. Conecta tu sesión para consultar el historial.'}</td></tr>}</tbody>
            </table></div>
            <p className="footnote">Esta interfaz es de consulta y no envía solicitudes para crear o modificar ventas.</p>
          </section>
        </div>

        <aside className="side-column">
          <section className="metric-card" aria-label="Unidades consultadas"><span className="metric-label">INVENTARIO VISIBLE</span><strong className="metric-value">{visibles.length.toString().padStart(2, '0')}</strong><span className="metric-foot">unidades en el filtro actual</span></section>
          <section className="card side-card"><h2 className="side-heading">Cómo empezar</h2><ol className="steps">
            <li><span className="step-number">01</span><span><b>Obtén un JWT</b>Inicia sesión desde Postman con el entorno local.</span></li>
            <li><span className="step-number">02</span><span><b>Pega el token</b>No incluyas el prefijo Bearer.</span></li>
            <li><span className="step-number">03</span><span><b>Consulta y explora</b>Filtra el catálogo y selecciona una unidad.</span></li>
          </ol><div className="api-route"><span className="method">GET</span><code>/api/vehiculos</code></div><p className="footnote">El cliente se conecta a través del gateway NGINX local en 127.0.0.1:8090.</p></section>
          <section className="card side-card"><div className="card-heading"><div className="heading-group"><span className="heading-icon">⌕</span><div><h2>Detalle del vehículo</h2><p className="card-subtitle">Selecciona una unidad del catálogo.</p></div></div></div>
            {seleccionado ? <dl className="detail-grid"><div><dt>ID</dt><dd>{seleccionado.idVehiculo ?? seleccionado.id ?? '—'}</dd></div><div><dt>Estado</dt><dd>{seleccionado.estado ?? '—'}</dd></div><div><dt>Marca</dt><dd>{seleccionado.marca ?? '—'}</dd></div><div><dt>Modelo</dt><dd>{seleccionado.modelo ?? '—'}</dd></div><div><dt>Precio</dt><dd>{mostrarPrecio(seleccionado.precio)}</dd></div><div><dt>Placa</dt><dd>{seleccionado.placa ?? '—'}</dd></div></dl> : <div className="detail-empty">El detalle aparecerá aquí<br />cuando elijas un vehículo.</div>}
          </section>
        </aside>
      </div>

      <footer className="footer"><span>Vía Motor · Práctica APE 04</span><span>Cliente web de consulta · React + Fetch</span></footer>
    </main>
  );
}
