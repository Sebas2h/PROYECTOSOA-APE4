package ec.edu.uta.venta_vehiculos_api.security;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.List;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;
import jakarta.servlet.*;
import jakarta.servlet.http.*;

// Configura el comportamiento de Spring o el mapeo ORM.
@Component
public class IntegrationFilter extends OncePerRequestFilter {
 private final String key;
 // Declara un método o constructor público.
 public IntegrationFilter(@Value("${app.security.ventas-key}") String key) {
  // Evalúa una condición o recorre elementos.
  if (key.length()<32) throw new IllegalStateException("Clave de servicio corta");
  this.key=key;
 }
 @Override
 protected void doFilterInternal(HttpServletRequest req,
   HttpServletResponse res, FilterChain chain)
   throws IOException, ServletException {
  String path=req.getRequestURI();
  boolean interna=path.equals("/api/reservas") ||
   path.startsWith("/api/reservas/") ||
   path.matches("/api/vehiculos/[0-9]+/reservas");
  // Evalúa una condición o recorre elementos.
  if (interna) {
   // Valida que se envíe una cabecera requerida.
   String enviada=req.getHeader("X-Service-Key");
   // Compara la clave recibida sin comparación de cadenas convencional.
   if (enviada==null || !MessageDigest.isEqual(
    key.getBytes(StandardCharsets.UTF_8),
    enviada.getBytes(StandardCharsets.UTF_8))) {
    res.setStatus(401); res.setContentType("application/problem+json");
    res.getWriter().write("{\"title\":\"Servicio no autorizado\",\"status\":401}");
    // Devuelve el resultado del método.
    return;
   }
   // Guarda temporalmente la identidad autenticada en la petición.
   SecurityContextHolder.getContext().setAuthentication(
    new UsernamePasswordAuthenticationToken("ventas-api",null,
     List.of(new SimpleGrantedAuthority("ROLE_SERVICIO_VENTAS"))));
  }
  chain.doFilter(req,res);
 }
}
