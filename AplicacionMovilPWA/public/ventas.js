import{crearVenta,listarVentas,listarVehiculos,listarCompradores}from'./api.js';
import{montarShell,mostrarAviso,proteger401}from'./app-shell.js';

if(montarShell('Ventas','ventas')){
  const p=document.querySelector('#pageContent');
  p.innerHTML=`
    <section class="page-intro">
      <div><span class="overline">OPERACIÓN COMERCIAL</span><h2>Ventas</h2><p>Consulta las operaciones registradas o crea una nueva venta.</p></div>
      <button class="button-outline" id="refreshSales">↻ Actualizar ventas</button>
    </section>
    <section class="sale-layout">
      <form class="content-card form-card sale-form" id="saleForm">
        <div class="card-heading"><span class="module-index yellow">＋</span><div><h3>Registrar venta</h3><p>La disponibilidad se valida también en el servidor.</p></div></div>
        <label>Vehículo disponible<select id="vehicleSelect" required><option value="">Cargando unidades…</option></select></label>
        <label>Comprador<select id="buyerSelect" required><option value="">Cargando compradores…</option></select></label>
        <details><summary>Clave de idempotencia</summary><input id="idempotencyKey" placeholder="Se genera al confirmar" minlength="8" pattern="[A-Za-z0-9_-]+"><small>Usa la misma clave al reintentar una operación.</small></details>
        <button class="button-primary" id="submitSale">Confirmar venta <span>→</span></button>
        <div id="saleMessage" class="notice" role="status"></div>
      </form>
      <aside class="sale-aside"><span class="overline">PROCESO SEGURO</span><h3>Una operación controlada de principio a fin.</h3><ul><li>Solo se ofrecen vehículos disponibles.</li><li>La API verifica permisos y estado.</li><li>La clave evita duplicados por reintento.</li></ul><div class="security-note"><span>✓</span><p>El servicio valida los datos antes de confirmar la venta.</p></div></aside>
    </section>
    <section class="content-card sales-list-card">
      <div class="table-toolbar"><div><b>Ventas registradas</b><small id="salesCount">Cargando…</small></div><span class="live-label"><i></i> Datos en vivo</span></div>
      <div class="sales-table-wrap"><table class="sales-table"><thead><tr><th>Venta</th><th>Vehículo</th><th>Comprador</th><th>Estado</th><th>Precio acordado</th><th>Fecha</th></tr></thead><tbody id="salesRows"><tr><td colspan="6" class="empty-state">Consultando ventas…</td></tr></tbody></table></div>
    </section>`;

  const vehicle=document.querySelector('#vehicleSelect'),buyer=document.querySelector('#buyerSelect'),form=document.querySelector('#saleForm'),message=document.querySelector('#saleMessage'),rows=document.querySelector('#salesRows'),count=document.querySelector('#salesCount');
  const esc=v=>String(v??'—').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  async function cargarOpciones(){
    try{
      const[vs,bs]=await Promise.all([listarVehiculos(sessionStorage.getItem('ape04.jwt')),listarCompradores(sessionStorage.getItem('ape04.jwt'))]);
      vehicle.innerHTML='<option value="">Selecciona una unidad</option>';
      for(const v of vs.vehiculos.filter(x=>String(x.estado).toUpperCase()==='DISPONIBLE'))vehicle.add(new Option(`${v.marca} ${v.modelo} · #${v.idVehiculo??v.id} · $${v.precio}`,v.idVehiculo??v.id));
      buyer.innerHTML='<option value="">Selecciona un comprador</option>';
      for(const b of bs)buyer.add(new Option(`${b.nombre} · #${b.id}`,b.id));
      if(vehicle.options.length===1)vehicle.innerHTML='<option value="">No hay vehículos disponibles</option>';
      if(buyer.options.length===1)buyer.innerHTML='<option value="">Registra primero un comprador</option>';
    }catch(e){mostrarAviso(message,e.message,'error');proteger401(e);}
  }
  async function cargarVentas(){
    rows.innerHTML='<tr><td colspan="6" class="empty-state">Consultando ventas…</td></tr>';
    try{
      const token=sessionStorage.getItem('ape04.jwt');
      const[ventas,vs,bs]=await Promise.all([listarVentas(token),listarVehiculos(token),listarCompradores(token)]);
      const vehiculos=new Map(vs.vehiculos.map(v=>[String(v.idVehiculo??v.id),`${v.marca||''} ${v.modelo||''}`.trim()]));
      const compradores=new Map(bs.map(b=>[String(b.id),b.nombre]));
      count.textContent=`${ventas.length} operación${ventas.length===1?'':'es'}`;
      if(!ventas.length){rows.innerHTML='<tr><td colspan="6" class="empty-state">Aún no hay ventas registradas.</td></tr>';return;}
      rows.innerHTML=ventas.map(v=>{
        const fecha=v.fechaUTC?new Date(v.fechaUTC).toLocaleString('es-EC',{dateStyle:'medium',timeStyle:'short'}):'—';
        const estado=String(v.estado||'—').toUpperCase();
        const status=estado==='COMPLETADA'?'available':estado==='FALLIDA'?'unavailable':'pending';
        const precio=v.precioAcordado==null?'—':`${esc(v.moneda||'USD')} ${esc(v.precioAcordado)}`;
        const vehiculo=vehiculos.get(String(v.vehiculoId)),comprador=compradores.get(String(v.compradorId));
        return `<tr><td data-label="Venta">#${esc(v.id)}</td><td data-label="Vehículo">${esc(vehiculo||`Unidad #${v.vehiculoId}`)}</td><td data-label="Comprador">${esc(comprador||`Comprador #${v.compradorId}`)}</td><td data-label="Estado"><span class="status ${status}">${esc(estado)}</span></td><td data-label="Precio">${precio}</td><td data-label="Fecha">${esc(fecha)}</td></tr>`;
      }).join('');
    }catch(e){count.textContent='No disponible';rows.innerHTML=`<tr><td colspan="6" class="empty-state error">${esc(e.message)}</td></tr>`;proteger401(e);}
  }
  form.addEventListener('submit',async e=>{
    e.preventDefault();const button=document.querySelector('#submitSale');button.disabled=true;
    const input=document.querySelector('#idempotencyKey'),key=input.value||crypto.randomUUID().replaceAll('-','');input.value=key;
    try{const sale=await crearVenta(sessionStorage.getItem('ape04.jwt'),{vehiculoId:Number(vehicle.value),compradorId:Number(buyer.value)},key);input.value='';mostrarAviso(message,`Venta ${sale.id} registrada · ${sale.estado}.`,'success');await Promise.all([cargarOpciones(),cargarVentas()]);}
    catch(error){mostrarAviso(message,`Venta no completada: ${error.message}. Reintenta con la misma clave.`,'error');proteger401(error);}
    finally{button.disabled=false;}
  });
  document.querySelector('#refreshSales').addEventListener('click',cargarVentas);
  cargarOpciones();cargarVentas();
}
