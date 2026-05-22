"""
Patrón Prototype — ProgramacionPrototype
==========================================
Permite clonar una Programacion existente como plantilla para un nuevo período,
copiando los campos escalares y reseteando el estado a 'borrador'.
"""

from __future__ import annotations
import copy
from datetime import date
from typing import Optional
from app.models.programacion import Programacion


class ProgramacionPrototype:
    """
    Envuelve una Programacion y expone el método clone() para generar
    una copia lista para ser persistida con nuevas fechas.
    """

    def __init__(self, original: Programacion) -> None:
        self._original = original

    def clone(
        self,
        nueva_fecha_inicio: date,
        nueva_fecha_fin: date,
        nuevo_nombre: Optional[str] = None,
        creado_por: Optional[int] = None,
    ) -> Programacion:
        """
        Retorna una nueva instancia de Programacion (sin id, sin timestamps)
        basada en el original, con estado='borrador' y las nuevas fechas.
        """
        if nueva_fecha_fin < nueva_fecha_inicio:
            raise ValueError("nueva_fecha_fin debe ser posterior o igual a nueva_fecha_inicio")

        clonada = Programacion(
            nombre       = nuevo_nombre or f"Copia de {self._original.nombre}",
            fecha_inicio = nueva_fecha_inicio,
            fecha_fin    = nueva_fecha_fin,
            estado       = "borrador",
            creado_por   = creado_por or self._original.creado_por,
            observaciones = (
                f"Clonada desde programación id={self._original.id}. "
                + (self._original.observaciones or "")
            ).strip(),
        )
        return clonada

    @property
    def original(self) -> Programacion:
        return self._original
