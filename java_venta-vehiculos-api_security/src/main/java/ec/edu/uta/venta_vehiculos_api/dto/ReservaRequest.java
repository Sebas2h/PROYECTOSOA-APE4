package ec.edu.uta.venta_vehiculos_api.dto;

import jakarta.validation.constraints.*;
// Declara un método o constructor público.
public record ReservaRequest(
 @NotBlank @Pattern(regexp="[A-Za-z0-9-]{1,64}")
 String operacionId
) {}
