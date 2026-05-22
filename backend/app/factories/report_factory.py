"""
Patrón Abstract Factory — ReportFactory
==========================================
Proporciona familias de generadores de reportes según el rol del usuario.

- ATUReportFactory    → reportes globales (administrador ATU)
- ConcesionarioReportFactory → reportes filtrados por concesionario

Cada factory crea productos concretos que comparten la misma interfaz,
garantizando coherencia interna dentro de la familia.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import date, timedelta
from typing import Optional
from sqlalchemy.orm import Session

from app.models.ruta import Ruta
from app.models.chofer import Chofer
from app.models.bus import Bus
from app.models.asignacion import Asignacion
from app.models.horario_servicio import HorarioServicio
from app.models.conflicto import Conflicto


# ══════════════════════════════════════════════════════════════════════════════
# Interfaces de productos abstractos
# ══════════════════════════════════════════════════════════════════════════════

class ReporteKPIs(ABC):
    @abstractmethod
    def generar(self, db: Session) -> dict: ...


class ReporteChoferes(ABC):
    @abstractmethod
    def generar(self, db: Session) -> dict: ...


class ReporteConflictos(ABC):
    @abstractmethod
    def generar(self, db: Session) -> dict: ...


# ══════════════════════════════════════════════════════════════════════════════
# Abstract Factory
# ══════════════════════════════════════════════════════════════════════════════

class AbstractReportFactory(ABC):
    """Interfaz de la fábrica abstracta para crear familias de reportes."""

    @abstractmethod
    def crear_reporte_kpis(self) -> ReporteKPIs: ...

    @abstractmethod
    def crear_reporte_choferes(self) -> ReporteChoferes: ...

    @abstractmethod
    def crear_reporte_conflictos(self) -> ReporteConflictos: ...


# ══════════════════════════════════════════════════════════════════════════════
# Familia ATU — visión global del sistema
# ══════════════════════════════════════════════════════════════════════════════

class ATUReporteKPIs(ReporteKPIs):
    def generar(self, db: Session) -> dict:
        hoy = date.today()
        en_30_dias = hoy + timedelta(days=30)
        return {
            "tipo":              "atu",
            "fecha":             hoy,
            "rutas_activas":     db.query(Ruta).filter(Ruta.activa == True).count(),
            "choferes_activos":  db.query(Chofer).filter(Chofer.estado == "activo").count(),
            "buses_operativos":  db.query(Bus).filter(Bus.estado == "operativo").count(),
            "asignaciones_hoy":  (
                db.query(Asignacion)
                .join(HorarioServicio)
                .filter(HorarioServicio.fecha == hoy, Asignacion.estado == "confirmada")
                .count()
            ),
            "conflictos_abiertos": db.query(Conflicto).filter(Conflicto.resuelto == False).count(),
            "certif_por_vencer_30d": (
                db.query(Chofer)
                .filter(Chofer.fec_vence_certif_prot <= en_30_dias, Chofer.estado == "activo")
                .count()
            ),
        }


class ATUReporteChoferes(ReporteChoferes):
    def generar(self, db: Session) -> dict:
        choferes = db.query(Chofer).all()
        return {
            "tipo":   "atu",
            "total":  len(choferes),
            "choferes": [
                {
                    "id":     c.id,
                    "nombre": f"{c.nombres} {c.apellidos}",
                    "estado": c.estado,
                    "concesionario_id": c.concesionario_id,
                }
                for c in choferes
            ],
        }


class ATUReporteConflictos(ReporteConflictos):
    def generar(self, db: Session) -> dict:
        conflictos = db.query(Conflicto).filter(Conflicto.resuelto == False).all()
        return {
            "tipo":  "atu",
            "total": len(conflictos),
            "conflictos": [
                {
                    "id":           c.id,
                    "tipo":         c.tipo,
                    "severidad":    c.severidad,
                    "descripcion":  c.descripcion,
                    "asignacion_id": c.asignacion_id,
                }
                for c in conflictos
            ],
        }


class ATUReportFactory(AbstractReportFactory):
    """Factory concreta que crea reportes con visión global (rol admin_atu)."""

    def crear_reporte_kpis(self) -> ReporteKPIs:
        return ATUReporteKPIs()

    def crear_reporte_choferes(self) -> ReporteChoferes:
        return ATUReporteChoferes()

    def crear_reporte_conflictos(self) -> ReporteConflictos:
        return ATUReporteConflictos()


# ══════════════════════════════════════════════════════════════════════════════
# Familia Concesionario — visión filtrada por empresa
# ══════════════════════════════════════════════════════════════════════════════

class ConcesionarioReporteKPIs(ReporteKPIs):
    def __init__(self, concesionario_id: int) -> None:
        self._cid = concesionario_id

    def generar(self, db: Session) -> dict:
        hoy = date.today()
        return {
            "tipo":             "concesionario",
            "concesionario_id": self._cid,
            "fecha":            hoy,
            "choferes_activos": (
                db.query(Chofer)
                .filter(Chofer.concesionario_id == self._cid, Chofer.estado == "activo")
                .count()
            ),
            "buses_operativos": (
                db.query(Bus)
                .filter(Bus.concesionario_id == self._cid, Bus.estado == "operativo")
                .count()
            ),
            "asignaciones_hoy": (
                db.query(Asignacion)
                .join(HorarioServicio)
                .filter(
                    HorarioServicio.fecha == hoy,
                    Asignacion.concesionario_id == self._cid,
                    Asignacion.estado == "confirmada",
                )
                .count()
            ),
            "conflictos_abiertos": (
                db.query(Conflicto)
                .join(Asignacion)
                .filter(Asignacion.concesionario_id == self._cid, Conflicto.resuelto == False)
                .count()
            ),
        }


class ConcesionarioReporteChoferes(ReporteChoferes):
    def __init__(self, concesionario_id: int) -> None:
        self._cid = concesionario_id

    def generar(self, db: Session) -> dict:
        choferes = (
            db.query(Chofer)
            .filter(Chofer.concesionario_id == self._cid)
            .all()
        )
        return {
            "tipo":             "concesionario",
            "concesionario_id": self._cid,
            "total":            len(choferes),
            "choferes": [
                {
                    "id":     c.id,
                    "nombre": f"{c.nombres} {c.apellidos}",
                    "estado": c.estado,
                }
                for c in choferes
            ],
        }


class ConcesionarioReporteConflictos(ReporteConflictos):
    def __init__(self, concesionario_id: int) -> None:
        self._cid = concesionario_id

    def generar(self, db: Session) -> dict:
        conflictos = (
            db.query(Conflicto)
            .join(Asignacion)
            .filter(Asignacion.concesionario_id == self._cid, Conflicto.resuelto == False)
            .all()
        )
        return {
            "tipo":             "concesionario",
            "concesionario_id": self._cid,
            "total":            len(conflictos),
            "conflictos": [
                {
                    "id":           c.id,
                    "tipo":         c.tipo,
                    "severidad":    c.severidad,
                    "descripcion":  c.descripcion,
                    "asignacion_id": c.asignacion_id,
                }
                for c in conflictos
            ],
        }


class ConcesionarioReportFactory(AbstractReportFactory):
    """Factory concreta que crea reportes filtrados por concesionario."""

    def __init__(self, concesionario_id: int) -> None:
        self._cid = concesionario_id

    def crear_reporte_kpis(self) -> ReporteKPIs:
        return ConcesionarioReporteKPIs(self._cid)

    def crear_reporte_choferes(self) -> ReporteChoferes:
        return ConcesionarioReporteChoferes(self._cid)

    def crear_reporte_conflictos(self) -> ReporteConflictos:
        return ConcesionarioReporteConflictos(self._cid)


# ══════════════════════════════════════════════════════════════════════════════
# Helper: selecciona la factory correcta según el usuario autenticado
# ══════════════════════════════════════════════════════════════════════════════

def get_report_factory(usuario: dict) -> AbstractReportFactory:
    """
    Retorna la factory apropiada según el rol del usuario.
    `usuario` es el dict que devuelven los routers via Depends(obtener_usuario_actual).
    """
    if usuario.get("rol") == "admin_atu":
        return ATUReportFactory()
    cid = usuario.get("concesionario_id")
    if cid is None:
        raise ValueError("El usuario no tiene concesionario_id asignado")
    return ConcesionarioReportFactory(cid)
