package ec.edu.uta.venta_vehiculos_api.dto;

import java.math.BigDecimal;
import ec.edu.uta.venta_vehiculos_api.model.Reserva;
// Declara un método o constructor público.
public record ReservaResponse(
 String id, String operacionId, Integer vehiculoId,
 BigDecimal precio, String moneda, String estado
) {
 // Declara un método o constructor público.
 public static ReservaResponse de(Reserva r) {
  // Devuelve el resultado del método.
  return new ReservaResponse(r.id,r.operacionId,
   r.vehiculo.getIdVehiculo(),r.precio,r.moneda,r.estado);
 }
}
