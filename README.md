# Patrones de Diseño Creacionales — PC2
## Proyecto Metrohub · Backend FastAPI + SQLAlchemy

> Referencia vista en clase : [ZapDos7 / design-patterns-examples](https://github.com/ZapDos7/design-patterns-examples)

Los patrones creacionales abstraen el proceso de instanciación de objetos, ocultando **cómo** y **cuándo** se crean, y dejando al sistema enfocado en **qué** necesita. Se implementaron los 5 patrones del catálogo GoF sobre el dominio del sistema de programación de rutas y choferes del Metropolitano de Lima.

---

## Resumen de patrones de diseño

| # | Patrón | Archivo | Clase/Función principal |
|---|--------|---------|------------------------|
| 1 | Singleton | `backend/app/database.py` | `DatabaseManager.get_instance()` |
| 2 | Factory Method | `backend/app/factories/conflicto_factory.py` | `ConflictoCreator` + `get_factory()` |
| 3 | Builder | `backend/app/builders/programacion_builder.py` | `ProgramacionBuilder.build()` |
| 4 | Prototype | `backend/app/prototypes/programacion_prototype.py` | `ProgramacionPrototype.clone()` |
| 5 | Abstract Factory | `backend/app/factories/report_factory.py` | `AbstractReportFactory` + `get_report_factory()` |


## 1. Singleton

**Archivo:** `backend/app/database.py`

### Definición
Garantiza que una clase tenga **una sola instancia** en toda la aplicación y proporciona un punto de acceso global a ella.

### Problema que resuelve en Metrohub
Antes de implementarlo, `engine` y `SessionLocal` eran variables de módulo —un pseudo-Singleton de Python por ser módulo-nivel, pero sin control explícito. Si algún módulo creara una segunda instancia del motor de base de datos, se abrirían conexiones duplicadas a PostgreSQL. `DatabaseManager` hace explícita la restricción de instancia única.

### Código clave
```python
class DatabaseManager:
    _instance = None                        #guarda la única instancia

    def __new__(cls):
        if cls._instance is None:           #lazy initialization
            cls._instance = super().__new__(cls)
            cls._instance._engine = create_engine(DATABASE_URL)
            cls._instance._session_local = sessionmaker(
                autocommit=False, autoflush=False,
                bind=cls._instance._engine,
            )
        return cls._instance                #siempre el mismo objeto

    @classmethod
    def get_instance(cls) -> "DatabaseManager":
        return cls()
```

La función `get_db()` que inyectan todos los routers vía `Depends` fue actualizada para consumir el Singleton:
```python
def get_db():
    db = DatabaseManager.get_instance().session_local()
    try:
        yield db
    finally:
        db.close()
```

### Cómo usarlo
```python
from app.database import DatabaseManager

mgr_a = DatabaseManager.get_instance()
mgr_b = DatabaseManager.get_instance()
assert mgr_a is mgr_b   #true — misma instancia
```

---

## 2. Factory Method

**Archivo:** `backend/app/factories/conflicto_factory.py`

### Definición
Define una **interfaz para crear un objeto**, pero deja que las subclases decidan qué clase concreta instanciar. El método de fábrica delega la creación a los Creators concretos.

### Problema que resuelve en Metrohub
El modelo `Conflicto` acepta 9 tipos (`solapamiento_turno`, `licencia_vencida`, `exceso_8h_dia`, etc.) cada uno con una severidad por defecto distinta (`critica`, `alta`, `media`, `baja`). Sin factory, cada punto del código que crea un conflicto debe recordar qué severidad corresponde a qué tipo, dispersando lógica de negocio. El factory centraliza esa decisión.

### Código clave
```python
class ConflictoCreator(ABC):            #creator abstracto
    @property
    @abstractmethod
    def tipo(self) -> str: ...

    @property
    @abstractmethod
    def severidad_defecto(self) -> str: ...

    def crear(self, asignacion_id, descripcion, db, severidad=None) -> Conflicto:
        conflicto = Conflicto(
            asignacion_id=asignacion_id,
            tipo=self.tipo,
            severidad=severidad or self.severidad_defecto,  #default por tipo
            descripcion=descripcion,
        )
        db.add(conflicto); db.commit(); db.refresh(conflicto)
        return conflicto

#creators concretos, cada uno conoce su tipo
class LicenciaVencidaFactory(ConflictoCreator):
    tipo              = "licencia_vencida"
    severidad_defecto = "critica"

class SolapamientoTurnoFactory(ConflictoCreator):
    tipo              = "solapamiento_turno"
    severidad_defecto = "alta"
```

Un registro permite obtener el factory por nombre de tipo:
```python
def get_factory(tipo: str) -> ConflictoCreator:
    return _REGISTRY[tipo]   #lanza ValueError si tipo no existe
```

### Cómo usarlo
```python
from app.factories.conflicto_factory import get_factory

factory = get_factory("licencia_vencida")
conflicto = factory.crear(asignacion_id=12, descripcion="Licencia vencida el 2026-04-01", db=db)
# conflicto.severidad == "critica"
```

---

## 3. Builder

**Archivo:** `backend/app/builders/programacion_builder.py`

### Definición
Separa la **construcción de un objeto complejo** de su representación, permitiendo que el mismo proceso de construcción produzca diferentes representaciones. Reemplaza el patrón "telescoping constructor" (múltiples sobrecargas de constructor).

### Problema que resuelve en Metrohub
`Programacion` tiene 9 campos, de los cuales 4 son opcionales (`aprobado_por`, `fecha_aprobacion`, `observaciones`, `estado`). Pasarlos todos en una sola llamada obliga a conocer el orden y el significado de cada argumento. El Builder permite construir el objeto paso a paso, dejando claro qué se está configurando en cada llamada.

### Código clave
```python
class ProgramacionBuilder:
    def __init__(self):
        self._nombre = self._fecha_inicio = self._fecha_fin = None
        self._creado_por = None
        self._estado = "borrador"           #valor por defecto
        self._aprobado_por = self._observaciones = None

    #setters fluidos, cada uno retorna self para encadenamiento
    def nombre(self, nombre: str)           -> "ProgramacionBuilder": ...
    def fechas(self, inicio, fin)           -> "ProgramacionBuilder": ...
    def creado_por(self, usuario_id: int)   -> "ProgramacionBuilder": ...
    def observaciones(self, texto: str)     -> "ProgramacionBuilder": ...

    def build(self) -> Programacion:
        #valida campos requeridos y coherencia de fechas antes de instanciar
        ...
        return Programacion(nombre=self._nombre, fecha_inicio=..., ...)
```

### Cómo usarlo
```python
from app.builders.programacion_builder import ProgramacionBuilder
from datetime import date

prog = (
    ProgramacionBuilder()
    .nombre("Programación Q3 2026")
    .fechas(date(2026, 7, 1), date(2026, 9, 30))
    .creado_por(usuario_id=3)
    .observaciones("Incluye feriados de julio")
    .build()
)
db.add(prog); db.commit()
```

---

## 4. Prototype

**Archivo:** `backend/app/prototypes/programacion_prototype.py`

### Definición
Especifica los tipos de objetos a crear usando una **instancia prototípica** y crea nuevos objetos copiándola (clonando). Útil cuando crear un objeto desde cero es costoso o complejo y existe uno similar ya configurado.

### Problema que resuelve en Metrohub
Al inicio de cada nuevo período (mes, trimestre), los operadores de la ATU suelen repetir la misma estructura de programación con fechas actualizadas. En vez de recrear todos los campos desde cero, `ProgramacionPrototype.clone()` copia los datos relevantes del período anterior y produce un nuevo objeto en estado `borrador` listo para ajustar.

### Código clave
```python
class ProgramacionPrototype:
    def __init__(self, original: Programacion) -> None:
        self._original = original           #objeto que sirve de molde

    def clone(
        self,
        nueva_fecha_inicio: date,
        nueva_fecha_fin: date,
        nuevo_nombre: str | None = None,
        creado_por: int | None = None,
    ) -> Programacion:
        return Programacion(
            nombre        = nuevo_nombre or f"Copia de {self._original.nombre}",
            fecha_inicio  = nueva_fecha_inicio,
            fecha_fin     = nueva_fecha_fin,
            estado        = "borrador",         #aiempre inicia como borrador
            creado_por    = creado_por or self._original.creado_por,
            observaciones = f"Clonada desde programación id={self._original.id}. "
                            + (self._original.observaciones or ""),
        )
```

### Cómo usarlo
```python
from app.prototypes.programacion_prototype import ProgramacionPrototype

prog_original = db.query(Programacion).filter_by(id=5).first()
prototipo = ProgramacionPrototype(prog_original)

nueva_prog = prototipo.clone(
    nueva_fecha_inicio=date(2026, 10, 1),
    nueva_fecha_fin=date(2026, 12, 31),
)
db.add(nueva_prog); db.commit()
```

---

## 5. Abstract Factory

**Archivo:** `backend/app/factories/report_factory.py`

### Definición
Proporciona una interfaz para crear **familias de objetos relacionados** sin especificar sus clases concretas. Garantiza que los productos de una familia sean coherentes entre sí.

### Problema que resuelve en Metrohub
El dashboard sirve a dos tipos de usuario con necesidades distintas: el **administrador ATU** necesita métricas globales de todo el sistema, mientras que el **concesionario** solo debe ver datos de su propia flota. Sin Abstract Factory, habría condicionales `if rol == "admin_atu"` dispersos en cada función de reporte. La factory encapsula la decisión y garantiza que todos los reportes de una sesión correspondan al mismo contexto (global vs. filtrado).

### Código clave
```python
#interfaz abstracta — define qué tipos de reporte existen
class AbstractReportFactory(ABC):
    @abstractmethod
    def crear_reporte_kpis(self)        -> ReporteKPIs: ...
    @abstractmethod
    def crear_reporte_choferes(self)    -> ReporteChoferes: ...
    @abstractmethod
    def crear_reporte_conflictos(self)  -> ReporteConflictos: ...

#familia ATU — datos de toda la red
class ATUReportFactory(AbstractReportFactory):
    def crear_reporte_kpis(self)       -> ReporteKPIs:       return ATUReporteKPIs()
    def crear_reporte_choferes(self)   -> ReporteChoferes:   return ATUReporteChoferes()
    def crear_reporte_conflictos(self) -> ReporteConflictos: return ATUReporteConflictos()

#familia Concesionario — datos filtrados por empresa
class ConcesionarioReportFactory(AbstractReportFactory):
    def __init__(self, concesionario_id: int): self._cid = concesionario_id
    def crear_reporte_kpis(self)       -> ReporteKPIs:       return ConcesionarioReporteKPIs(self._cid)
    def crear_reporte_choferes(self)   -> ReporteChoferes:   return ConcesionarioReporteChoferes(self._cid)
    def crear_reporte_conflictos(self) -> ReporteConflictos: return ConcesionarioReporteConflictos(self._cid)
```

El helper `get_report_factory` selecciona la familia correcta según el JWT del usuario:
```python
def get_report_factory(usuario: dict) -> AbstractReportFactory:
    if usuario.get("rol") == "admin_atu":
        return ATUReportFactory()
    return ConcesionarioReportFactory(usuario["concesionario_id"])
```

### Cómo usarlo
```python
from app.factories.report_factory import get_report_factory

factory = get_report_factory(usuario)           #usuario viene de Depends(obtener_usuario_actual)
kpis      = factory.crear_reporte_kpis().generar(db)
choferes  = factory.crear_reporte_choferes().generar(db)
conflictos = factory.crear_reporte_conflictos().generar(db)
```

---

