package ec.edu.uta.venta_vehiculos_api.controller;

import jakarta.validation.Valid;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import ec.edu.uta.venta_vehiculos_api.dto.*;
import ec.edu.uta.venta_vehiculos_api.service.ReservaService;

// Configura el comportamiento de Spring o el mapeo ORM.
@RestController
public class ReservaController {
 private final ReservaService service;
 // Declara un método o constructor público.
 public ReservaController(ReservaService service) {
  this.service=service;
 }
 // Configura el comportamiento de Spring o el mapeo ORM.
 @PostMapping("/api/vehiculos/{id}/reservas")
 // Declara un método o constructor público.
 public ReservaResponse reservar(@PathVariable int id,
   @Valid @RequestBody ReservaRequest d) {
  // Devuelve el resultado del método.
  return service.reservar(id,d.operacionId());
 }
 // Configura el comportamiento de Spring o el mapeo ORM.
 @GetMapping("/api/reservas/{id}")
 // Declara un método o constructor público.
 public ReservaResponse obtener(@PathVariable String id) {
  // Devuelve el resultado del método.
  return service.obtener(id);
 }
 // Configura el comportamiento de Spring o el mapeo ORM.
 @GetMapping("/api/reservas")
 // Declara un método o constructor público.
 public ReservaResponse operacion(@RequestParam String operacionId) {
  // Devuelve el resultado del método.
  return service.porOperacion(operacionId);
 }
 // Configura el comportamiento de Spring o el mapeo ORM.
 @PutMapping("/api/reservas/{id}/confirmacion")
 // Declara un método o constructor público.
 public ReservaResponse confirmar(@PathVariable String id) {
  // Devuelve el resultado del método.
  return service.confirmar(id);
 }
 // Configura el comportamiento de Spring o el mapeo ORM.
 @DeleteMapping("/api/reservas/{id}")
 // Declara un método o constructor público.
 public ResponseEntity<Void> liberar(@PathVariable String id) {
  service.liberar(id); return ResponseEntity.noContent().build();
 }
}
