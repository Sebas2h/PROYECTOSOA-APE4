package ec.edu.uta.venta_vehiculos_api.client;

import java.time.Duration;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.web.client.*;
import ec.edu.uta.venta_vehiculos_api.dto.NotificacionRequest;

// Configura el comportamiento de Spring o el mapeo ORM.
@Component
public class NotificacionClient {
 private final RestClient client;
 private final String destino;
 // Declara un método o constructor público.
 public NotificacionClient(
  @Value("${servicios.notificaciones.url}") String url,
  @Value("${servicios.notificaciones.key}") String key,
  @Value("${servicios.notificaciones.destinatario}") String destino) {
  var f=new SimpleClientHttpRequestFactory();
  f.setConnectTimeout(Duration.ofSeconds(2));
  f.setReadTimeout(Duration.ofSeconds(3));
  // Prepara el cliente HTTP con URL, clave y tiempos de espera.
  client=RestClient.builder().baseUrl(url).requestFactory(f)
   // Valida que se envíe una cabecera requerida.
   .defaultHeader("X-Notification-Key",key).build();
  this.destino=destino;
 }
 // Declara un método o constructor público.
 public void enviar(Integer id,String tipo,String mensaje) {
  // Controla errores sin detener toda la aplicación.
  try {
   client.post().uri("/api/notificaciones")
    .body(new NotificacionRequest(id,destino,tipo,mensaje))
    .retrieve().toBodilessEntity();
  } catch (RestClientException e) {
   System.err.println("Notificación no enviada para vehículo "+id);
  }
}
}
