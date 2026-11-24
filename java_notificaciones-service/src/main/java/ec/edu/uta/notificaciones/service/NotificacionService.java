package ec.edu.uta.notificaciones.service;

import ec.edu.uta.notificaciones.dto.NotificacionRequest;
import ec.edu.uta.notificaciones.dto.NotificacionResponse;
import ec.edu.uta.notificaciones.model.Notificacion;
import ec.edu.uta.notificaciones.repository.NotificacionRepository;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Set;
import java.util.UUID;

@Service
public class NotificacionService {

    private final NotificacionRepository repository;

    public NotificacionService(NotificacionRepository repository) {
        this.repository = repository;
    }

    private static final Set<String> TIPOS_PERMITIDOS =
            Set.of("REGISTRO", "ACTUALIZACION", "ELIMINACION", "VENTA");

    public NotificacionResponse procesar(NotificacionRequest request) {

        if (request.getVehiculoId() == null || request.getVehiculoId() <= 0) {
            throw new IllegalArgumentException("vehiculoId debe estar presente y ser válido");
        }

        if (request.getDestinatario() == null ||
                request.getDestinatario().trim().isEmpty()) {
            throw new IllegalArgumentException("El destinatario no puede estar vacío");
        }

        if (request.getMensaje() == null ||
                request.getMensaje().trim().isEmpty()) {
            throw new IllegalArgumentException("El mensaje no puede estar vacío");
        }

        if (request.getTipo() == null ||
                !TIPOS_PERMITIDOS.contains(request.getTipo().toUpperCase())) {
            throw new IllegalArgumentException("Tipo de notificación no válido");
        }


        String eventoId = request.getEventoId();
        if (eventoId == null || eventoId.isBlank()) eventoId = UUID.randomUUID().toString();
        if (repository.existsByEventoId(eventoId)) {
            return new NotificacionResponse(true, eventoId, "DUPLICADA", "Evento ya procesado");
        }
        Notificacion n = new Notificacion();
        n.setEventoId(eventoId);
        n.setVentaId(request.getVentaId());
        n.setVehiculoId(request.getVehiculoId());
        n.setDestinatario(request.getDestinatario().trim());
        n.setTipo(request.getTipo().toUpperCase());
        n.setMensaje(request.getMensaje().trim());
        repository.save(n);
        return new NotificacionResponse(
                true,
                eventoId,
                "ENVIADA",
                "Notificación procesada correctamente"
        );
    }

    public List<Notificacion> listar() {
        return repository.findAllByOrderByRecibidaEnDesc();
    }
}
