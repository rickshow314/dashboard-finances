"""
Modelos de SQLAlchemy para la base de datos de Dashboard Financiero.

Entidades:
- Account: Representa cuentas de dinero (efectivo, tarjeta, broker, etc.)
- Category: Categorías para organizar transacciones (gastos/ingresos)
- Transaction: Movimientos de dinero entre cuentas o con categorías
- Budget: Presupuestos para controlar gastos por categoría
- Recurring: Gastos e ingresos recurrentes (suscripciones, salario, etc.)
- FinancialGoal: Objetivos/metas de ahorro a largo plazo
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()


# ==================== AUTENTICACIÓN ====================

class User(Base):
    """
    Modelo User - Usuario del sistema.
    
    Atributos:
        id: Identificador único (PK)
        email: Email único del usuario
        password_hash: Hash bcrypt de la contraseña
        first_name: Nombre del usuario (opcional)
        last_name: Apellido del usuario (opcional)
        is_active: Si el usuario está activo
        created_at: Fecha de creación
        updated_at: Última actualización
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relaciones
    accounts = relationship("Account", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"


class AccountType(str, enum.Enum):
    """Tipos de cuentas disponibles"""
    CASH = "efectivo"
    CARD = "tarjeta"
    BROKER = "broker"
    SAVINGS = "ahorro"
    OTHER = "otro"


class CurrencyType(str, enum.Enum):
    """Tipos de monedas soportadas"""
    USD = "USD"
    EUR = "EUR"
    MXN = "MXN"
    ARS = "ARS"
    OTHER = "OTHER"


class TransactionType(str, enum.Enum):
    """Tipos de transacciones"""
    INCOME = "ingreso"
    EXPENSE = "gasto"


class CategoryType(str, enum.Enum):
    """Tipos de categorías"""
    INCOME = "ingreso"
    EXPENSE = "gasto"


class RecurrenceFrequency(str, enum.Enum):
    """Frecuencia de recurrencia"""
    DAILY = "diaria"
    WEEKLY = "semanal"
    BIWEEKLY = "quincenal"
    MONTHLY = "mensual"
    QUARTERLY = "trimestral"
    SEMIANNUAL = "semestral"
    ANNUAL = "anual"


class GoalStatus(str, enum.Enum):
    """Estados de un objetivo financiero"""
    ACTIVE = "activo"
    PAUSED = "pausado"
    COMPLETED = "completado"
    CANCELLED = "cancelado"


class Account(Base):
    """
    Modelo Account - Representa un contenedor de dinero.
    
    Atributos:
        id: Identificador único (PK)
        user_id: FK → User (propietario de la cuenta)
        nombre: Nombre de la cuenta
        tipo: Tipo de cuenta (efectivo, tarjeta, broker, ahorro, otro)
        moneda: Moneda de la cuenta (USD, EUR, MXN, ARS, etc.)
        saldo_inicial: Saldo inicial de la cuenta (opcional, default: 0)
        created_at: Fecha de creación
        updated_at: Última actualización
        transacciones: Relación con transacciones
    """
    __tablename__ = "accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    nombre = Column(String(100), nullable=False)
    tipo = Column(Enum(AccountType), nullable=False, default=AccountType.OTHER)
    moneda = Column(Enum(CurrencyType), nullable=False, default=CurrencyType.USD)
    saldo_inicial = Column(Float, nullable=True, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relaciones
    user = relationship("User", back_populates="accounts")
    transacciones = relationship("Transaction", back_populates="account", cascade="all, delete-orphan")
    recurrentes = relationship("Recurring", back_populates="account", cascade="all, delete-orphan")
    objetivos = relationship("FinancialGoal", back_populates="account", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Account(id={self.id}, nombre='{self.nombre}', tipo={self.tipo}, moneda={self.moneda})>"


class Category(Base):
    """
    Modelo Category - Organiza transacciones en categorías.
    
    Atributos:
        id: Identificador único (PK)
        nombre: Nombre de la categoría
        tipo: Tipo de categoría (ingreso/gasto)
        created_at: Fecha de creación
        updated_at: Última actualización
        transacciones: Relación con transacciones
        presupuestos: Relación con presupuestos
    """
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    tipo = Column(Enum(CategoryType), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relaciones
    transacciones = relationship("Transaction", back_populates="category", cascade="all, delete-orphan")
    presupuestos = relationship("Budget", back_populates="category", cascade="all, delete-orphan")
    recurrentes = relationship("Recurring", back_populates="category", cascade="all, delete-orphan")
    objetivos = relationship("FinancialGoal", back_populates="category", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Category(id={self.id}, nombre='{self.nombre}', tipo={self.tipo})>"


class Transaction(Base):
    """
    Modelo Transaction - Representa movimientos de dinero.
    
    Atributos:
        id: Identificador único (PK)
        fecha: Fecha de la transacción
        cantidad: Monto de la transacción
        descripción: Descripción detallada
        tipo: Tipo de transacción (ingreso/gasto)
        account_id: FK → Account
        categoria_id: FK → Category
        created_at: Fecha de creación del registro
        updated_at: Última actualización
    """
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(DateTime, nullable=False, default=datetime.utcnow)
    cantidad = Column(Float, nullable=False)
    descripcion = Column(String(500), nullable=True)
    tipo = Column(Enum(TransactionType), nullable=False)
    
    # Foreign Keys
    account_id = Column(Integer, ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)
    categoria_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relaciones
    account = relationship("Account", back_populates="transacciones")
    category = relationship("Category", back_populates="transacciones")
    
    def __repr__(self):
        return f"<Transaction(id={self.id}, fecha={self.fecha}, cantidad={self.cantidad}, tipo={self.tipo})>"


class Budget(Base):
    """
    Modelo Budget - Presupuestos para controlar gastos por categoría.
    
    Atributos:
        id: Identificador único (PK)
        nombre: Nombre del presupuesto
        monto_limite: Monto límite del presupuesto
        monto_usado: Monto usado actualmente (se actualiza con transacciones)
        categoria_id: FK → Category
        fecha_inicio: Fecha de inicio del presupuesto
        fecha_fin: Fecha de fin del presupuesto (opcional, puede ser recurrente)
        activo: Si el presupuesto está activo o no
        created_at: Fecha de creación
        updated_at: Última actualización
    """
    __tablename__ = "budgets"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    monto_limite = Column(Float, nullable=False, default=0.0)
    monto_usado = Column(Float, nullable=False, default=0.0)
    categoria_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)
    fecha_inicio = Column(DateTime, nullable=False, default=datetime.utcnow)
    fecha_fin = Column(DateTime, nullable=True)
    activo = Column(Integer, nullable=False, default=True)  # 1 = activo, 0 = inactivo
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relación con categoría
    category = relationship("Category", back_populates="presupuestos")
    
    def __repr__(self):
        return f"<Budget(id={self.id}, nombre='{self.nombre}', monto_limite={self.monto_limite}, monto_usado={self.monto_usado})>"


class Recurring(Base):
    """
    Modelo Recurring - Gastos e ingresos recurrentes (suscripciones, salarios, etc.)
    
    Atributos:
        id: Identificador único (PK)
        nombre: Nombre del gasto/ingreso recurrente
        descripcion: Descripción detallada
        monto: Monto a restar/sumar cada vez
        tipo: Tipo (ingreso/gasto)
        frecuencia: Frecuencia de recurrencia (diaria, semanal, mensual, etc.)
        categoria_id: FK → Category (opcional)
        account_id: FK → Account (opcional)
        fecha_inicio: Cuándo inicia la recurrencia
        fecha_fin: Cuándo termina (None = indefinido)
        activo: Si está activo o no
        created_at: Fecha de creación
        updated_at: Última actualización
    """
    __tablename__ = "recurring"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(String(500), nullable=True)
    monto = Column(Float, nullable=False, default=0.0)
    tipo = Column(Enum(TransactionType), nullable=False)
    frecuencia = Column(Enum(RecurrenceFrequency), nullable=False, default=RecurrenceFrequency.MONTHLY)
    categoria_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    account_id = Column(Integer, ForeignKey("accounts.id", ondelete="SET NULL"), nullable=True)
    fecha_inicio = Column(DateTime, nullable=False, default=datetime.utcnow)
    fecha_fin = Column(DateTime, nullable=True)
    activo = Column(Integer, nullable=False, default=True)  # 1 = activo, 0 = inactivo
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relaciones
    category = relationship("Category", back_populates="recurrentes")
    account = relationship("Account", back_populates="recurrentes")
    
    def __repr__(self):
        return f"<Recurring(id={self.id}, nombre='{self.nombre}', monto={self.monto}, frecuencia={self.frecuencia})>"


class FinancialGoal(Base):
    """
    Modelo FinancialGoal - Objetivos/metas de ahorro a largo plazo.
    
    Atributos:
        id: Identificador único (PK)
        nombre: Nombre del objetivo (ej: "Vacaciones", "Coche", "Casa")
        descripcion: Descripción del objetivo
        monto_objetivo: Monto que se quiere alcanzar
        monto_ahorrado: Monto ahorrado hasta ahora
        account_id: FK → Account (donde se guarda el dinero)
        categoria_id: FK → Category (opcional, para clasificar el objetivo)
        fecha_objetivo: Fecha límite para alcanzar el objetivo
        estado: Estado del objetivo (activo, pausado, completado, cancelado)
        prioridad: Prioridad (1=baja, 5=alta)
        created_at: Fecha de creación
        updated_at: Última actualización
    """
    __tablename__ = "financial_goals"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(String(500), nullable=True)
    monto_objetivo = Column(Float, nullable=False, default=0.0)
    monto_ahorrado = Column(Float, nullable=False, default=0.0)
    account_id = Column(Integer, ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)
    categoria_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    fecha_objetivo = Column(DateTime, nullable=True)
    estado = Column(Enum(GoalStatus), nullable=False, default=GoalStatus.ACTIVE)
    prioridad = Column(Integer, nullable=False, default=3)  # 1-5
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relaciones
    account = relationship("Account", back_populates="objetivos")
    category = relationship("Category", back_populates="objetivos")
    
    def __repr__(self):
        return f"<FinancialGoal(id={self.id}, nombre='{self.nombre}', monto_objetivo={self.monto_objetivo}, monto_ahorrado={self.monto_ahorrado})>"


