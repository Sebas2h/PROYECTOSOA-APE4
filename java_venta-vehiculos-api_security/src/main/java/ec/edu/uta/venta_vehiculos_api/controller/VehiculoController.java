// Paquete donde se encuentran los controladores.
package ec.edu.uta.venta_vehiculos_api.controller;

// Permite construir la dirección del vehículo creado.
import java.net.URI;

// Importa List y Map para manejar listas y datos.
import java.util.*;

// Permite validar automáticamente los datos del DTO.
import jakarta.validation.Valid;

// Permite personalizar las respuestas HTTP.
import org.springframework.http.ResponseEntity;

// Importa las anotaciones REST de Spring Boot.
import org.springframework.web.bind.annotation.*;

// Importa los DTO de entrada y salida.
import ec.edu.uta.venta_vehiculos_api.dto.*;

// Importa el servicio que contiene las reglas de negocio.
import ec.edu.uta.venta_vehiculos_api.service.VehiculoService;

// Importa el cliente que comunica con notificaciones-service.
import ec.edu.uta.venta_vehiculos_api.client.NotificacionClient;

// Indica que esta clase recibe peticiones HTTP y devuelve JSON.
@RestController

// Define la ruta principal para administrar vehículos.
@RequestMapping("/api/vehiculos")
public class VehiculoController {

    // Servicio encargado de las operaciones de vehículos.
    private final VehiculoService service;

    // Cliente encargado de solicitar las notificaciones.
    private final NotificacionClient avisos;

    // Constructor que recibe las dependencias desde Spring.
    public VehiculoController(
            VehiculoService service,
            NotificacionClient avisos) {

        // Guarda el servicio de vehículos.
        this.service = service;

        // Guarda el cliente de notificaciones.
        this.avisos = avisos;
    }

    // Atiende GET /api/vehiculos.
    @GetMapping
    public List<VehiculoResponse> listar(

            // Recibe el parámetro opcional marca.
            @RequestParam(required = false) String marca) {

        // Solicita al Service listar o filtrar vehículos.
        return service.listar(marca);
    }

    // Atiende GET /api/vehiculos/{id}.
    @GetMapping("/{id}")
    public VehiculoResponse obtener(

            // Obtiene el identificador desde la URL.
            @PathVariable int id) {

        // Busca el vehículo y devuelve su DTO.
        return service.obtener(id);
    }

    // Atiende POST /api/vehiculos.
    @PostMapping
    public ResponseEntity<VehiculoResponse> crear(

            // Convierte el JSON en un DTO y valida sus campos.
            @Valid @RequestBody VehiculoRequest d) {

        // Solicita crear el vehículo en MySQL.
        var r = service.crear(d);

        // Solicita enviar una notificación de registro.
        avisos.enviar(
                r.idVehiculo(),
                "REGISTRO",
                "Vehículo registrado"
        );

        // Devuelve HTTP 201 con la ubicación del nuevo vehículo.
        return ResponseEntity.created(
                URI.create("/api/vehiculos/" + r.idVehiculo())
        ).body(r); // Incluye el DTO del vehículo creado.
    }

    // Atiende PUT /api/vehiculos/{id}.
    @PutMapping("/{id}")
    public VehiculoResponse actualizar(

            // Obtiene el ID desde la URL.
            @PathVariable int id,

            // Recibe y valida todos los datos editables del vehículo.
            @Valid @RequestBody VehiculoRequest d) {

        // Solicita al Service actualizar el vehículo.
        var r = service.actualizar(id, d);

        // Solicita una notificación de actualización.
        avisos.enviar(
                id,
                "ACTUALIZACION",
                "Vehículo actualizado"
        );

        // Devuelve el vehículo actualizado con HTTP 200.
        return r;
    }

    // Atiende PATCH /api/vehiculos/{id}.
    // Solo acepta el formato application/merge-patch+json.
    @PatchMapping(
            value = "/{id}",
            consumes = "application/merge-patch+json"
    )
    public VehiculoResponse precio(

            // Obtiene el ID del vehículo desde la URL.
            @PathVariable int id,

            // Recibe el JSON con el nuevo precio.
            @RequestBody Map<String, Object> d) {

        // Solicita modificar únicamente el precio.
        var r = service.precio(id, d);

        // Solicita una notificación por el cambio de precio.
        avisos.enviar(
                id,
                "ACTUALIZACION",
                "Precio actualizado"
        );

        // Devuelve los datos actualizados con HTTP 200.
        return r;
    }

    // Atiende DELETE /api/vehiculos/{id}.
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> eliminar(

            // Obtiene el ID del vehículo que se desea eliminar.
            @PathVariable int id) {

        // Solicita eliminar el vehículo si cumple las reglas.
        service.eliminar(id);

        // Solicita una notificación de eliminación.
        avisos.enviar(
                id,
                "ELIMINACION",
                "Vehículo eliminado"
        );

        // Devuelve HTTP 204 porque no hay cuerpo de respuesta.
        return ResponseEntity.noContent().build();
    }

} // Finaliza la clase VehiculoController.
