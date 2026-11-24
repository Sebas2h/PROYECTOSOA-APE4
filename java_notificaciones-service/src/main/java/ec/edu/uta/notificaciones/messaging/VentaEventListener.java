package ec.edu.uta.notificaciones.messaging;

import ec.edu.uta.notificaciones.dto.NotificacionRequest;
import ec.edu.uta.notificaciones.service.NotificacionService;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.stereotype.Component;

@Component
public class VentaEventListener {
    private final NotificacionService service;
    public VentaEventListener(NotificacionService service) { this.service = service; }

    @RabbitListener(queues = "${app.rabbit.queue}")
    public void recibir(NotificacionRequest evento) {
        service.procesar(evento);
    }
}

