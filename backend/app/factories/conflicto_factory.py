"""
Patrón Factory Method — ConflictoFactory
=========================================
Cada tipo de Conflicto tiene su propio Creator concreto que conoce
la severidad por defecto y el valor de `tipo` correcto.
El método de fábrica `crear()` encapsula la lógica de instanciación.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from app.models.conflicto import Conflicto


# ── Creator abstracto ─────────────────────────────────────────────────────────

class ConflictoCreator(ABC):
    """Define la interfaz del método de fábrica para crear Conflictos."""

    @property
    @abstractmethod
    def tipo(self) -> str: ...

    @property
    @abstractmethod
    def severidad_defecto(self) -> str: ...

    def crear(
        self,
        asignacion_id: int,
        descripcion: str,
        db: Session,
        severidad: str | None = None,
    ) -> Conflicto:
        """Método de fábrica: instancia, persiste y retorna el Conflicto."""
        conflicto = Conflicto(
            asignacion_id=asignacion_id,
            tipo=self.tipo,
            severidad=severidad or self.severidad_defecto,
            descripcion=descripcion,
        )
        db.add(conflicto)
        db.commit()
        db.refresh(conflicto)
        return conflicto


# ── Creators concretos ────────────────────────────────────────────────────────

class SolapamientoTurnoFactory(ConflictoCreator):
    tipo             = "solapamiento_turno"
    severidad_defecto = "alta"


class ExcesoHorasDiaFactory(ConflictoCreator):
    tipo             = "exceso_8h_dia"
    severidad_defecto = "alta"


class ChoferNoDisponibleFactory(ConflictoCreator):
    tipo             = "chofer_no_disponible"
    severidad_defecto = "media"


class LicenciaVencidaFactory(ConflictoCreator):
    tipo             = "licencia_vencida"
    severidad_defecto = "critica"


class CertifProtVencidaFactory(ConflictoCreator):
    tipo             = "certif_prot_vencida"
    severidad_defecto = "critica"


class DescansoInsuficienteFactory(ConflictoCreator):
    tipo             = "descanso_insuficiente"
    severidad_defecto = "media"


class ConcesionarioIncorrectoFactory(ConflictoCreator):
    tipo             = "concesionario_incorrecto"
    severidad_defecto = "alta"


class BusNoOperativoFactory(ConflictoCreator):
    tipo             = "bus_no_operativo"
    severidad_defecto = "media"


class OtroConflictoFactory(ConflictoCreator):
    tipo             = "otro"
    severidad_defecto = "baja"


# ── Registro para obtener el factory por tipo ─────────────────────────────────

_REGISTRY: dict[str, ConflictoCreator] = {
    "solapamiento_turno":    SolapamientoTurnoFactory(),
    "exceso_8h_dia":         ExcesoHorasDiaFactory(),
    "chofer_no_disponible":  ChoferNoDisponibleFactory(),
    "licencia_vencida":      LicenciaVencidaFactory(),
    "certif_prot_vencida":   CertifProtVencidaFactory(),
    "descanso_insuficiente": DescansoInsuficienteFactory(),
    "concesionario_incorrecto": ConcesionarioIncorrectoFactory(),
    "bus_no_operativo":      BusNoOperativoFactory(),
    "otro":                  OtroConflictoFactory(),
}


def get_factory(tipo: str) -> ConflictoCreator:
    """Retorna el Creator concreto registrado para el tipo dado."""
    factory = _REGISTRY.get(tipo)
    if factory is None:
        raise ValueError(f"Tipo de conflicto desconocido: '{tipo}'")
    return factory
