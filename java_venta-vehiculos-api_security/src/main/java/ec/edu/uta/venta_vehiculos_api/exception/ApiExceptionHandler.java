// Paquete donde se manejan los errores de la API.
package ec.edu.uta.venta_vehiculos_api.exception;

// Permite construir identificadores URI para los errores.
import java.net.URI;

// Permite generar un identificador único para cada error.
import java.util.UUID;

// Permite registrar los errores en la consola.
import org.slf4j.LoggerFactory;

// Detecta errores de integridad en MySQL, como duplicados.
import org.springframework.dao.DataIntegrityViolationException;

// Importa clases para manejar respuestas y códigos HTTP.
import org.springframework.http.*;

// Detecta errores al recibir un JSON incorrecto.
import org.springframework.http.converter.HttpMessageNotReadableException;

// Detecta errores de validación de los DTO.
import org.springframework.web.bind.MethodArgumentNotValidException;

// Importa anotaciones para manejar excepciones.
import org.springframework.web.bind.annotation.*;

// Permite consultar información de errores HTTP de Spring.
import org.springframework.web.ErrorResponse;

// Permite obtener información de la petición HTTP.
import jakarta.servlet.http.HttpServletRequest;

// Indica que esta clase maneja errores de todos los Controllers.
@RestControllerAdvice
public class ApiExceptionHandler {

    // Captura las excepciones que ocurren en la API.
    @ExceptionHandler(Exception.class)

    // Método que recibe el error y la petición HTTP.
    public ResponseEntity<ProblemDetail> manejar(
            Exception ex, HttpServletRequest req) {

        // Código predeterminado: error interno del servidor.
        int status = 500;

        // Identificador predeterminado del error.
        String codigo = "ERROR_INTERNO";

        // Mensaje predeterminado para el cliente.
        String detalle = "No fue posible completar la solicitud";

        // Comprueba si es un error personalizado de la aplicación.
        if (ex instanceof ApiError e) {

            // Recupera el código HTTP, identificador y mensaje.
            status = e.status;
            codigo = e.codigo;
            detalle = e.getMessage();

        // Comprueba si fallaron las validaciones del DTO.
        } else if (ex instanceof MethodArgumentNotValidException e) {

            // Devuelve 422 cuando los datos no cumplen las validaciones.
            status = 422;
            codigo = "VALIDACION";

            // Obtiene todos los campos que presentan errores.
            detalle = e.getBindingResult().getFieldErrors().stream()

                // Une el nombre del campo con su mensaje de error.
                .map(x -> x.getField() + ": " + x.getDefaultMessage())

                // Combina los mensajes de error en un solo texto.
                .reduce((a,b) -> a + "; " + b)

                // Mensaje utilizado si no se obtiene ningún detalle.
                .orElse("Datos inválidos");

        // Comprueba si el JSON recibido es incorrecto.
        } else if (ex instanceof HttpMessageNotReadableException) {

            // Devuelve HTTP 400 por una petición mal formada.
            status = 400;
            codigo = "JSON_INVALIDO";
            detalle = "JSON ilegible o tipo de dato incorrecto";

        // Comprueba si MySQL rechazó una operación por integridad.
        } else if (ex instanceof DataIntegrityViolationException) {

            // Devuelve 409 por conflictos, como una placa duplicada.
            status = 409;
            codigo = "CONFLICTO_DATOS";
            detalle = "Duplicado o relación que impide la operación";

        // Comprueba si un argumento recibido es incorrecto.
        } else if (ex instanceof IllegalArgumentException) {

            // Devuelve 400 con el mensaje de la excepción.
            status = 400;
            codigo = "SOLICITUD_INVALIDA";
            detalle = ex.getMessage();

        // Comprueba si Spring generó un error HTTP.
        } else if (ex instanceof ErrorResponse e) {

            // Obtiene el código HTTP original de Spring.
            status = e.getStatusCode().value();

            // Asigna un identificador general al error.
            codigo = "ERROR_HTTP";

            // Obtiene la descripción del error.
            detalle = e.getBody().getDetail();
        }

        // Genera un identificador único para localizar el error.
        String trace = UUID.randomUUID().toString();

        // Si el error es 500 o superior, lo registra en consola.
        if (status >= 500)
            LoggerFactory.getLogger(getClass())
                .error("Error " + trace, ex);

        // Construye la respuesta estándar del error.
        ProblemDetail p = ProblemDetail.forStatusAndDetail(
            HttpStatusCode.valueOf(status), detalle);

        // Asigna un identificador URI al tipo de error.
        p.setType(URI.create("urn:vehiculos:" + codigo.toLowerCase()));

        // Guarda la ruta donde ocurrió el error.
        p.setInstance(URI.create(req.getRequestURI()));

        // Agrega el código personalizado al JSON.
        p.setProperty("codigo", codigo);

        // Agrega el identificador único del error al JSON.
        p.setProperty("traceId", trace);

        // Devuelve el código HTTP y el error como JSON.
        return ResponseEntity.status(status)
            .contentType(MediaType.APPLICATION_PROBLEM_JSON)
            .body(p);

    } // Finaliza el método manejar.

} // Finaliza la clase ApiExceptionHandler.
