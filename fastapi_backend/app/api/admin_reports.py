import csv
import io

from fastapi import APIRouter
from fastapi import Depends

from fastapi.responses import StreamingResponse

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.db.session import get_db

from app.models.order import Order
from app.models.order import PaymentStatus

from app.models.user import User
from app.models.user import UserRole


router = APIRouter(
    prefix="/admin/reports",
    tags=["Admin - Reports"],
)


# ============================================================
# ORDERS CSV
# ============================================================

@router.get(
    "/orders/csv"
)
def export_orders_csv(
    current_user=Depends(
        require_roles(UserRole.admin)
    ),
    db: Session = Depends(get_db),
):

    orders = db.scalars(
        select(Order)
        .order_by(
            Order.created_at.desc()
        )
    ).all()

    output = io.StringIO()

    writer = csv.writer(
        output
    )

    writer.writerow(
        [
            "Order ID",
            "User ID",
            "Total",
            "Payment Status",
            "Order Status",
            "Created At",
        ]
    )

    for order in orders:

        writer.writerow(
            [
                order.id,
                order.user_id,
                order.total,
                order.payment_status.value,
                order.order_status.value,
                order.created_at.isoformat(),
            ]
        )

    output.seek(0)

    return StreamingResponse(
        iter([
            output.getvalue()
        ]),
        media_type="text/csv",
        headers={
            "Content-Disposition":
                "attachment; filename=orders.csv"
        },
    )


# ============================================================
# USERS CSV
# ============================================================

@router.get(
    "/users/csv"
)
def export_users_csv(
    current_user=Depends(
        require_roles(UserRole.admin)
    ),
    db: Session = Depends(get_db),
):

    users = db.scalars(
        select(User)
        .order_by(
            User.created_at.desc()
        )
    ).all()

    output = io.StringIO()

    writer = csv.writer(
        output
    )

    writer.writerow(
        [
            "ID",
            "Name",
            "Email",
            "Role",
            "Active",
            "Created At",
        ]
    )

    for user in users:

        writer.writerow(
            [
                user.id,
                user.name,
                user.email,
                user.role.value,
                user.is_active,
                user.created_at.isoformat(),
            ]
        )

    output.seek(0)

    return StreamingResponse(
        iter([
            output.getvalue()
        ]),
        media_type="text/csv",
        headers={
            "Content-Disposition":
                "attachment; filename=users.csv"
        },
    )


# ============================================================
# SALES CSV
# ============================================================

@router.get(
    "/sales/csv"
)
def export_sales_csv(
    current_user=Depends(
        require_roles(UserRole.admin)
    ),
    db: Session = Depends(get_db),
):

    orders = db.scalars(
        select(Order)
        .where(
            Order.payment_status
            == PaymentStatus.paid
        )
        .order_by(
            Order.created_at.desc()
        )
    ).all()

    output = io.StringIO()

    writer = csv.writer(
        output
    )

    writer.writerow(
        [
            "Order ID",
            "User ID",
            "Amount",
            "Payment Status",
            "Order Status",
            "Date",
        ]
    )

    for order in orders:

        writer.writerow(
            [
                order.id,
                order.user_id,
                order.total,
                order.payment_status.value,
                order.order_status.value,
                order.created_at.isoformat(),
            ]
        )

    output.seek(0)

    return StreamingResponse(
        iter([
            output.getvalue()
        ]),
        media_type="text/csv",
        headers={
            "Content-Disposition":
                "attachment; filename=sales.csv"
        },
    )


# ============================================================
# ORDERS PDF
# ============================================================

@router.get(
    "/orders/pdf"
)
def export_orders_pdf(
    current_user=Depends(
        require_roles(UserRole.admin)
    ),
    db: Session = Depends(get_db),
):

    orders = db.scalars(
        select(Order)
        .order_by(
            Order.created_at.desc()
        )
    ).all()

    buffer = io.BytesIO()

    pdf = canvas.Canvas(
        buffer,
        pagesize=A4,
    )

    width, height = A4

    y = height - 40

    pdf.setFont(
        "Helvetica-Bold",
        16,
    )

    pdf.drawString(
        40,
        y,
        "Orders Report",
    )

    y -= 30

    pdf.setFont(
        "Helvetica",
        9,
    )

    for order in orders:

        line = (
            f"Order #{order.id} | "
            f"User {order.user_id} | "
            f"Total {order.total} | "
            f"Payment {order.payment_status.value} | "
            f"Status {order.order_status.value}"
        )

        pdf.drawString(
            40,
            y,
            line[:120],
        )

        y -= 16

        if y < 40:

            pdf.showPage()

            y = height - 40

            pdf.setFont(
                "Helvetica",
                9,
            )

    pdf.save()

    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                "attachment; filename=orders.pdf"
        },
    )