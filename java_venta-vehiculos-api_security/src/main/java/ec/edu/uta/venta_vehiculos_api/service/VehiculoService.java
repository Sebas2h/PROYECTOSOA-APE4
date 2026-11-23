package ec.edu.uta.venta_vehiculos_api.service; // Paquete de servicios.

// Permite manejar precios con precisión decimal.
import java.math.BigDecimal;

// Permite obtener el año actual.
import java.time.Year;

// Importa List, Map y Locale.
import java.util.*;

// Identifica la clase como servicio de Spring Boot.
import org.springframework.stereotype.Service;

// Permite manejar transacciones con MySQL.
import org.springframework.transaction.annotation.Transactional;

// Importa los DTO de entrada y salida.
import ec.edu.uta.venta_vehiculos_api.dto.*;

// Importa la clase personalizada de errores.
import ec.edu.uta.venta_vehiculos_api.exception.ApiError;

// Importa la entidad Vehiculo.
import ec.edu.uta.venta_vehiculos_api.model.Vehiculo;

// Importa los repositorios para acceder a MySQL.
import ec.edu.uta.venta_vehiculos_api.repository.*;

// Indica que esta clase contiene lógica de negocio.
@Service

// Ejecuta sus operaciones dentro de transacciones.
// Si ocurre un error de ejecución, la transacción se revierte.
@Transactional
public class VehiculoService {

    // Repositorio para consultar y modificar vehículos.
    private final VehiculoRepository repo;

    // Repositorio para consultar las reservas.
    private final ReservaRepository reservas;

    // Constructor que recibe los repositorios mediante Spring.
    public VehiculoService(
            VehiculoRepository repo,
            ReservaRepository reservas) {

        // Guarda el repositorio de vehículos.
        this.repo = repo;

        // Guarda el repositorio de reservas.
        this.reservas = reservas;
    }

    // Indica que esta operación solamente consulta información.
    @Transactional(readOnly = true)
    public List<VehiculoResponse> listar(String marca) {

        // Si no recibe marca, consulta todos los vehículos.
        // Si recibe marca, busca los que coincidan con el texto.
        var lista = marca == null
                ? repo.findAll()
                : repo.findByMarcaContainingIgnoreCase(marca);

        // Convierte cada entidad Vehiculo en un DTO de respuesta.
        // Devuelve una lista con los resultados.
        return lista.stream()
                .map(VehiculoResponse::de)
                .toList();
    }

    // Transacción utilizada solamente para consultar.
    @Transactional(readOnly = true)
    public VehiculoResponse obtener(int id) {

        // Busca el vehículo mediante su identificador.
        // Si no existe, genera un error 404.
        // Si existe, convierte la entidad en un DTO.
        return VehiculoResponse.de(
                repo.findById(id)
                    .orElseThrow(() -> falta())
        );
    }

    // Registra un nuevo vehículo en MySQL.
    public VehiculoResponse crear(VehiculoRequest d) {

        // Crea un objeto Vehiculo vacío.
        Vehiculo v = new Vehiculo();

        // Copia y valida los datos recibidos del DTO.
        copiar(v, d);

        // Todo vehículo nuevo inicia como DISPONIBLE.
        v.setEstado("DISPONIBLE");

        // Guarda el vehículo en MySQL.
        // flush sincroniza los cambios con la base de datos.
        // Convierte el resultado en un DTO de respuesta.
        return VehiculoResponse.de(repo.saveAndFlush(v));
    }

    // Actualiza los datos de un vehículo existente.
    public VehiculoResponse actualizar(int id, VehiculoRequest d) {

        // Busca el vehículo y comprueba que pueda modificarse.
        Vehiculo v = editable(id);

        // Copia los nuevos datos al vehículo.
        copiar(v, d);

        // Guarda los cambios y devuelve el DTO actualizado.
        return VehiculoResponse.de(repo.saveAndFlush(v));
    }

