"""DTO de entrada validados por Pydantic."""
# Valida estructuras de entrada y tipos JSON.
from pydantic import BaseModel, ConfigDict, Field


# Esquema Pydantic para validar los campos recibidos al registrar un comprador.
class CrearComprador(BaseModel):
    # Rechaza campos imprevistos y, para comprador, elimina espacios externos.
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    # Exige documento de entre 3 y 30 caracteres.
    documento: str = Field(min_length=3, max_length=30)
    # Exige nombre de entre 2 y 120 caracteres.
    nombre: str = Field(min_length=2, max_length=120)
    # Exige correo con longitud razonable y formato básico.
    correo: str = Field(min_length=5, max_length=200,
                        # Expresión regular sencilla para comprobar el formato del correo.
                        pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


# Esquema de creación: solo acepta los ID de vehículo y comprador.
class CrearVenta(BaseModel):
    # Rechaza campos imprevistos y, para comprador, elimina espacios externos.
    model_config = ConfigDict(extra="forbid")
    # Requiere número entero positivo, sin conversiones ambiguas.
    vehiculoId: int = Field(gt=0, strict=True)
    # Requiere ID de comprador entero y positivo.
    compradorId: int = Field(gt=0, strict=True)
