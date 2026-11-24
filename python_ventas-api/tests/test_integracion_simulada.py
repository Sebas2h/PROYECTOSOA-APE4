"""Pruebas con SQLite temporal y servicios HTTP simulados; NO reemplazan a Java/MySQL reales."""
import importlib
import os
import sys
from pathlib import Path

import pytest
import httpx
from fastapi.testclient import TestClient
from sqlalchemy import create_engine as sqlalchemy_create_engine
from sqlalchemy.pool import StaticPool


@pytest.fixture
def sistema(monkeypatch):
    # Arranca con una base SQLite aislada y conexión compartida en memoria.
    engine = sqlalchemy_create_engine('sqlite://', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    # La app sigue generando la URL de MySQL, pero para la prueba utiliza SQLite.
    import sqlalchemy
    monkeypatch.setattr(sqlalchemy, 'create_engine', lambda *args, **kwargs: engine)
    for k,v in {'DB_USER':'pruebas','DB_HOST':'127.0.0.1','DB_NAME':'venta_vehiculos',
                'JAVA_URL':'http://127.0.0.1:8080', 'VENTAS_SERVICE_KEY':'clave_prueba_java_con_32_caracteres_1234',
                'NOTIFICACIONES_URL':'http://127.0.0.1:8081','NOTIFICACIONES_KEY':'clave_prueba_notif_con_32_caracteres_123'}.items():
        monkeypatch.setenv(k,v)
    monkeypatch.setenv('NOTIFICATION_TRANSPORT', 'http')
    # Fuerza a cargar los módulos para usar el motor temporal de pruebas.
    for name in list(sys.modules):
        if name == 'app' or name.startswith('app.'):
            del sys.modules[name]
    from app.db import Base
    from app import models
    Base.metadata.create_all(engine)
    from app.main import app
    import app.services.venta_service as svc
    import app.security as sec
    import app.clients.vehiculos_client as veh
    # Servidor Java simulado con las mismas rutas y estados de reserva del contrato real.
    estado={'reservas':{},'vehiculos':{1:'DISPONIBLE',2:'DISPONIBLE'},'avisos':[], 'notificaciones_activas':True}
    def identidad(url, **kw):
        assert url.endswith('/api/identidad')
        auth = kw.get('headers',{}).get('Authorization','')
        if auth=='Bearer valido':return httpx.Response(200,json={'usuario':'operador','roles':['ROLE_OPERADOR']})
        if auth=='Bearer consulta':return httpx.Response(200,json={'usuario':'lector','roles':['ROLE_CONSULTA']})
        return httpx.Response(401,json={'error':'token inválido'})
    def java(method,url,**kw):
        assert kw['headers']['X-Service-Key']=='clave_prueba_java_con_32_caracteres_1234'
        route=url.split(':8080')[-1]
        if method=='GET' and route=='/api/reservas':
            op=kw['params']['operacionId'];r=estado['reservas'].get(op)
            return httpx.Response(200,json=r) if r else httpx.Response(404,json={'error':'no existe'})
        if method=='POST' and route.startswith('/api/vehiculos/'):
            vehiculo=int(route.split('/')[3]);op=kw['json']['operacionId']
            if vehiculo not in estado['vehiculos']:return httpx.Response(404,json={'error':'inexistente'})
            if estado['vehiculos'][vehiculo]!='DISPONIBLE':return httpx.Response(409,json={'error':'vendido'})
            estado['vehiculos'][vehiculo]='RESERVADO'
            r={'id':op,'operacionId':op,'vehiculoId':vehiculo,'precio':'18000.00','moneda':'USD','estado':'RESERVADA'}
            estado['reservas'][op]=r
            return httpx.Response(200,json=r)
        if method=='PUT' and route.endswith('/confirmacion'):
            reserva=route.split('/')[3];r=estado['reservas'][reserva]
            r['estado']='CONFIRMADA';estado['vehiculos'][r['vehiculoId']]='VENDIDO'
            return httpx.Response(200,json=r)
        raise AssertionError(f'Ruta inesperada: {method} {route}')
    def avisar(url,**kw):
        assert kw['headers']['X-Notification-Key']=='clave_prueba_notif_con_32_caracteres_123'
        assert url.endswith('/api/notificaciones')
        if not estado['notificaciones_activas']:raise httpx.ConnectError('apagado')
        estado['avisos'].append(kw['json'])
        return httpx.Response(201,json={'estado':'ENVIADA'})
    monkeypatch.setattr(httpx,'get',identidad)
    monkeypatch.setattr(httpx,'request',java)
    monkeypatch.setattr(httpx,'post',avisar)
    return TestClient(app),estado


def test_venta_con_jwt_e_idempotencia(sistema):
    client,estado=sistema
    assert client.get('/health').json()=={'status':'UP'}
    auth={'Authorization':'Bearer valido'}
    comprador=client.post('/api/compradores',json={'documento':'1801111111','nombre':'Ana','correo':'ana@ejemplo.com'},headers=auth)
    assert comprador.status_code==201, comprador.text
    cid=comprador.json()['id']
    headers={**auth,'Idempotency-Key':'laboratorio0001'}
    payload={'vehiculoId':1,'compradorId':cid}
    creado=client.post('/api/ventas',json=payload,headers=headers)
    assert creado.status_code==201, creado.text
    assert creado.json()['estado']=='COMPLETADA'
    assert creado.json()['notificacion']=='ENVIADA'
    assert estado['vehiculos'][1]=='VENDIDO'
    assert len(estado['avisos'])==1
    mismo=client.post('/api/ventas',json=payload,headers=headers)
    assert mismo.status_code==200 and mismo.json()['id']==creado.json()['id']
    assert len(estado['avisos'])==1
    incorrecto=client.post('/api/ventas',json={'vehiculoId':2,'compradorId':cid},headers=headers)
    assert incorrecto.status_code==409
    no_disponible=client.post('/api/ventas',json=payload,headers={**auth,'Idempotency-Key':'laboratorio0002'})
    assert no_disponible.status_code==409


def test_seguridad_validaciones_y_reenvio(sistema):
    client,estado=sistema
    data={'documento':'1805555555','nombre':'Ana','correo':'ana@ejemplo.com'}
    assert client.post('/api/compradores',json=data).status_code==401
    assert client.post('/api/compradores',json=data,headers={'Authorization':'Bearer consulta'}).status_code==403
    auth={'Authorization':'Bearer valido'}
    assert client.post('/api/compradores',json={'nombre':'Ana'},headers=auth).status_code==422
    cid=client.post('/api/compradores',json=data,headers=auth).json()['id']
    estado['notificaciones_activas']=False
    venta=client.post('/api/ventas',json={'vehiculoId':2,'compradorId':cid},headers={**auth,'Idempotency-Key':'laboratorio0003'})
    assert venta.status_code==201
    assert venta.json()['notificacion']=='PENDIENTE'
    estado['notificaciones_activas']=True
    from app.worker import ciclo
    ciclo()
    compr=client.get(f"/api/ventas/{venta.json()['id']}",headers=auth)
    assert compr.json()['notificacion']=='ENVIADA'
    assert len(estado['avisos'])==1
