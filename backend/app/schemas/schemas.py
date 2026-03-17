"""
Schemas de Pydantic para validación de datos en los endpoints.

Usados para:
- Validar requests
- Documentación automática en Swagger
- Serialización de responses
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum


class AccountTypeSchema(str, Enum):
    """Tipos de cuentas"""
    CASH = "efectivo"
    CARD = "tarjeta"
    BROKER = "broker"
    SAVINGS = "ahorro"
    OTHER = "otro"


class CurrencyTypeSchema(str, Enum):
    """Tipos de monedas"""
    USD = "USD"
    EUR = "EUR"
    MXN = "MXN"
    ARS = "ARS"
    OTHER = "OTHER"


class TransactionTypeSchema(str, Enum):
    """Tipos de transacciones"""
    INCOME = "ingreso"
    EXPENSE = "gasto"


class CategoryTypeSchema(str, Enum):
    """Tipos de categorías"""
    INCOME = "ingreso"
    EXPENSE = "gasto"


# ==================== ACCOUNT SCHEMAS ====================

class AccountCreate(BaseModel):
    """Schema para crear una cuenta"""
    nombre: str = Field(..., min_length=1, max_length=100, description="Nombre de la cuenta")
    tipo: AccountTypeSchema = Field(default=AccountTypeSchema.OTHER, description="Tipo de cuenta")
    moneda: CurrencyTypeSchema = Field(default=CurrencyTypeSchema.USD, description="Moneda de la cuenta")
    saldo_inicial: Optional[float] = Field(default=0.0, ge=0, description="Saldo inicial")


class AccountUpdate(BaseModel):
    """Schema para actualizar una cuenta"""
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    tipo: Optional[AccountTypeSchema] = None
    moneda: Optional[CurrencyTypeSchema] = None
    saldo_inicial: Optional[float] = Field(None, ge=0)


class AccountResponse(BaseModel):
    """Schema de response para una cuenta"""
    id: int
    nombre: str
    tipo: str
    moneda: str
    saldo_inicial: Optional[float]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== CATEGORY SCHEMAS ====================

class CategoryCreate(BaseModel):
    """Schema para crear una categoría"""
    nombre: str = Field(..., min_length=1, max_length=100, description="Nombre de la categoría")
    tipo: CategoryTypeSchema = Field(..., description="Tipo de categoría (ingreso/gasto)")


class CategoryUpdate(BaseModel):
    """Schema para actualizar una categoría"""
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    tipo: Optional[CategoryTypeSchema] = None


class CategoryResponse(BaseModel):
    """Schema de response para una categoría"""
    id: int
    nombre: str
    tipo: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== TRANSACTION SCHEMAS ====================

class TransactionCreate(BaseModel):
    """Schema para crear una transacción"""
    fecha: datetime = Field(default_factory=datetime.utcnow, description="Fecha de la transacción")
    cantidad: float = Field(..., gt=0, description="Monto de la transacción")
    descripcion: Optional[str] = Field(None, max_length=500, description="Descripción")
    tipo: TransactionTypeSchema = Field(..., description="Tipo de transacción (ingreso/gasto)")
    account_id: int = Field(..., gt=0, description="ID de la cuenta")
    categoria_id: int = Field(..., gt=0, description="ID de la categoría")


class TransactionUpdate(BaseModel):
    """Schema para actualizar una transacción"""
    fecha: Optional[datetime] = None
    cantidad: Optional[float] = Field(None, gt=0)
    descripcion: Optional[str] = Field(None, max_length=500)
    tipo: Optional[TransactionTypeSchema] = None
    account_id: Optional[int] = Field(None, gt=0)
    categoria_id: Optional[int] = Field(None, gt=0)


class TransactionResponse(BaseModel):
    """Schema de response para una transacción"""
    id: int
    fecha: datetime
    cantidad: float
    descripcion: Optional[str]
    tipo: str
    account_id: int
    categoria_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TransactionWithRelations(TransactionResponse):
    """Schema de response con relaciones embebidas"""
    account: AccountResponse
    category: CategoryResponse


# ==================== BUDGET SCHEMAS ====================

class BudgetCreate(BaseModel):
    """Schema para crear un presupuesto"""
    nombre: str = Field(..., min_length=1, max_length=100, description="Nombre del presupuesto")
    monto_limite: float = Field(..., gt=0, description="Monto límite del presupuesto")
    categoria_id: int = Field(..., gt=0, description="ID de la categoría")
    fecha_inicio: datetime = Field(default_factory=datetime.utcnow, description="Fecha de inicio")
    fecha_fin: Optional[datetime] = Field(None, description="Fecha de fin (opcional)")
    activo: bool = Field(default=True, description="Si el presupuesto está activo")


class BudgetUpdate(BaseModel):
    """Schema para actualizar un presupuesto"""
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    monto_limite: Optional[float] = Field(None, gt=0)
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None
    activo: Optional[bool] = None


class BudgetResponse(BaseModel):
    """Schema de response para un presupuesto"""
    id: int
    nombre: str
    monto_limite: float
    monto_usado: float
    categoria_id: int
    fecha_inicio: datetime
    fecha_fin: Optional[datetime]
    activo: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BudgetWithCategory(BudgetResponse):
    """Schema de response con categoría embebida"""
    category: CategoryResponse


# ==================== RECURRING SCHEMAS ====================

class RecurringCreate(BaseModel):
    """Schema para crear un gasto/ingreso recurrente"""
    nombre: str = Field(..., min_length=1, max_length=100, description="Nombre")
    descripcion: Optional[str] = Field(None, max_length=500)
    monto: float = Field(..., gt=0, description="Monto")
    tipo: TransactionTypeSchema = Field(..., description="Tipo (ingreso/gasto)")
    frecuencia: str = Field(..., description="Frecuencia (diaria, semanal, mensual, etc.)")
    categoria_id: Optional[int] = Field(None, gt=0)
    account_id: Optional[int] = Field(None, gt=0)
    fecha_inicio: datetime = Field(default_factory=datetime.utcnow)
    fecha_fin: Optional[datetime] = None
    activo: bool = Field(default=True)


class RecurringUpdate(BaseModel):
    """Schema para actualizar un recurrente"""
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    descripcion: Optional[str] = Field(None, max_length=500)
    monto: Optional[float] = Field(None, gt=0)
    tipo: Optional[TransactionTypeSchema] = None
    frecuencia: Optional[str] = None
    categoria_id: Optional[int] = Field(None, gt=0)
    account_id: Optional[int] = Field(None, gt=0)
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None
    activo: Optional[bool] = None


class RecurringResponse(BaseModel):
    """Schema de response para un recurrente"""
    id: int
    nombre: str
    descripcion: Optional[str]
    monto: float
    tipo: str
    frecuencia: str
    categoria_id: Optional[int]
    account_id: Optional[int]
    fecha_inicio: datetime
    fecha_fin: Optional[datetime]
    activo: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RecurringWithRelations(RecurringResponse):
    """Schema con relaciones embebidas"""
    category: Optional[CategoryResponse]
    account: Optional[AccountResponse]


# ==================== FINANCIAL GOAL SCHEMAS ====================

class FinancialGoalCreate(BaseModel):
    """Schema para crear un objetivo financiero"""
    nombre: str = Field(..., min_length=1, max_length=100, description="Nombre del objetivo")
    descripcion: Optional[str] = Field(None, max_length=500)
    monto_objetivo: float = Field(..., gt=0, description="Monto a alcanzar")
    account_id: int = Field(..., gt=0, description="Cuenta donde guardar el dinero")
    categoria_id: Optional[int] = Field(None, gt=0)
    fecha_objetivo: Optional[datetime] = None
    estado: str = Field(default="activo", description="Estado (activo, pausado, completado, cancelado)")
    prioridad: int = Field(default=3, ge=1, le=5, description="Prioridad 1-5")


class FinancialGoalUpdate(BaseModel):
    """Schema para actualizar un objetivo"""
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    descripcion: Optional[str] = Field(None, max_length=500)
    monto_objetivo: Optional[float] = Field(None, gt=0)
    monto_ahorrado: Optional[float] = Field(None, ge=0)
    categoria_id: Optional[int] = Field(None, gt=0)
    fecha_objetivo: Optional[datetime] = None
    estado: Optional[str] = None
    prioridad: Optional[int] = Field(None, ge=1, le=5)


class FinancialGoalResponse(BaseModel):
    """Schema de response para un objetivo"""
    id: int
    nombre: str
    descripcion: Optional[str]
    monto_objetivo: float
    monto_ahorrado: float
    account_id: int
    categoria_id: Optional[int]
    fecha_objetivo: Optional[datetime]
    estado: str
    prioridad: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FinancialGoalWithRelations(FinancialGoalResponse):
    """Schema con relaciones embebidas"""
    account: AccountResponse
    category: Optional[CategoryResponse]

    @property
    def porcentaje_avance(self) -> float:
        """Calcula el porcentaje de avance hacia el objetivo"""
        if self.monto_objetivo <= 0:
            return 0.0
        return (self.monto_ahorrado / self.monto_objetivo) * 100


