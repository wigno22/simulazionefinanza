# backend/main.py
from fastapi import FastAPI, HTTPException
from sqlmodel import SQLModel, Field, create_engine, Session, select
from typing import Optional, List
from datetime import datetime
import numpy as np
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

DB_URL = "sqlite:///./market.db"
engine = create_engine(DB_URL, echo=False)

app = FastAPI(title="Market Simulator API")

# Allow requests from Angular dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Stock(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    symbol: str
    name: str
    price: float
    drift: float        # expected return per step
    volatility: float   # standard deviation
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class PriceHistory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    stock_id: int
    timestamp: datetime
    price: float

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    balance: float

class Holding(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int
    stock_id: int
    quantity: int

# Pydantic models for requests
class TradeRequest(BaseModel):
    user_id: int
    symbol: str
    side: str    # "buy" or "sell"
    quantity: int

class StockRead(BaseModel):
    symbol: str
    name: str
    price: float
    volatility: float
    drift: float

def create_db_and_seed():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        existing = session.exec(select(Stock)).first()
        if existing:
            return
        # crea 10 azioni finte con diversa volatilità/drift
        sample = [
            ("TECH", "TechNova", 100.0, 0.0008, 0.02),
            ("BIO", "BioGenix", 90.0, 0.0005, 0.03),
            ("ECO", "EcoSteel", 120.0, 0.0003, 0.01),
            ("FIN", "FinEdge", 80.0, 0.0006, 0.025),
            ("RE", "RealEstateCo", 150.0, 0.0002, 0.008),
            ("ENER", "PowerFlow", 70.0, 0.0007, 0.04),
            ("RETAIL", "MallMart", 60.0, 0.0004, 0.02),
            ("AUTO", "AutoMotive", 110.0, 0.0005, 0.03),
            ("SOFT", "SoftWorks", 95.0, 0.0009, 0.035),
            ("FOOD", "GoodFoods", 50.0, 0.00025, 0.01),
        ]
        for sym, name, price, drift, vol in sample:
            s = Stock(symbol=sym, name=name, price=price, drift=drift, volatility=vol)
            session.add(s)
        # crea utente demo
        user = User(username="player1", balance=10000.0)
        session.add(user)
        session.commit()

@app.on_event("startup")
def on_startup():
    create_db_and_seed()

@app.get("/stocks", response_model=List[StockRead])
def list_stocks():
    with Session(engine) as session:
        stocks = session.exec(select(Stock)).all()
        return [StockRead(symbol=s.symbol, name=s.name, price=s.price, volatility=s.volatility, drift=s.drift) for s in stocks]

@app.post("/simulate/step")
def simulate_step(days: int = 1):
    """Avanza la simulazione di `days` passi (es. giorni virtuali)."""
    with Session(engine) as session:
        stocks = session.exec(select(Stock)).all()
        for _ in range(days):
            for s in stocks:
                # Geometric Brownian Motion per prezzo
                mu = s.drift
                sigma = s.volatility
                z = np.random.normal()
                # dt = 1 (a step)
                new_price = s.price * np.exp((mu - 0.5 * sigma**2) + sigma * z)
                # evita prezzi negativi
                new_price = max(new_price, 0.01)
                s.price = float(round(new_price, 2))
                s.last_updated = datetime.utcnow()
                ph = PriceHistory(stock_id=s.id, timestamp=s.last_updated, price=s.price)
                session.add(ph)
        session.commit()
    return {"status": "ok", "days": days}

@app.get("/users/{user_id}/portfolio")
def get_portfolio(user_id: int):
    with Session(engine) as session:
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        holdings = session.exec(select(Holding).where(Holding.user_id == user_id)).all()
        # attach current price and value
        result = {"username": user.username, "balance": user.balance, "positions": []}
        for h in holdings:
            stock = session.get(Stock, h.stock_id)
            result["positions"].append({
                "symbol": stock.symbol,
                "name": stock.name,
                "quantity": h.quantity,
                "price": stock.price,
                "value": round(h.quantity * stock.price, 2)
            })
        return result

@app.post("/trade")
def trade(tr: TradeRequest):
    if tr.quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be positive")
    with Session(engine) as session:
        user = session.get(User, tr.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        stock = session.exec(select(Stock).where(Stock.symbol == tr.symbol)).first()
        if not stock:
            raise HTTPException(status_code=404, detail="Stock not found")
        cost = round(stock.price * tr.quantity, 2)
        holding = session.exec(select(Holding).where(Holding.user_id==tr.user_id, Holding.stock_id==stock.id)).first()
        if tr.side == "buy":
            if user.balance < cost:
                raise HTTPException(status_code=400, detail="Insufficient balance")
            user.balance -= cost
            if holding:
                holding.quantity += tr.quantity
            else:
                holding = Holding(user_id=user.id, stock_id=stock.id, quantity=tr.quantity)
                session.add(holding)
            session.commit()
            return {"status":"bought", "symbol": stock.symbol, "quantity": tr.quantity, "cost": cost}
        elif tr.side == "sell":
            if not holding or holding.quantity < tr.quantity:
                raise HTTPException(status_code=400, detail="Not enough shares to sell")
            holding.quantity -= tr.quantity
            user.balance += cost
            if holding.quantity == 0:
                session.delete(holding)
            session.commit()
            return {"status":"sold", "symbol": stock.symbol, "quantity": tr.quantity, "received": cost}
        else:
            raise HTTPException(status_code=400, detail="side must be 'buy' or 'sell'")


@app.get("/stocks/{symbol}/history")
def get_price_history(symbol: str):
    """Ritorna lo storico dei prezzi di una specifica azione"""
    with Session(engine) as session:
        stock = session.exec(select(Stock).where(Stock.symbol == symbol)).first()
        if not stock:
            raise HTTPException(status_code=404, detail="Stock not found")
        history = session.exec(
            select(PriceHistory).where(PriceHistory.stock_id == stock.id).order_by(PriceHistory.timestamp)
        ).all()
        return [{"timestamp": ph.timestamp, "price": ph.price} for ph in history]


from pydantic import BaseModel


class UserCreateRequest(BaseModel):
    username: str
    balance: float = 10000.0  # saldo iniziale di default


@app.post("/users", response_model=dict)
def create_user(user_req: UserCreateRequest):
    with Session(engine) as session:
        # controlla che l'username non esista già
        existing = session.exec(select(User).where(User.username == user_req.username)).first()
        if existing:
            raise HTTPException(status_code=400, detail="Username already exists")

        user = User(username=user_req.username, balance=user_req.balance)
        session.add(user)
        session.commit()
        session.refresh(user)
        return {"id": user.id, "username": user.username, "balance": user.balance}


@app.get("/users", response_model=List[dict])
def list_users():
    with Session(engine) as session:
        users = session.exec(select(User)).all()
        return [{"id": u.id, "username": u.username, "balance": u.balance} for u in users]

