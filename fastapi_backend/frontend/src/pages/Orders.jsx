import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { apiFetch } from "../api";
import Navbar from "../components/Navbar";

function Orders() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    loadOrders();
  }, []);

  async function loadOrders() {
    setLoading(true);
    setError("");

    try {
      const response = await apiFetch("/orders");
      const data = await response.json();

      if (!response.ok) {
        setError(
          data.detail || "Failed to load orders"
        );
        return;
      }

      setOrders(
        Array.isArray(data) ? data : []
      );
    } catch (err) {
      console.error(err);
      setError("Cannot connect to backend");
    } finally {
      setLoading(false);
    }
  }

  function formatDate(date) {
    if (!date) {
      return "Unknown";
    }

    return new Date(date).toLocaleString();
  }

  function formatAmount(amount) {
    return Number(amount || 0).toFixed(2);
  }

  function getStatusClass(status) {
    if (
      status === "paid" ||
      status === "delivered"
    ) {
      return "status-success";
    }

    if (
      status === "failed" ||
      status === "cancelled"
    ) {
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
            My Orders
          </h1>

          <p>
            View your order history and payment status.
          </p>

        </section>

        {error && (
          <div className="message error">
            {error}
          </div>
        )}

        {loading ? (

          <div className="loading">
            Loading orders...
          </div>

        ) : orders.length === 0 ? (

          <div className="empty">

            <h2>
              No orders found
            </h2>

            <p>
              You have not placed any orders yet.
            </p>

            <Link
              to="/products"
              className="primary-button"
            >
              Start Shopping
            </Link>

          </div>

        ) : (

          <div className="orders-list">

            {orders.map((order) => (

              <article
                className="order-card"
                key={order.id}
              >

                {/* Order Header */}

                <div className="order-header">

                  <div>

                    <h2>
                      Order #{order.id}
                    </h2>

                    <p>
                      {formatDate(
                        order.created_at
                      )}
                    </p>

                  </div>

                  <div className="order-total">

                    ₹
                    {formatAmount(
                      order.total
                    )}

                  </div>

                </div>


                {/* Order Status */}

                <div className="order-status">

                  <span>
                    Payment:{" "}

                    <strong
                      className={getStatusClass(
                        order.payment_status
                      )}
                    >
                      {order.payment_status}
                    </strong>
                  </span>

                  <span>
                    Order:{" "}

                    <strong
                      className={getStatusClass(
                        order.order_status
                      )}
                    >
                      {order.order_status}
                    </strong>
                  </span>

                </div>


                {/* Order Items */}

                <div className="order-items">

                  <h3>
                    Items
                  </h3>

                  {order.items?.map(
                    (item) => (

                      <div
                        className="order-item"
                        key={item.id}
                      >

                        <div>

                          <strong>
                            Product #{item.product_id}
                          </strong>

                          <p>
                            Quantity:{" "}
                            {item.quantity}
                          </p>

                        </div>

                        <div>

                          <p>
                            ₹
                            {formatAmount(
                              item.price
                            )}{" "}
                            ×{" "}
                            {item.quantity}
                          </p>

                          <strong>
                            ₹
                            {formatAmount(
                              item.item_total
                            )}
                          </strong>

                        </div>

                      </div>

                    )
                  )}

                </div>


                {/* View Details */}

                <div className="order-actions">

                  <Link
                    to={`/orders/${order.id}`}
                    className="primary-button"
                  >
                    View Order Details
                  </Link>

                </div>

              </article>

            ))}

          </div>

        )}

      </main>

    </div>
  );
}

export default Orders;