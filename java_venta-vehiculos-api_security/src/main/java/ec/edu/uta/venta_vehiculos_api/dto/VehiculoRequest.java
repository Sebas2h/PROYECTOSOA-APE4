// Paquete donde se encuentran los DTO de la aplicación.
package ec.edu.uta.venta_vehiculos_api.dto;

// Permite manejar precios con precisión decimal.
import java.math.BigDecimal;

// Importa las anotaciones para validar los datos recibidos.
import jakarta.validation.constraints.*;

// Define un DTO que recibe los datos de un vehículo.
// record crea automáticamente el constructor y métodos de acceso.
public record VehiculoRequest(

    // La marca es obligatoria y no puede estar vacía.
    @NotBlank String marca,

    // El modelo es obligatorio y no puede estar vacío.
    @NotBlank String modelo,

    // La placa es obligatoria y no puede estar vacía.
    @NotBlank String placa,

    // El chasis es obligatorio y debe tener exactamente 17 caracteres.
    @NotBlank @Size(min=17, max=17) String chasis,

    // El año es obligatorio y no puede ser null.
    @NotNull Integer anio,

    // El color es opcional porque no tiene validación de obligatoriedad.
    String color,

    // El precio es obligatorio: no puede ser null.
    // @Positive exige que sea mayor que cero.
    // @Digits permite hasta 10 dígitos enteros y 2 decimales.
    @NotNull @Positive @Digits(integer=10, fraction=2)
    BigDecimal precio

) {} // Finaliza la definición del DTO.
