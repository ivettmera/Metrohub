"""
Patrón Builder — ProgramacionBuilder
======================================
Permite construir instancias de Programacion de forma fluida, evitando
el problema del constructor telescópico cuando varios campos son opcionales.
"""

from __future__ import annotations
from datetime import date
from typing import Optional
from app.models.programacion import Programacion


class ProgramacionBuilder:
    """Builder fluido para crear objetos Programacion."""

    def __init__(self) -> None:
        self._nombre:           Optional[str]  = None
        self._fecha_inicio:     Optional[date] = None
        self._fecha_fin:        Optional[date] = None
        self._creado_por:       Optional[int]  = None
        self._estado:           str            = "borrador"
        self._aprobado_por:     Optional[int]  = None
        self._observaciones:    Optional[str]  = None

    # ── Setters fluidos ───────────────────────────────────────────────────────

    def nombre(self, nombre: str) -> "ProgramacionBuilder":
        self._nombre = nombre
        return self

    def fechas(self, inicio: date, fin: date) -> "ProgramacionBuilder":
        self._fecha_inicio = inicio
        self._fecha_fin    = fin
        return self

    def creado_por(self, usuario_id: int) -> "ProgramacionBuilder":
        self._creado_por = usuario_id
        return self

    def estado(self, estado: str) -> "ProgramacionBuilder":
        estados_validos = {"borrador", "revision", "aprobada", "archivada"}
        if estado not in estados_validos:
            raise ValueError(f"Estado inválido '{estado}'. Válidos: {estados_validos}")
        self._estado = estado
        return self

    def aprobado_por(self, usuario_id: int) -> "ProgramacionBuilder":
        self._aprobado_por = usuario_id
        return self

    def observaciones(self, texto: str) -> "ProgramacionBuilder":
        self._observaciones = texto
        return self

    # ── Construcción final ────────────────────────────────────────────────────

    def build(self) -> Programacion:
        """Valida los campos requeridos y retorna una instancia de Programacion."""
        faltantes = [
            campo for campo, valor in [
                ("nombre",       self._nombre),
                ("fecha_inicio", self._fecha_inicio),
                ("fecha_fin",    self._fecha_fin),
                ("creado_por",   self._creado_por),
            ]
            if valor is None
        ]
        if faltantes:
            raise ValueError(f"Campos requeridos sin asignar: {faltantes}")

        if self._fecha_fin < self._fecha_inicio:
            raise ValueError("fecha_fin debe ser posterior o igual a fecha_inicio")

        return Programacion(
            nombre           = self._nombre,
            fecha_inicio     = self._fecha_inicio,
            fecha_fin        = self._fecha_fin,
            creado_por       = self._creado_por,
            estado           = self._estado,
            aprobado_por     = self._aprobado_por,
            observaciones    = self._observaciones,
        )
