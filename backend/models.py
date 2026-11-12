from typing import List, Optional
from decimal import Decimal
from sqlalchemy.dialects.postgresql import UUID
from uuid import UUID as PyUUID
from sqlalchemy import Column, String, Text, Numeric, Integer, ForeignKey, DateTime, text
from sqlalchemy.orm import declarative_base, relationship
from pydantic import BaseModel


Base = declarative_base()

# 1. SQLALCHEMY DATABASE MODELS (String UUIDs)

class User(Base):
    __tablename__ = "users"
    uid = Column(UUID(as_uuid=True), primary_key=True)   # matches uuid in the DB
    displayname = Column(String, nullable=True)
    auth_provider_id = Column(Text, nullable=True)
    email_id = Column(Text, nullable=False, unique=True)
    createdat = Column(DateTime(timezone=True), nullable=False,)
    # ORM Relationships
    inventories = relationship("Inventory", back_populates="broker", cascade="all, delete-orphan")
    customers = relationship("Customer", back_populates="broker", cascade="all, delete-orphan")
    queries = relationship("CustomerQuery", back_populates="broker", cascade="all, delete-orphan")
    leads = relationship("Lead", back_populates="broker", cascade="all, delete-orphan")

class Inventory(Base):
    __tablename__ = "inventory"

    inventory_id = Column(Integer, primary_key=True, autoincrement=True)
    broker_id = Column(String, ForeignKey("users.uid"), nullable=False)  # String representation
    asset_type = Column(String, nullable=False)
    base_price = Column(Numeric, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    attraction = Column(Text, nullable=True)
    createdat = Column(DateTime(timezone=True), nullable=False, server_default=text("timezone('utc'::text, now())"))

    # ORM Relationships
    broker = relationship("User", back_populates="inventories")
    media = relationship("InventoryMedia", back_populates="inventory", cascade="all, delete-orphan")
    queries = relationship("CustomerQuery", back_populates="requested_inventory")


class InventoryMedia(Base):
    __tablename__ = "inventory_media"

    media_id = Column(Integer, primary_key=True, autoincrement=True)
    inventory_id = Column(Integer, ForeignKey("inventory.inventory_id"), nullable=False)
    media_url = Column(Text, nullable=False)

    # ORM Relationships
    inventory = relationship("Inventory", back_populates="media")


class Customer(Base):
    __tablename__ = "customer"

    customer_id = Column(Integer, primary_key=True, autoincrement=True)
    broker_id = Column(String, ForeignKey("users.uid"), nullable=False)  # String representation
    name = Column(Text, nullable=False)
    phone_number = Column(String, nullable=False)

    # ORM Relationships
    broker = relationship("User", back_populates="customers")
    queries = relationship("CustomerQuery", back_populates="customer", cascade="all, delete-orphan")
    leads = relationship("Lead", back_populates="customer", cascade="all, delete-orphan")


class CustomerQuery(Base):
    __tablename__ = "customer_queries"

    query_id = Column(Integer, primary_key=True, autoincrement=True)
    broker_id = Column(String, ForeignKey("users.uid"), nullable=False)  # String representation
    customer_id = Column(Integer, ForeignKey("customer.customer_id"), nullable=False)
    requested_inventory_id = Column(Integer, ForeignKey("inventory.inventory_id"), nullable=True)
    source = Column(String, nullable=False)
    asset_type = Column(String, nullable=True)
    budget_min = Column(Numeric, nullable=True)
    budget_max = Column(Numeric, nullable=True)
    preferred_location = Column(Text, nullable=True)
    requirements_text = Column(Text, nullable=True)
    query_status = Column(String, nullable=False, server_default=text("'pending'::character varying"))
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("timezone('utc'::text, now())"))
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=text("timezone('utc'::text, now())"))

    # ORM Relationships
    broker = relationship("User", back_populates="queries")
    customer = relationship("Customer", back_populates="queries")
    requested_inventory = relationship("Inventory", back_populates="queries")
    leads = relationship("Lead", back_populates="query", cascade="all, delete-orphan")


class Lead(Base):
    __tablename__ = "leads"

    lead_id = Column(Integer, primary_key=True, autoincrement=True)
    broker_id = Column(String, ForeignKey("users.uid"), nullable=False)  # String representation
    customer_id = Column(Integer, ForeignKey("customer.customer_id"), nullable=False)
    query_id = Column(Integer, ForeignKey("customer_queries.query_id"), nullable=False)
    status = Column(String, nullable=False, server_default=text("'new'::character varying"))
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("timezone('utc'::text, now())"))
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=text("timezone('utc'::text, now())"))
    closed_at = Column(DateTime(timezone=True), nullable=True)

    # ORM Relationships
    broker = relationship("User", back_populates="leads")
    customer = relationship("Customer", back_populates="leads")
    query = relationship("CustomerQuery", back_populates="leads")





# 2. PYDANTIC DATA VALIDATION SCHEMAS (String UUIDs)


class UserSetName(BaseModel):
    uid: PyUUID   # FastAPI sends it to the client as a normal string
    displayname: str

class InventoryCreate(BaseModel):
    broker_id: str
    asset_type: str
    base_price: Decimal
    title: str
    description: Optional[str] = None
    attraction: Optional[str] = None

class InventoryMediaCreate(BaseModel):
    inventory_id: int
    media_url: str

class CreateCustomer(BaseModel):
    broker_id: str
    name: str
    phone_number: str

class CreateCustomerQuery(BaseModel):
    broker_id: str
    customer_id: int
    requested_inventory_id:int
    source: str
    asset_type: Optional[str] = None
    budget_min: Optional[Decimal] = None
    budget_max: Optional[Decimal] = None
    preferred_location: Optional[str] = None
    requirements_text: Optional[str] = None
    query_status: str = "pending"

class LeadCreate(BaseModel):
    broker_id: str
    customer_id: int
    query_id: int
    status: str = "new"
    notes: Optional[str] = None


#login class 
class AuthRequest(BaseModel):
    email: str
    password: str
