const fs = require('fs');
const path = require('path');

const out = __dirname;
const base = '{{baseUrl}}';
const auth = [{ key: 'Authorization', value: 'Bearer {{accessToken}}', type: 'text' }];
const jsonHeader = [{ key: 'Content-Type', value: 'application/json', type: 'text' }];

function test(code, expected, extra = '') {
  return [{ listen: 'test', script: { type: 'text/javascript', exec: [
    `pm.test("${code} HTTP esperado", () => pm.expect(pm.response.code).to.be.oneOf([${expected.join(',')}]))`,
    extra
  ].filter(Boolean) } }];
}

function req(id, name, method, url, options = {}) {
  const headers = [...(options.auth === false ? [] : auth), ...(options.headers || [])];
  const request = { method, header: headers, url: { raw: `${base}${url}`, host: [base], path: url.replace(/^\//, '').split('/') } };
  if (options.raw) request.body = { mode: 'raw', raw: options.raw, options: { raw: { language: 'json' } } };
  else if (options.body) request.body = { mode: 'raw', raw: JSON.stringify(options.body, null, 2), options: { raw: { language: 'json' } } };
  if (options.form) request.body = { mode: 'urlencoded', urlencoded: Object.entries(options.form).map(([key,value]) => ({key,value,type:'text'})) };
  return { name: `${id} ${name}`, request, event: test(id, options.expected || [200], options.script || '') };
}

function manual(id, name, verifyUrl = '/nginx-ping') {
  return req(id, `${name} [requiere acción GUI/infra]`, 'GET', verifyUrl, {
    auth: false,
    expected: [200],
    script: `pm.test("${id} evidencia manual confirmada", () => pm.expect(pm.environment.get("manual_${id}")).to.eql("OK"))`
  });
}

const login = (id, role, userVar, passVar, tokenVar) => req(id, `login ${role}`, 'POST', '/oauth/token', {
  auth: false,
  headers: [{ key: 'Authorization', value: 'Basic {{oauthBasic}}', type: 'text' }, { key: 'Content-Type', value: 'application/x-www-form-urlencoded', type: 'text' }],
  form: { grant_type: 'password', username: `{{${userVar}}}`, password: `{{${passVar}}}` },
  expected: [200],
  script: `const j=pm.response.json(); pm.environment.set("${tokenVar}",j.access_token); ${tokenVar === 'operatorToken' ? 'pm.environment.set("accessToken",j.access_token);' : ''} pm.test("JWT presente",()=>pm.expect(j.access_token).to.be.a("string"))`
});

const vehicle = { marca: 'APE04', modelo: 'QA {{qaSuffix}}', placa: '{{qaPlate}}', chasis: '{{qaChassis}}', anio: 2026, color: 'Azul', precio: 19990.50 };
const buyer = { documento: '{{qaDocument}}', nombre: 'Comprador APE04', correo: '{{qaEmail}}' };
const sale = { vehiculoId: 999999, compradorId: 999999 };

const folders = [
  { name: 'Diagnóstico', item: [
    manual('E29','versión JDK y Maven'), manual('E30','Python entorno y dependencias'), manual('E31','dotnet build'),
    manual('E32','compilación React'), manual('E33','construcción PWA'), manual('E34','MySQL y separación de esquemas'),
    req('E35','health simultáneo vía NGINX','GET','/nginx-ping',{auth:false,expected:[200]})
  ]},
  { name: 'Vehículos y JWT', item: [
    login('E36','OPERADOR','operadorUser','operadorPassword','operatorToken'), login('E37','CONSULTA','consultaUser','consultaPassword','consultaToken'),
    req('E38','crear vehículo autorizado','POST','/api/vehiculos',{headers:jsonHeader,body:vehicle,expected:[201],script:'const j=pm.response.json(); pm.environment.set("vehiculoId",j.idVehiculo)'}),
    req('E39','vehículo con campos inválidos','POST','/api/vehiculos',{headers:jsonHeader,body:{marca:'',modelo:'',placa:'',chasis:'corto',anio:null,precio:-1},expected:[422]}),
    req('E40','vehículo duplicado','POST','/api/vehiculos',{headers:jsonHeader,body:vehicle,expected:[400,409]}),
    req('E41','consulta sin JWT','GET','/api/vehiculos',{auth:false,expected:[401]}),
    req('E42','JWT con firma alterada','GET','/api/vehiculos',{auth:false,headers:[{key:'Authorization',value:'Bearer {{alteredToken}}',type:'text'}],expected:[401]}),
    req('E43','JWT expirado','GET','/api/vehiculos',{auth:false,headers:[{key:'Authorization',value:'Bearer {{expiredToken}}',type:'text'}],expected:[401]}),
    req('E44','vehículo inexistente','GET','/api/vehiculos/999999999',{expected:[404]}),
    req('E45','crear vehículo con CONSULTA','POST','/api/vehiculos',{auth:false,headers:[{key:'Authorization',value:'Bearer {{consultaToken}}',type:'text'},...jsonHeader],body:vehicle,expected:[403]})
  ]},
  { name: 'Casos obligatorios P02-P28', item: [
    manual('P02','WinForms crea vehículo','/api/vehiculos'), manual('P03','WinForms lista vehículos','/api/vehiculos'),
    manual('P04','WinForms crea comprador','/api/compradores'), manual('P05','WinForms lista compradores','/api/compradores'),
    manual('P06','WinForms lista ventas','/api/ventas'), manual('P07','PWA login válido y JWT'),
    req('P08','login inválido','POST','/oauth/token',{auth:false,headers:[{key:'Authorization',value:'Basic {{oauthBasic}}',type:'text'},{key:'Content-Type',value:'application/x-www-form-urlencoded',type:'text'}],form:{grant_type:'password',username:'invalido',password:'invalida'},expected:[401]}),
    manual('P09','PWA registra venta','/api/ventas'),
    req('P10','misma clave y cuerpo no duplica','POST','/api/ventas',{headers:[...jsonHeader,{key:'Idempotency-Key',value:'{{idempotencyKey}}',type:'text'}],raw:'{"vehiculoId": {{vehiculoId}}, "compradorId": {{compradorId}}}',expected:[200,201],script:'const primero=pm.response.json(); pm.sendRequest({url:pm.environment.get("baseUrl")+"/api/ventas",method:"POST",header:{"Authorization":"Bearer "+pm.environment.get("accessToken"),"Content-Type":"application/json","Idempotency-Key":pm.environment.get("idempotencyKey")},body:{mode:"raw",raw:JSON.stringify({vehiculoId:Number(pm.environment.get("vehiculoId")),compradorId:Number(pm.environment.get("compradorId"))})}},(e,r)=>{pm.test("P10 reintento devuelve 200 y mismo ID",()=>{pm.expect(e).to.equal(null);pm.expect(r.code).to.equal(200);pm.expect(r.json().id).to.equal(primero.id)});pm.environment.set("ventaId",primero.id)})'}),
    req('P11','misma clave cuerpo diferente','POST','/api/ventas',{headers:[...jsonHeader,{key:'Idempotency-Key',value:'{{idempotencyKey}}',type:'text'}],raw:'{"vehiculoId": {{vehiculoIdAlt}}, "compradorId": {{compradorId}}}',expected:[409]}),
    req('P12','venta inválida o no disponible','POST','/api/ventas',{headers:[...jsonHeader,{key:'Idempotency-Key',value:'ape04-invalid-{{$timestamp}}',type:'text'}],body:sale,expected:[404,409,422]}),
    req('P13','permiso insuficiente','POST','/api/ventas',{auth:false,headers:[{key:'Authorization',value:'Bearer {{consultaToken}}',type:'text'},...jsonHeader,{key:'Idempotency-Key',value:'ape04-role-{{$timestamp}}',type:'text'}],body:sale,expected:[403]}),
    manual('P14','React consulta catálogo','/api/vehiculos'), manual('P15','React filtro y detalle','/api/vehiculos?marca=APE04'),
    manual('P16','React consulta ventas','/api/ventas'), manual('P17','evento RabbitMQ persistente','/api/notificaciones'),
    manual('P18','venta rechazada no emite evento','/api/notificaciones'), manual('P19','consumidor detenido mensaje Ready'),
    manual('P20','consumidor reiniciado procesa pendiente','/api/notificaciones'), manual('P21','JavaFX muestra notificación','/api/notificaciones'),
    manual('P22','reentrega no duplica aviso','/api/notificaciones'), manual('P23','balanceo 3 a 1 con 100 GET','/api/vehiculos'),
    manual('P24','caída de instancia Java','/api/vehiculos'), manual('P25','recuperación y JWT stateless','/api/vehiculos'),
    manual('P26','monitor y rutas','/nginx-ping'), manual('P27','cadena comercial completa','/api/ventas'),
    manual('P28','auditoría sin secretos ni resultados ficticios')
  ]},
  { name: 'FastAPI', item: [
    req('E46','crear comprador válido','POST','/api/compradores',{headers:jsonHeader,body:buyer,expected:[201],script:'const j=pm.response.json(); pm.environment.set("compradorId",j.id)'}),
    req('E47','comprador incompleto','POST','/api/compradores',{headers:jsonHeader,body:{nombre:'A'},expected:[422]}),
    req('E48','comprador duplicado','POST','/api/compradores',{headers:jsonHeader,body:buyer,expected:[409,500]}),
    req('E49','listar compradores','GET','/api/compradores',{expected:[200]}), req('E50','listar ventas','GET','/api/ventas',{expected:[200]}),
    req('E51','venta comprador inexistente','POST','/api/ventas',{headers:[...jsonHeader,{key:'Idempotency-Key',value:'ape04-buyer-{{$timestamp}}',type:'text'}],body:sale,expected:[404,409]}),
    req('E52','venta vehículo inexistente','POST','/api/ventas',{headers:[...jsonHeader,{key:'Idempotency-Key',value:'ape04-car-{{$timestamp}}',type:'text'}],body:sale,expected:[404,409]}),
    req('E53','venta sin Idempotency-Key','POST','/api/ventas',{headers:jsonHeader,body:sale,expected:[422]}),
    manual('E54','reconciliación después de conexión incierta','/api/ventas')
  ]},
  { name: 'Clientes y resiliencia', item: [
    manual('E55','WinForms maneja 401 y 403'), manual('E56','WinForms backend no disponible'), manual('E57','WinForms valida entradas'),
    manual('E58','PWA cierre de sesión'), manual('E59','PWA doble submit idempotente'), manual('E60','PWA fallo incierto'),
    manual('E61','React maneja 401 y 403'), manual('E62','React vacío y fallo de conectividad'),
    req('E63','payload evento sin secretos','GET','/api/notificaciones',{expected:[200]}), manual('E64','caída y recuperación RabbitMQ'),
    req('E65','notificaciones autorizadas','GET','/api/notificaciones',{expected:[200,401,403]}), manual('E66','JavaFX recupera sondeo','/api/notificaciones')
  ]},
  { name: 'NGINX e integración', item: [
    manual('E67','nginx -t'), req('E68','nginx-ping con backend caído','GET','/nginx-ping',{auth:false,expected:[200]}),
    manual('E69','coherencia directa Java A y B','/api/vehiculos'), manual('E70','recuperación de balanceo','/api/vehiculos'),
    manual('E71','vehículo vendido e IDs consistentes','/api/ventas'), manual('E72','WinForms y React no crean ventas','/api/ventas'),
    manual('E73','segunda venta independiente','/api/ventas')
  ]}
];

const collection = {
  info: { name: 'APE04 - 72 pruebas restantes', schema: 'https://schema.getpostman.com/json/collection/v2.1.0/collection.json', description: 'P02-P28 y E29-E73. Los casos GUI/infra fallan deliberadamente hasta que su variable manual_ID sea OK.' },
  item: folders,
  variable: [{key:'baseUrl',value:'http://127.0.0.1:8090'}]
};

const envValues = [
  ['baseUrl','http://127.0.0.1:8090'], ['oauthBasic',''], ['operadorUser',''], ['operadorPassword',''],
  ['consultaUser',''], ['consultaPassword',''], ['accessToken',''], ['operatorToken',''], ['consultaToken',''], ['alteredToken','token.alterado.firma'],
  ['expiredToken',''], ['vehiculoId',''], ['vehiculoIdAlt',''], ['compradorId',''], ['ventaId',''], ['idempotencyKey','ape04-idempotencia-001'],
  ['qaSuffix',''], ['qaPlate',''], ['qaChassis',''], ['qaDocument',''], ['qaEmail','']
].map(([key,value])=>({key,value,type:'default',enabled:true}));
for (const folder of folders) for (const item of folder.item) {
  const id = item.name.slice(0,3).trim();
  if (item.name.includes('[requiere acción GUI/infra]')) envValues.push({key:`manual_${id}`,value:'PENDIENTE',type:'default',enabled:true});
}
const environment = { id:'ape04-local-sanitizado', name:'APE04 Local Sanitizado', values:envValues, _postman_variable_scope:'environment', _postman_exported_using:'Codex' };

fs.mkdirSync(out,{recursive:true});
fs.writeFileSync(path.join(out,'APE04_72_PRUEBAS.postman_collection.json'),JSON.stringify(collection,null,2));
fs.writeFileSync(path.join(out,'APE04_LOCAL_SANITIZADO.postman_environment.json'),JSON.stringify(environment,null,2));
console.log(`Generados ${folders.reduce((n,f)=>n+f.item.length,0)} casos`);
