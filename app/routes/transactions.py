from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import JSONResponse

from app.auth import require_login
from app.database import get_db
from app.models import TransactionCreate, TransactionOut, SummaryOut, CategoryBreakdown

router = APIRouter(prefix="/api")


@router.get("/transactions", response_model=list[TransactionOut])
async def list_transactions(user: dict = Depends(require_login)):
    with get_db() as conn:
        rows = conn.execute(
            "SELECT id, type, amount, name, category, date, created_at "
            "FROM transactions WHERE user_id = ? ORDER BY date DESC, created_at DESC",
            (user["id"],),
        ).fetchall()
    return [dict(r) for r in rows]


@router.post("/transactions", response_model=TransactionOut, status_code=201)
async def create_transaction(
    body: TransactionCreate,
    user: dict = Depends(require_login),
):
    with get_db() as conn:
        cur = conn.execute(
            "INSERT INTO transactions (user_id, type, amount, name, category, date) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (user["id"], body.type, body.amount, body.name, body.category, body.date),
        )
        row = conn.execute(
            "SELECT id, type, amount, name, category, date, created_at "
            "FROM transactions WHERE id = ?",
            (cur.lastrowid,),
        ).fetchone()
    return dict(row)


@router.delete("/transactions/{transaction_id}", status_code=204)
async def delete_transaction(
    transaction_id: int,
    user: dict = Depends(require_login),
):
    with get_db() as conn:
        row = conn.execute(
            "SELECT user_id FROM transactions WHERE id = ?", (transaction_id,)
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Transaction not found")
        if row["user_id"] != user["id"]:
            raise HTTPException(status_code=403, detail="Not allowed")
        conn.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))


@router.get("/summary", response_model=SummaryOut)
async def get_summary(user: dict = Depends(require_login)):
    with get_db() as conn:
        income_row = conn.execute(
            "SELECT COALESCE(SUM(amount), 0) AS total FROM transactions "
            "WHERE user_id = ? AND type = 'income'",
            (user["id"],),
        ).fetchone()
        expense_row = conn.execute(
            "SELECT COALESCE(SUM(amount), 0) AS total FROM transactions "
            "WHERE user_id = ? AND type = 'expense'",
            (user["id"],),
        ).fetchone()
        category_rows = conn.execute(
            "SELECT category, SUM(amount) AS total FROM transactions "
            "WHERE user_id = ? AND type = 'expense' "
            "GROUP BY category ORDER BY total DESC",
            (user["id"],),
        ).fetchall()

    return SummaryOut(
        total_income=round(income_row["total"], 2),
        total_expenses=round(expense_row["total"], 2),
        expense_by_category=[
            CategoryBreakdown(category=r["category"] or "Uncategorized", total=round(r["total"], 2))
            for r in category_rows
        ],
    )
