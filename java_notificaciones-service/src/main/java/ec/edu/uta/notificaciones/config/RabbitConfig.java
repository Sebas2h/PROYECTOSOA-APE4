package ec.edu.uta.notificaciones.config;

import org.springframework.amqp.core.*;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class RabbitConfig {
    @Bean
    DirectExchange ventasExchange(@Value("${app.rabbit.exchange}") String nombre) {
        return new DirectExchange(nombre, true, false);
    }
    @Bean
    Queue ventasQueue(@Value("${app.rabbit.queue}") String nombre) {
        return QueueBuilder.durable(nombre).build();
    }
    @Bean
    Binding ventasBinding(Queue ventasQueue, DirectExchange ventasExchange,
            @Value("${app.rabbit.routing-key}") String routingKey) {
        return BindingBuilder.bind(ventasQueue).to(ventasExchange).with(routingKey);
    }
}

