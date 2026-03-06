from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import config

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    __table_args__ = (
        Index('idx_user_telegram_id', 'telegram_id'),
    )

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String(100))
    full_name = Column(String(200))
    balance = Column(Float, default=0.0)
    referral_code = Column(String(20), unique=True)
    referrer_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    total_spent = Column(Float, default=0.0)

    referrals = relationship('User', backref='referrer', remote_side=[id])
    orders = relationship('Order', back_populates='user')
    tickets = relationship('SupportTicket', back_populates='user')


class Order(Base):
    __tablename__ = 'orders'
    __table_args__ = (
        Index('idx_order_order_id', 'order_id'),
        Index('idx_order_user_id', 'user_id'),
        Index('idx_order_status', 'status'),
    )

    id = Column(Integer, primary_key=True)
    order_id = Column(String(50), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    product = Column(String(100), default="Venmo Accounts")
    quantity = Column(Integer, default=1)
    amount = Column(Float, nullable=False)
    status = Column(String(20), default='pending')  # pending, paid, completed, cancelled
    payment_method = Column(String(50))
    transaction_id = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    user = relationship('User', back_populates='orders')
    payment = relationship('Payment', uselist=False, back_populates='order')


class Payment(Base):
    __tablename__ = 'payments'
    __table_args__ = (
        Index('idx_payment_order_id', 'order_id'),
        Index('idx_payment_status', 'status'),
    )

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default='USD')
    crypto_network = Column(String(20))
    wallet_address = Column(String(100))
    transaction_hash = Column(String(100))
    status = Column(String(20), default='pending')
    screenshot_path = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)
    confirmed_at = Column(DateTime, nullable=True)

    order = relationship('Order', back_populates='payment')


class SupportTicket(Base):
    __tablename__ = 'tickets'
    __table_args__ = (
        Index('idx_ticket_user_id', 'user_id'),
        Index('idx_ticket_status', 'status'),
    )

    id = Column(Integer, primary_key=True)
    ticket_number = Column(String(20), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    subject = Column(String(200))
    message = Column(Text)
    status = Column(String(20), default='open')  # open, in_progress, closed
    admin_response = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)

    user = relationship('User', back_populates='tickets')


class Referral(Base):
    __tablename__ = 'referrals'
    __table_args__ = (
        Index('idx_referral_referrer_id', 'referrer_id'),
    )

    id = Column(Integer, primary_key=True)
    referrer_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    referred_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    earned_amount = Column(Float, default=0.0)
    status = Column(String(20), default='active')
    created_at = Column(DateTime, default=datetime.utcnow)


engine = create_engine(config.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


def init_db():
    Base.metadata.create_all(engine)
    print("База данных инициализирована")