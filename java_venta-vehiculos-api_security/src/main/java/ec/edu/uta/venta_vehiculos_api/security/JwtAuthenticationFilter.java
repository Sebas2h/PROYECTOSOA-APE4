package ec.edu.uta.venta_vehiculos_api.security;

import java.io.IOException;
import java.util.List;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;
import jakarta.servlet.*;
import jakarta.servlet.http.*;

// Configura el comportamiento de Spring o el mapeo ORM.
@Component
public class JwtAuthenticationFilter extends OncePerRequestFilter {
 private final JwtService jwt;
 // Declara un método o constructor público.
 public JwtAuthenticationFilter(JwtService jwt) { this.jwt=jwt; }
 @Override
 protected void doFilterInternal(HttpServletRequest req,
   HttpServletResponse res, FilterChain chain)
   throws IOException, ServletException {
  // Valida que se envíe una cabecera requerida.
  String h=req.getHeader("Authorization");
  // Guarda temporalmente la identidad autenticada en la petición.
  if (SecurityContextHolder.getContext().getAuthentication()==null &&
      h!=null && h.startsWith("Bearer ")) {
   // Controla errores sin detener toda la aplicación.
   try {
    var c=jwt.validarToken(h.substring(7));
    // Evalúa una condición o recorre elementos.
    if (!"access".equals(c.get("tipo",String.class)))
     // Genera un error de negocio que capturará el manejador.
     throw new IllegalArgumentException("Se requiere access token");
    String rol=c.get("rol",String.class);
    // Evalúa una condición o recorre elementos.
    if (!List.of("CONSULTA","OPERADOR","ADMIN").contains(rol))
     // Genera un error de negocio que capturará el manejador.
     throw new IllegalArgumentException("Rol inválido");
    // Guarda temporalmente la identidad autenticada en la petición.
    SecurityContextHolder.getContext().setAuthentication(
     new UsernamePasswordAuthenticationToken(c.getSubject(),null,
      List.of(new SimpleGrantedAuthority("ROLE_"+rol))));
   } catch (Exception ex) { SecurityContextHolder.clearContext(); }
  }
  chain.doFilter(req,res);
 }
}