    // Modifica únicamente el precio mediante PATCH.
    public VehiculoResponse precio(int id, Map<String, Object> d) {

        // Comprueba que el JSON tenga únicamente el campo precio.
        // También exige que su valor sea numérico.
        if (d.size() != 1 ||
                !d.containsKey("precio") ||
                !(d.get("precio") instanceof Number)) {

            // Genera un error 422 si los datos no son válidos.
            throw new ApiError(
                    422,
                    "PATCH_INVALIDO",
                    "PATCH admite únicamente precio numérico y no nulo"
            );
        }

        // Variable donde se almacenará el nuevo precio.
        BigDecimal precio;

        try {

            // Convierte el valor recibido a BigDecimal.
            precio = new BigDecimal(d.get("precio").toString());

        } catch (NumberFormatException e) {

            // Genera un error si el precio no puede convertirse.
            throw new ApiError(
                    422,
                    "PRECIO_INVALIDO",
                    "Precio inválido"
            );
        }

        // signum() comprueba que el precio sea positivo.
        // scale() comprueba que no tenga más de 2 decimales.
        // compareTo() comprueba el valor máximo permitido.
        if (precio.signum() <= 0 ||
                precio.scale() > 2 ||
                precio.compareTo(
                    new BigDecimal("9999999999.99")) > 0) {

            // Rechaza precios fuera del rango permitido.
            throw new ApiError(
                    422,
                    "PRECIO_INVALIDO",
                    "Precio positivo con máximo dos decimales"
            );
        }

        // Busca el vehículo y comprueba que esté disponible.
        Vehiculo v = editable(id);

        // Asigna el nuevo precio.
        v.setPrecio(precio);

        // Guarda el nuevo precio y devuelve el resultado.
        return VehiculoResponse.de(repo.saveAndFlush(v));
    }

    // Elimina un vehículo de MySQL si cumple las reglas.
    public void eliminar(int id) {

        // Busca el vehículo y verifica que esté DISPONIBLE.
        Vehiculo v = editable(id);

        // Comprueba si existen reservas asociadas al vehículo.
        if (reservas.existsByVehiculo_IdVehiculo(id)) {

            // No permite eliminar vehículos con historial de reservas.
            throw new ApiError(
                    409,
                    "HISTORIAL_RESERVAS",
                    "Se conserva el vehículo por su historial de reservas"
            );
        }

        // Solicita eliminar el vehículo de MySQL.
        repo.delete(v);

        // Sincroniza la eliminación con la base de datos.
        repo.flush();
    }

    // Método privado que verifica si un vehículo puede editarse.
    private Vehiculo editable(int id) {

        // Busca el vehículo y bloquea su registro durante
        // la transacción para controlar cambios simultáneos.
        // Si no existe, genera un error 404.
        Vehiculo v = repo.bloquear(id)
                .orElseThrow(() -> falta());

        // Comprueba que el vehículo esté DISPONIBLE.
        if (!"DISPONIBLE".equals(v.getEstado())) {

            // Impide modificar vehículos RESERVADOS o VENDIDOS.
            throw new ApiError(
                    409,
                    "VEHICULO_NO_DISPONIBLE",
                    "Un vehículo reservado o vendido no se modifica ni elimina"
            );
        }

        // Devuelve el vehículo que puede modificarse.
        return v;
    }

    // Método privado que construye un error 404.
    private ApiError falta() {

        // Devuelve un error indicando que no existe el vehículo.
        return new ApiError(
                404,
                "VEHICULO_NO_ENCONTRADO",
                "El vehículo no existe"
        );
    }

    // Copia los datos del DTO a la entidad Vehiculo.
    private void copiar(Vehiculo v, VehiculoRequest d) {

        // Comprueba que el año sea desde 1900 hasta
        // el año siguiente al actual.
        if (d.anio() < 1900 ||
                d.anio() > Year.now().getValue() + 1) {

            // Genera un error si el año está fuera de rango.
            throw new ApiError(
                    422,
                    "ANIO_INVALIDO",
                    "Año fuera de rango"
            );
        }

        // Asigna la marca eliminando espacios de los extremos.
        v.setMarca(d.marca().trim());

        // Asigna el modelo eliminando espacios de los extremos.
        v.setModelo(d.modelo().trim());

        // Convierte la placa a mayúsculas y elimina espacios.
        v.setPlaca(
                d.placa().trim().toUpperCase(Locale.ROOT)
        );

        // Convierte el chasis a mayúsculas y elimina espacios.
        v.setChasis(
                d.chasis().trim().toUpperCase(Locale.ROOT)
        );

        // Comprueba que el chasis tenga exactamente 17 caracteres.
        if (v.getChasis().length() != 17) {

            // Genera un error si el chasis no cumple la longitud.
            throw new ApiError(
                    422,
                    "CHASIS_INVALIDO",
                    "Chasis de 17 caracteres"
            );
        }

        // Asigna el año del vehículo.
        v.setAnio(d.anio());

        // Asigna el color recibido.
        v.setColor(d.color());

        // Asigna el precio recibido.
        v.setPrecio(d.precio());
    }

} // Finaliza la clase VehiculoService.
