// Paquete donde se encuentran los repositorios de la aplicación.
package ec.edu.uta.venta_vehiculos_api.repository;

// Importa Optional y List para manejar resultados de consultas.
import java.util.*;

// Permite establecer bloqueos sobre registros de la base de datos.
import jakarta.persistence.LockModeType;

// Importa JpaRepository, @Query y @Lock de Spring Data JPA.
import org.springframework.data.jpa.repository.*;

// Permite asignar parámetros a las consultas personalizadas.
import org.springframework.data.repository.query.Param;

// Importa la entidad Vehiculo que representa la tabla vehiculos.
import ec.edu.uta.venta_vehiculos_api.model.Vehiculo;

// Define el repositorio para acceder a los vehículos en MySQL.
public interface VehiculoRepository

    // Hereda operaciones como guardar, buscar, listar y eliminar.
    // Vehiculo es la entidad e Integer es el tipo de su ID.
    extends JpaRepository<Vehiculo, Integer> {

    // Busca un vehículo mediante su placa.
    // Optional permite representar un resultado que puede no existir.
    Optional<Vehiculo> findByPlaca(String placa);

    // Busca un vehículo mediante su número de chasis.
    Optional<Vehiculo> findByChasis(String chasis);

    // Busca vehículos cuya marca contenga el texto indicado.
    // IgnoreCase permite buscar sin distinguir mayúsculas y minúsculas.
    List<Vehiculo> findByMarcaContainingIgnoreCase(String marca);

    // Bloquea el registro para impedir cambios simultáneos
    // incompatibles mientras dure la transacción.
    @Lock(LockModeType.PESSIMISTIC_WRITE)

    // Consulta la entidad Vehiculo mediante su identificador.
    // :id representa el parámetro recibido por el método.
    @Query("select v from Vehiculo v where v.idVehiculo = :id")

    // Busca y bloquea el vehículo indicado.
    // @Param relaciona el argumento id con el parámetro :id.
    Optional<Vehiculo> bloquear(@Param("id") Integer id);

} // Finaliza la interfaz VehiculoRepository.
