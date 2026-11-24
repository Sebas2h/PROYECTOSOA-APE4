package ec.edu.uta.notificaciones.model;

import jakarta.persistence.*;
import java.time.Instant;

@Entity
@Table(name = "notificaciones", uniqueConstraints = @UniqueConstraint(name = "uq_notificacion_evento", columnNames = "eventoId"))
public class Notificacion {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    @Column(nullable = false, length = 36)
    private String eventoId;
    private Integer ventaId;
    @Column(nullable = false)
    private Integer vehiculoId;
    @Column(nullable = false, length = 200)
    private String destinatario;
    @Column(nullable = false, length = 30)
    private String tipo;
    @Column(nullable = false, length = 500)
    private String mensaje;
    @Column(nullable = false)
    private Instant recibidaEn = Instant.now();

    public Long getId() { return id; }
    public String getEventoId() { return eventoId; }
    public void setEventoId(String eventoId) { this.eventoId = eventoId; }
    public Integer getVentaId() { return ventaId; }
    public void setVentaId(Integer ventaId) { this.ventaId = ventaId; }
    public Integer getVehiculoId() { return vehiculoId; }
    public void setVehiculoId(Integer vehiculoId) { this.vehiculoId = vehiculoId; }
    public String getDestinatario() { return destinatario; }
    public void setDestinatario(String destinatario) { this.destinatario = destinatario; }
    public String getTipo() { return tipo; }
    public void setTipo(String tipo) { this.tipo = tipo; }
    public String getMensaje() { return mensaje; }
    public void setMensaje(String mensaje) { this.mensaje = mensaje; }
    public Instant getRecibidaEn() { return recibidaEn; }
}

