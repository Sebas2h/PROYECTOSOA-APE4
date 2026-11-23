package ec.edu.uta.venta_vehiculos_api.controller;

import java.util.Map;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

// Configura el comportamiento de Spring o el mapeo ORM.
@RestController
public class IdentidadController {
 // Configura el comportamiento de Spring o el mapeo ORM.
 @GetMapping("/api/identidad")
 // Declara un método o constructor público.
 public Map<String,Object> identidad(Authentication a) {
  // Devuelve el resultado del método.
  return Map.of("usuario",a.getName(),"roles",
   a.getAuthorities().stream().map(x -> x.getAuthority()).toList());
 }
}
