import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { apiFetch } from "../api";
import Navbar from "../components/Navbar";

function OrderDetails() {
  const { order_id } = useParams();

  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    loadOrder();
  }, [order_id]);

  async function loadOrder() {
    setLoading(true);
    setError("");

    try {
      const response = await apiFetch(
        `/orders/${order_id}`
      );

      const data = await response.json();

      if (!response.ok) {
        setError(
          data.detail || "Failed to load order"
        );
        return;
      }

      setOrder(data);
    } catch (err) {
      console.error(err);
      setError("Cannot connect to backend");
    } finally {
      setLoading(false);
    }
  }

  function formatAmount(amount) {
    return Number(amount || 0).toFixed(2);
  }

  function formatDate(date) {
    if (!date) {
      return "Unknown";
    }

    return new Date(date).toLocaleString();
  }

  function getStatusClass(status) {
    if (status === "paid" || status === "delivered") {
      return "status-success";
    }

    if (status === "failed" || status === "cancelled") {
      return "status-error";
    }

    return "status-pending";
  }

  return (
    <div className="page">
      <Navbar />

      <main className="container">

        <section className="hero">
          <h1>
            Order #{order_id}
          </h1>

          <p>
            View your complete order details.
          </p>
        </section>

        {loading ? (
          <div className="loading">
            Loading order...
          </div>
        ) : error ? (
          <div className="message error">
            {error}
          </div>
        ) : !order ? (
          <div className="empty">
            <h2>
              Order not found
            </h2>

            <p>
              This order does not exist or you do not
              have permission to view it.
            </p>

            <Link
              to="/orders"
              className="secondary-button"
            >
              Back to Orders
            </Link>
          </div>
        ) : (
          <>
            {/* Order Information */}
            <section className="cart-summary">

              <h2>
                Order Summary
              </h2>

              <p>
                <strong>
                  Order ID:
                </strong>{" "}
                #{order.id}
              </p>

              <p>
                <strong>
                  Order Date:
                </strong>{" "}
                {formatDate(order.created_at)}
              </p>

              <p>
                <strong>
                  Payment Status:
                </strong>{" "}

                <span
                  className={getStatusClass(
                    order.payment_status
                  )}
                >
                  {order.payment_status}
                </span>
              </p>

              <p>
                <strong>
                  Order Status:
                </strong>{" "}

                <span
                  className={getStatusClass(
                    order.order_status
                  )}
                >
                  {order.order_status}
                </span>
              </p>

              <hr />

              <p className="total">
                Total: ₹
                {formatAmount(order.total)}
              </p>

            </section>

            {/* Order Items */}
            <section className="cart-items">

              <h2>
                Order Items
              </h2>

              {!order.items ||
              order.items.length === 0 ? (
                <div className="empty">
                  <p>
                    No items found for this order.
                  </p>
                </div>
              ) : (
                order.items.map((item) => (
                  <article
                    className="cart-item"
                    key={item.id}
                  >

                    <div>
                      <h3>
                        Product #{item.product_id}
                      </h3>

                      <p>
                        Quantity:{" "}
                        {item.quantity}
                      </p>

                      <p>
                        Unit Price: ₹
                        {formatAmount(item.price)}
                      </p>
                    </div>

                    <div>
                      <p>
                        Item Total
                      </p>

                      <strong>
                        ₹
                        {formatAmount(
                          item.item_total
                        )}
                      </strong>
                    </div>

                  </article>
                ))
              )}

            </section>

            {/* Bottom Actions */}
            <div className="order-actions">

              <Link
                to="/orders"
                className="secondary-button"
              >
                ← Back to Orders
              </Link>

              <Link
                to="/products"
                className="primary-button"
              >
                Continue Shopping
              </Link>

            </div>
          </>
        )}

      </main>
    </div>
  );
}

export default OrderDetails;