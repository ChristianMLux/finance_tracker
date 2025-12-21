import sys
import os
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

# Add the current directory to sys.path to allow imports from backend
current_dir = os.getcwd()
sys.path.append(current_dir)

from backend.database import SessionLocal, engine
from backend import models

def check_data():
    db = SessionLocal()
    expenses = db.query(models.Expense).order_by(models.Expense.date).all()
    
    print(f"Total expenses: {len(expenses)}")
    print(f"{'ID':<5} {'Date':<12} {'d/m':<6} {'Category':<15} {'Amount':<10} {'Description'}")
    print("-" * 80)
    for e in expenses:
        date_str = e.date.strftime("%Y-%m-%d")
        dm_str = e.date.strftime("%d/%m")
        print(f"{e.id:<5} {date_str:<12} {dm_str:<6} {e.category:<15} {e.amount:<10} {e.description}")
        
    db.close()

if __name__ == "__main__":
    check_data()
