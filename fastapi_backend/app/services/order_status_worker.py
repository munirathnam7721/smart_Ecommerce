import asyncio
from datetime import datetime, timedelta

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.order import Order, OrderStatus, PaymentStatus


async def update_order_statuses():
    while True:
        db = SessionLocal()

        try:
            now = datetime.utcnow()

            orders = db.scalars(
                select(Order).where(
                    Order.payment_status == PaymentStatus.paid
                )
            ).all()

            for order in orders:

                # Never automatically change returned/refunded orders
                if (
                    order.payment_status == PaymentStatus.refunded
                    or order.order_status == OrderStatus.returned
                ):
                    continue

                # After 3 days → DELIVERED
                if (
                    order.created_at
                    and now >= order.created_at + timedelta(days=3)
                ):
                    if order.order_status in (
                        OrderStatus.paid,
                        OrderStatus.shipped,
                    ):
                        order.order_status = OrderStatus.delivered

                # After 1 day → SHIPPED
                elif (
                    order.created_at
                    and now >= order.created_at + timedelta(days=1)
                ):
                    if order.order_status == OrderStatus.paid:
                        order.order_status = OrderStatus.shipped

            db.commit()

        except Exception as e:
            db.rollback()
            print("Order status worker error:", e)

        finally:
            db.close()

        # Check every 1 minute
        await asyncio.sleep(60)