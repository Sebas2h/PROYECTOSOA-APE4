package ec.edu.uta.venta_vehiculos_api.service;

import java.util.UUID;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.*;
import ec.edu.uta.venta_vehiculos_api.dto.*;
import ec.edu.uta.venta_vehiculos_api.exception.ApiError;
import ec.edu.uta.venta_vehiculos_api.model.*;
import ec.edu.uta.venta_vehiculos_api.repository.*;

// Configura el comportamiento de Spring o el mapeo ORM.
@Service
// Configura el comportamiento de Spring o el mapeo ORM.
@Transactional(isolation=Isolation.READ_COMMITTED)
public class ReservaService {
 private final VehiculoRepository vehiculos;
 private final ReservaRepository reservas;
 // Declara un método o constructor público.
 public ReservaService(VehiculoRepository v, ReservaRepository r) {
  vehiculos=v; reservas=r;
 }
 // Declara un método o constructor público.
 public ReservaResponse reservar(int id, String op) {
  // Todas las mutaciones bloquean primero el vehículo.
  Vehiculo v=vehiculos.bloquear(id).orElseThrow(() ->
   new ApiError(404,"VEHICULO_NO_ENCONTRADO","Vehículo inexistente"));
  // Evita crear otra reserva al repetir el mismo operacionId.
  var anterior=reservas.findByOperacionId(op);
  // Evalúa una condición o recorre elementos.
  if (anterior.isPresent()) {
   Reserva r=anterior.get();
   // Evalúa una condición o recorre elementos.
   if (!r.vehiculo.getIdVehiculo().equals(id))
    // Genera un error de negocio que capturará el manejador.
    throw conflicto("La operación pertenece a otro vehículo");
   // Devuelve el resultado del método.
   return ReservaResponse.de(r);
  }
  // Evalúa una condición o recorre elementos.
  if (!"DISPONIBLE".equals(v.getEstado()))
   // Genera un error de negocio que capturará el manejador.
   throw conflicto("El vehículo no está disponible");
  Reserva r=new Reserva();
  r.id=UUID.randomUUID().toString(); r.operacionId=op;
  r.vehiculo=v; r.precio=v.getPrecio();
  r.moneda="USD"; r.estado="RESERVADA";
  v.setEstado("RESERVADO");
  reservas.saveAndFlush(r);
  // Devuelve el resultado del método.
  return ReservaResponse.de(r);
 }
 // Configura el comportamiento de Spring o el mapeo ORM.
 @Transactional(readOnly=true)
 // Declara un método o constructor público.
 public ReservaResponse obtener(String id) {
  // Devuelve el resultado del método.
  return ReservaResponse.de(buscar(id));
 }
 // Configura el comportamiento de Spring o el mapeo ORM.
 @Transactional(readOnly=true)
 // Declara un método o constructor público.
 public ReservaResponse porOperacion(String op) {
  // Evita crear otra reserva al repetir el mismo operacionId.
  return ReservaResponse.de(reservas.findByOperacionId(op)
   .orElseThrow(() -> new ApiError(404,"RESERVA_NO_ENCONTRADA",
    "La operación no tiene reserva")));
 }
 // Declara un método o constructor público.
 public ReservaResponse confirmar(String id) {
  Reserva r=bloquear(id);
  // Evalúa una condición o recorre elementos.
  if ("LIBERADA".equals(r.estado))
   // Genera un error de negocio que capturará el manejador.
   throw conflicto("La reserva fue liberada");
  // Evalúa una condición o recorre elementos.
  if ("RESERVADA".equals(r.estado)) {
   // Evalúa una condición o recorre elementos.
   if (!"RESERVADO".equals(r.vehiculo.getEstado()))
    // Genera un error de negocio que capturará el manejador.
    throw conflicto("Estado del vehículo inconsistente");
   r.estado="CONFIRMADA"; r.vehiculo.setEstado("VENDIDO");
  }
  // Devuelve el resultado del método.
  return ReservaResponse.de(r);
 }
 // Declara un método o constructor público.
 public void liberar(String id) {
  Reserva r=bloquear(id);
  // Evalúa una condición o recorre elementos.
  if ("CONFIRMADA".equals(r.estado))
   // Genera un error de negocio que capturará el manejador.
   throw conflicto("No se libera una reserva confirmada");
  // Evalúa una condición o recorre elementos.
  if ("RESERVADA".equals(r.estado)) {
   r.estado="LIBERADA"; r.vehiculo.setEstado("DISPONIBLE");
  }
 }
 // Define un método interno del servicio.
 private Reserva bloquear(String id) {
  Reserva r=buscar(id);
  // Bloquea el vehículo para impedir una doble reserva concurrente.
  vehiculos.bloquear(r.vehiculo.getIdVehiculo()).orElseThrow();
  // Refrescar evita trabajar con estado leído antes del bloqueo.
  return refrescar(r);
 }
 @jakarta.persistence.PersistenceContext
 private jakarta.persistence.EntityManager em;
 // Define un método interno del servicio.
 private Reserva refrescar(Reserva r) {
  em.refresh(r); em.refresh(r.vehiculo); return r;
 }
 // Define un método interno del servicio.
 private Reserva buscar(String id) {
  // Devuelve el resultado del método.
  return reservas.findById(id).orElseThrow(() ->
   new ApiError(404,"RESERVA_NO_ENCONTRADA","Reserva inexistente"));
 }
 // Define un método interno del servicio.
 private ApiError conflicto(String detalle) {
  // Devuelve el resultado del método.
  return new ApiError(409,"CONFLICTO_RESERVA",detalle);
 }
}
