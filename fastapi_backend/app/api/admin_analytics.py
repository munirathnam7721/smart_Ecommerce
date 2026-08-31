from collections import defaultdict
from decimal import Decimal

from fastapi import APIRouter, Depends

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.db.session import get_db

from app.models.order import Order, PaymentStatus
from app.models.order_item import OrderItem
from app.models.product import Product
from app.models.user import UserRole


router = APIRouter(
    prefix="/admin/analytics",
    tags=["Admin - Analytics"],
)


# ============================================================
# DASHBOARD
# ============================================================

@router.get("/dashboard")
def dashboard(
    low_stock_threshold: int = 5,
    current_user=Depends(
        require_roles(UserRole.admin)
    ),
    db: Session = Depends(get_db),
):

    # --------------------------------------------------------
    # TOTAL SALES
    # --------------------------------------------------------

    total_sales = db.scalar(
        select(
            func.count(Order.id)
        ).where(
            Order.payment_status == PaymentStatus.paid
        )
    ) or 0


    # --------------------------------------------------------
    # TOTAL REVENUE
    # --------------------------------------------------------

    total_revenue = db.scalar(
        select(
            func.coalesce(
                func.sum(Order.total),
                0
            )
        ).where(
            Order.payment_status == PaymentStatus.paid
        )
    ) or Decimal("0.00")


    # --------------------------------------------------------
    # REVENUE TRENDS
    # --------------------------------------------------------

    paid_orders = db.execute(
        select(
            Order.created_at,
            Order.total,
        )
        .where(
            Order.payment_status == PaymentStatus.paid
        )
        .order_by(
            Order.created_at.asc()
        )
    ).all()


    daily_revenue = defaultdict(
        lambda: Decimal("0.00")
    )


    for order in paid_orders:

        if order.created_at is not None:

            date_key = (
                order.created_at
                .date()
                .isoformat()
            )

            daily_revenue[date_key] += Decimal(
                str(order.total or 0)
            )


    revenue_trends = [
        {
            "date": date,
            "revenue": float(amount),
        }
        for date, amount in sorted(
            daily_revenue.items()
        )
    ]


    # --------------------------------------------------------
    # TOP SELLING PRODUCTS
    # --------------------------------------------------------

    rows = db.execute(
        select(
            Product.id.label("product_id"),

            Product.name.label(
                "product_name"
            ),

            func.coalesce(
                func.sum(
                    OrderItem.quantity
                ),
                0
            ).label(
                "quantity_sold"
            ),

            func.coalesce(
                func.sum(
                    OrderItem.item_total
                ),
                0
            ).label(
                "revenue"
            ),

        )
        .join(
            OrderItem,
            OrderItem.product_id == Product.id,
        )
        .join(
            Order,
            Order.id == OrderItem.order_id,
        )
        .where(
            Order.payment_status == PaymentStatus.paid
        )
        .group_by(
            Product.id,
            Product.name,
        )
        .order_by(
            func.sum(
                OrderItem.quantity
            ).desc()
        )
        .limit(10)
    ).all()


    top_products = [
        {
            "product_id": row.product_id,

            "product_name": row.product_name,

            "quantity_sold": int(
                row.quantity_sold or 0
            ),

            "revenue": float(
                row.revenue
                or Decimal("0.00")
            ),
        }
        for row in rows
    ]


    # --------------------------------------------------------
    # LOW STOCK
    # --------------------------------------------------------

    low_stock_rows = db.execute(
        select(
            Product.id,
            Product.name,
            Product.stock,
        )
        .where(
            Product.stock <= low_stock_threshold
        )
        .order_by(
            Product.stock.asc()
        )
    ).all()


    low_stock_products = [
        {
            "product_id": row.id,

            "product_name": row.name,

            "stock": row.stock,
        }
        for row in low_stock_rows
    ]


    # --------------------------------------------------------
    # RESPONSE
    # --------------------------------------------------------

    return {
        "total_sales": total_sales,

        "total_revenue": float(
            total_revenue
        ),

        "revenue_trends": revenue_trends,

        "top_selling_products": top_products,

        "low_stock_products": low_stock_products,
    }