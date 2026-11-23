// Paquete donde se encuentran los DTO de la aplicación.
package ec.edu.uta.venta_vehiculos_api.dto;

// Permite manejar el precio con precisión decimal.
import java.math.BigDecimal;

// Importa la entidad Vehiculo que representa la tabla de MySQL.
import ec.edu.uta.venta_vehiculos_api.model.Vehiculo;

// Define el DTO que se devolverá como respuesta JSON.
// record genera automáticamente el constructor y métodos de acceso.
public record VehiculoResponse(

    // Identificador único del vehículo.
    Integer idVehiculo,

    // Marca y modelo del vehículo.
    String marca, String modelo,

    // Placa, chasis y año del vehículo.
    String placa, String chasis, Integer anio,

    // Color, precio y estado actual del vehículo.
    String color, BigDecimal precio, String estado

) {

    // Método estático que convierte una entidad Vehiculo en un DTO.
    public static VehiculoResponse de(Vehiculo v) {

        // Crea un nuevo DTO con los datos obtenidos de la entidad.
        return new VehiculoResponse(

            v.getIdVehiculo(), // Obtiene el ID del vehículo.
            v.getMarca(),      // Obtiene la marca.
            v.getModelo(),     // Obtiene el modelo.
            v.getPlaca(),      // Obtiene la placa.
            v.getChasis(),     // Obtiene el chasis.
            v.getAnio(),       // Obtiene el año.
            v.getColor(),      // Obtiene el color.
            v.getPrecio(),     // Obtiene el precio.
            v.getEstado()      // Obtiene el estado actual.
        );
    } // Finaliza el método de conversión.

} // Finaliza el DTO VehiculoResponse.
