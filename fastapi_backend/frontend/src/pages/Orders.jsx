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

  // ============================================================
  // LOAD ORDERS
  // GET /orders
  // ============================================================

  async function loadOrders() {
    setLoading(true);
    setError("");

    try {
      const response = await apiFetch("/orders");

      let data = null;

      try {
        data = await response.json();
      } catch {
        data = null;
      }

      console.log("ORDERS FROM BACKEND:", data);

      if (!response.ok) {
        const message =
          typeof data?.detail === "string"
            ? data.detail
            : "Failed to load orders";

        setError(message);
        return;
      }

      if (!Array.isArray(data)) {
        setOrders([]);
        return;
      }

      setOrders(data);
    } catch (err) {
      console.error("LOAD ORDERS ERROR:", err);

      setError("Cannot connect to backend");
    } finally {
      setLoading(false);
    }
  }

  // ============================================================
  // REQUEST RETURN
  // POST /orders/{order_id}/return
  // ============================================================

  async function handleReturnRequest(orderId) {
    const reason = window.prompt(
      "Why do you want to return this order?"
    );

    if (!reason || !reason.trim()) {
      return;
    }

    const comment = window.prompt(
      "Additional comment (optional):"
    );

    const payload = {
      reason: reason.trim(),
      comment:
        comment && comment.trim()
          ? comment.trim()
          : null,
    };

    console.log("RETURN REQUEST:", {
      orderId,
      payload,
    });

    try {
      const response = await apiFetch(
        `/orders/${orderId}/return`,
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
          },

          body: JSON.stringify(payload),
        }
      );

      let data = null;

      try {
        data = await response.json();
      } catch {
        data = null;
      }

      console.log("RETURN RESPONSE:", {
        status: response.status,
        data,
      });

      // ========================================================
      // ERROR
      // ========================================================

      if (!response.ok) {
        let message = "Unable to submit return request";

        if (typeof data?.detail === "string") {
          message = data.detail;
        } else if (data?.detail?.message) {
          message = data.detail.message;
        }

        alert(message);

        return;
      }

      // ========================================================
      // SUCCESS
      // ========================================================

      alert(
        "Return request submitted successfully!"
      );

      // Reload orders.
      // delivered -> return_requested
      await loadOrders();
    } catch (err) {
      console.error(
        "RETURN REQUEST ERROR:",
        err
      );

      alert(
        "Cannot connect to backend"
      );
    }
  }

  // ============================================================
  // FORMAT DATE
  // ============================================================

  function formatDate(date) {
    if (!date) {
      return "Unknown";
    }

    const parsedDate = new Date(date);

    if (Number.isNaN(parsedDate.getTime())) {
      return "Unknown";
    }

    return parsedDate.toLocaleString();
  }

  // ============================================================
  // FORMAT AMOUNT
  // ============================================================

  function formatAmount(amount) {
    const value = Number(amount);

    if (Number.isNaN(value)) {
      return "0.00";
    }

    return value.toFixed(2);
  }

  // ============================================================
  // DISPLAY STATUS
  // ============================================================

  function formatStatus(status) {
    if (!status) {
      return "Unknown";
    }

    return status
      .replaceAll("_", " ")
      .replace(/\b\w/g, (letter) =>
        letter.toUpperCase()
      );
  }

  // ============================================================
  // STATUS CLASS
  // ============================================================

  function getStatusClass(status) {
    if (
      status === "paid" ||
      status === "delivered"
    ) {
      return "status-success";
    }

    if (
      status === "failed" ||
      status === "cancelled" ||
      status === "rejected"
    ) {
      return "status-error";
    }

    if (
      status === "return_requested"
    ) {
      return "status-pending";
    }

    return "status-pending";
  }

  // ============================================================
  // PAGE
  // ============================================================

  return (
    <div className="page">
      <Navbar />

      <main className="container">

        {/* ================================================== */}
        {/* HERO */}
        {/* ================================================== */}

        <section className="hero">
          <h1>
            My Orders
          </h1>

          <p>
            View your order history and payment status.
          </p>
        </section>

        {/* ================================================== */}
        {/* ERROR */}
        {/* ================================================== */}

        {error && (
          <div className="message error">
            {error}
          </div>
        )}

        {/* ================================================== */}
        {/* LOADING */}
        {/* ================================================== */}

        {loading ? (

          <div className="loading">
            Loading orders...
          </div>

        ) : orders.length === 0 ? (

          /* ================================================== */
          /* EMPTY */
          /* ================================================== */

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

          /* ================================================== */
          /* ORDERS */
          /* ================================================== */

          <div
            className="orders-list"
            style={{
              display: "flex",
              flexDirection: "column",
              gap: "25px",
            }}
          >

            {orders.map((order) => (

              <article
                key={order.id}
                className="order-card"
                style={{
                  background: "#ffffff",
                  borderRadius: "12px",
                  padding: "28px",
                  marginBottom: "0",
                  boxShadow:
                    "0 4px 14px rgba(0, 0, 0, 0.08)",
                }}
              >

                {/* ================================================== */}
                {/* ORDER HEADER */}
                {/* ================================================== */}

                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "flex-start",
                    paddingBottom: "20px",
                    borderBottom:
                      "1px solid #e5e7eb",
                  }}
                >

                  <div>

                    <h2
                      style={{
                        margin: "0 0 8px",
                      }}
                    >
                      Order #{order.id}
                    </h2>

                    <p
                      style={{
                        margin: 0,
                        color: "#666",
                      }}
                    >
                      {formatDate(
                        order.created_at
                      )}
                    </p>

                  </div>

                  <div
                    style={{
                      fontSize: "22px",
                      fontWeight: "700",
                      whiteSpace: "nowrap",
                    }}
                  >
                    ₹
                    {formatAmount(
                      order.total
                    )}
                  </div>

                </div>

                {/* ================================================== */}
                {/* STATUS */}
                {/* ================================================== */}

                <div
                  style={{
                    display: "flex",
                    gap: "30px",
                    padding: "18px 0",
                    borderBottom:
                      "1px solid #e5e7eb",
                    flexWrap: "wrap",
                  }}
                >

                  <span>
                    Payment:{" "}

                    <strong
                      className={getStatusClass(
                        order.payment_status
                      )}
                    >
                      {formatStatus(
                        order.payment_status
                      )}
                    </strong>
                  </span>

                  <span>
                    Order:{" "}

                    <strong
                      className={getStatusClass(
                        order.order_status
                      )}
                    >
                      {formatStatus(
                        order.order_status
                      )}
                    </strong>
                  </span>

                </div>

                {/* ================================================== */}
                {/* ITEMS */}
                {/* ================================================== */}

                <div
                  style={{
                    paddingTop: "20px",
                  }}
                >

                  <h3
                    style={{
                      margin: "0 0 15px",
                    }}
                  >
                    Items
                  </h3>

                  {order.items?.map(
                    (item) => (

                      <div
                        key={item.id}
                        style={{
                          display: "flex",
                          justifyContent:
                            "space-between",
                          alignItems: "center",
                          padding: "16px",
                          marginBottom: "12px",
                          background:
                            "#f8fafc",
                          border:
                            "1px solid #e5e7eb",
                          borderRadius: "8px",
                          gap: "20px",
                        }}
                      >

                        {/* PRODUCT */}

                        <div>

                          <strong>
                            Product #{item.product_id}
                          </strong>

                          <p
                            style={{
                              margin:
                                "6px 0 0",
                              color: "#666",
                            }}
                          >
                            Quantity:{" "}
                            {item.quantity}
                          </p>

                        </div>

                        {/* PRICE */}

                        <div
                          style={{
                            textAlign: "right",
                          }}
                        >

                          <p
                            style={{
                              margin:
                                "0 0 5px",
                              color: "#666",
                            }}
                          >
                            ₹
                            {formatAmount(
                              item.price
                            )}

                            {" × "}

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

                {/* ================================================== */}
                {/* ACTION BUTTONS */}
                {/* ================================================== */}

                <div
                  style={{
                    marginTop: "25px",
                    paddingTop: "20px",
                    borderTop:
                      "1px solid #e5e7eb",
                    display: "flex",
                    justifyContent: "flex-end",
                    gap: "12px",
                    flexWrap: "wrap",
                  }}
                >

                  {/* ================================================== */}
                  {/* RETURN BUTTON */}
                  {/* Only delivered orders */}
                  {/* ================================================== */}

                  {order.order_status ===
                    "delivered" && (

                    <button
                      type="button"
                      onClick={() =>
                        handleReturnRequest(
                          order.id
                        )
                      }
                      style={{
                        display: "inline-flex",
                        alignItems: "center",
                        justifyContent: "center",
                        padding: "12px 22px",
                        minWidth: "170px",
                        background: "#dc2626",
                        color: "#ffffff",
                        border: "none",
                        borderRadius: "8px",
                        fontWeight: "600",
                        fontSize: "15px",
                        cursor: "pointer",
                        boxSizing: "border-box",
                      }}
                    >
                      Request Return
                    </button>
                  )}

                  {/* ================================================== */}
                  {/* RETURN REQUESTED MESSAGE */}
                  {/* ================================================== */}

                  {order.order_status ===
                    "return_requested" && (

                    <div
                      style={{
                        display: "inline-flex",
                        alignItems: "center",
                        justifyContent: "center",
                        padding: "12px 22px",
                        minWidth: "190px",
                        background: "#fef3c7",
                        color: "#92400e",
                        borderRadius: "8px",
                        fontWeight: "600",
                        fontSize: "15px",
                        boxSizing: "border-box",
                      }}
                    >
                      Return Requested
                    </div>
                  )}

                  {/* ================================================== */}
                  {/* VIEW ORDER DETAILS */}
                  {/* ================================================== */}

                  <Link
                    to={`/orders/${order.id}`}
                    style={{
                      display: "inline-flex",
                      alignItems: "center",
                      justifyContent: "center",
                      padding: "12px 22px",
                      minWidth: "190px",
                      background: "#2563eb",
                      color: "#ffffff",
                      textDecoration: "none",
                      borderRadius: "8px",
                      fontWeight: "600",
                      fontSize: "15px",
                      boxSizing: "border-box",
                    }}
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