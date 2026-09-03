import { useEffect, useState } from "react";

import {
  getAdminOrders,
  getAdminOrderPayment,
  getAdminReturns,
  approveAdminReturn,
  rejectAdminReturn,
} from "../adminApi";


// ============================================================
// STATUS FORMAT
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
// STATUS STYLE
// ============================================================

function getStatusStyle(status) {
  if (
    status === "paid" ||
    status === "shipped" ||
    status === "delivered" ||
    status === "returned"
  ) {
    return {
      color: "#166534",
      background: "#dcfce7",
    };
  }

  if (
    status === "failed" ||
    status === "cancelled" ||
    status === "refunded" ||
    status === "rejected"
  ) {
    return {
      color: "#991b1b",
      background: "#fee2e2",
    };
  }

  if (
    status === "return_requested" ||
    status === "pending"
  ) {
    return {
      color: "#92400e",
      background: "#fef3c7",
    };
  }

  return {
    color: "#6b7280",
    background: "#f3f4f6",
  };
}


// ============================================================
// DATE
// ============================================================

function formatDate(date) {
  if (!date) {
    return "Unknown";
  }

  const parsed = new Date(date);

  if (Number.isNaN(parsed.getTime())) {
    return "Unknown";
  }

  return parsed.toLocaleString();
}


// ============================================================
// AMOUNT
// ============================================================

function formatAmount(amount) {
  const value = Number(amount);

  if (Number.isNaN(value)) {
    return "0.00";
  }

  return value.toFixed(2);
}


// ============================================================
// ADMIN ORDERS
// ============================================================

function AdminOrders() {

  const [orders, setOrders] =
    useState([]);

  const [returns, setReturns] =
    useState([]);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  const [returnError, setReturnError] =
    useState("");

  const [paymentDetails, setPaymentDetails] =
    useState({});

  const [returnLoading, setReturnLoading] =
    useState({});


  // ==========================================================
  // LOAD ORDERS
  // ==========================================================

  async function loadOrders() {

    try {

      setError("");

      const data =
        await getAdminOrders();

      if (!Array.isArray(data)) {

        setOrders([]);

        return;
      }

      setOrders(data);

    } catch (err) {

      console.error(
        "ADMIN ORDERS ERROR:",
        err
      );

      setError(
        err.message ||
        "Unable to load admin orders"
      );

    } finally {

      setLoading(false);

    }
  }


  // ==========================================================
  // LOAD RETURNS
  // ==========================================================

  async function loadReturns() {

    try {

      setReturnError("");

      const data =
        await getAdminReturns();

      if (!Array.isArray(data)) {

        setReturns([]);

        return;
      }

      setReturns(data);

    } catch (err) {

      console.error(
        "ADMIN RETURNS ERROR:",
        err
      );

      setReturnError(
        err.message ||
        "Unable to load returns"
      );
    }
  }


  // ==========================================================
  // FIND RETURN FOR ORDER
  // ==========================================================

  function getReturnForOrder(orderId) {

    return returns.find(
      (returnItem) =>
        Number(returnItem.order_id) ===
        Number(orderId)
    );
  }


  // ==========================================================
  // LOAD PAYMENT
  // ==========================================================

  async function loadPayment(orderId) {

    try {

      const data =
        await getAdminOrderPayment(
          orderId
        );

      setPaymentDetails(
        (previous) => ({
          ...previous,
          [orderId]: data,
        })
      );

    } catch (err) {

      console.error(
        "PAYMENT DETAILS ERROR:",
        err
      );

      setError(
        err.message ||
        "Unable to load payment details"
      );
    }
  }


  // ==========================================================
  // APPROVE RETURN
  // ==========================================================

  async function handleApproveReturn(
    returnId
  ) {

    const confirmed =
      window.confirm(
        "Are you sure you want to approve this return?"
      );

    if (!confirmed) {
      return;
    }

    try {

      setReturnLoading(
        (previous) => ({
          ...previous,
          [returnId]: true,
        })
      );

      setReturnError("");

      await approveAdminReturn(
        returnId
      );

      // Reload latest data
      await loadOrders();
      await loadReturns();

    } catch (err) {

      console.error(
        "APPROVE RETURN ERROR:",
        err
      );

      setReturnError(
        err.message ||
        "Unable to approve return"
      );

    } finally {

      setReturnLoading(
        (previous) => ({
          ...previous,
          [returnId]: false,
        })
      );
    }
  }


  // ==========================================================
  // REJECT RETURN
  // ==========================================================

  async function handleRejectReturn(
    returnId
  ) {

    const confirmed =
      window.confirm(
        "Are you sure you want to reject this return?"
      );

    if (!confirmed) {
      return;
    }

    try {

      setReturnLoading(
        (previous) => ({
          ...previous,
          [returnId]: true,
        })
      );

      setReturnError("");

      await rejectAdminReturn(
        returnId
      );

      // Reload latest data
      await loadOrders();
      await loadReturns();

    } catch (err) {

      console.error(
        "REJECT RETURN ERROR:",
        err
      );

      setReturnError(
        err.message ||
        "Unable to reject return"
      );

    } finally {

      setReturnLoading(
        (previous) => ({
          ...previous,
          [returnId]: false,
        })
      );
    }
  }


  // ==========================================================
  // INITIAL LOAD
  // ==========================================================

  useEffect(() => {

    loadOrders();
    loadReturns();

  }, []);


  // ==========================================================
  // AUTOMATIC REFRESH
  // ==========================================================

  useEffect(() => {

    const interval =
      setInterval(() => {

        loadOrders();
        loadReturns();

      }, 30000);

    return () => {

      clearInterval(interval);

    };

  }, []);


  // ==========================================================
  // LOADING
  // ==========================================================

  if (loading) {

    return (

      <div style={styles.page}>

        <div style={styles.container}>

          <div style={styles.loadingBox}>

            <div style={styles.loadingSpinner}>
              ⟳
            </div>

            <h2 style={styles.loadingTitle}>
              Loading Orders
            </h2>

            <p style={styles.loadingText}>
              Please wait while orders are loading...
            </p>

          </div>

        </div>

      </div>
    );
  }


  // ==========================================================
  // PAGE
  // ==========================================================

  return (

    <div style={styles.page}>

      <div style={styles.container}>


        {/* ================================================== */}
        {/* HEADER */}
        {/* ================================================== */}

        <div style={styles.header}>

          <div>

            <h1 style={styles.title}>
              Admin Orders
            </h1>

            <p style={styles.subtitle}>
              Monitor customer orders and delivery status.
            </p>

          </div>


          <button
            type="button"
            onClick={() => {
              loadOrders();
              loadReturns();
            }}
            style={styles.refreshButton}
          >
            ↻ Refresh
          </button>

        </div>


        {/* ================================================== */}
        {/* ERROR */}
        {/* ================================================== */}

        {error && (

          <div style={styles.error}>

            <span>
              {error}
            </span>

            <button
              type="button"
              onClick={() =>
                setError("")
              }
              style={styles.closeError}
            >
              ×
            </button>

          </div>
        )}


        {/* ================================================== */}
        {/* RETURN ERROR */}
        {/* ================================================== */}

        {returnError && (

          <div style={styles.returnError}>

            <span>
              {returnError}
            </span>

            <button
              type="button"
              onClick={() =>
                setReturnError("")
              }
              style={styles.closeReturnError}
            >
              ×
            </button>

          </div>
        )}


        {/* ================================================== */}
        {/* EMPTY */}
        {/* ================================================== */}

        {!error &&
          orders.length === 0 && (

            <div style={styles.empty}>

              <div style={styles.emptyIcon}>
                📦
              </div>

              <h2 style={styles.emptyTitle}>
                No orders found
              </h2>

              <p style={styles.emptyText}>
                There are currently no customer orders.
              </p>

            </div>
          )}


        {/* ================================================== */}
        {/* ORDER LIST */}
        {/* ================================================== */}

        <div style={styles.orders}>

          {orders.map((order) => {

            const returnRequest =
              getReturnForOrder(
                order.id
              );

            const isReturnRequested =
              order.order_status ===
              "return_requested";

            const returnId =
              returnRequest?.id;

            const isReturnLoading =
              returnId
                ? returnLoading[returnId]
                : false;

            return (

              <div
                key={order.id}
                style={styles.card}
              >


                {/* ======================================== */}
                {/* ORDER HEADER */}
                {/* ======================================== */}

                <div style={styles.orderHeader}>

                  <div>

                    <h2 style={styles.orderTitle}>
                      Order #{order.id}
                    </h2>

                    <p style={styles.date}>
                      Created:{" "}
                      {formatDate(
                        order.created_at
                      )}
                    </p>

                    <p style={styles.user}>
                      Customer ID:{" "}
                      {order.user_id}
                    </p>

                  </div>


                  <div style={styles.amount}>
                    ₹
                    {formatAmount(
                      order.total
                    )}
                  </div>

                </div>


                {/* ======================================== */}
                {/* STATUS */}
                {/* ======================================== */}

                <div style={styles.statusSection}>

                  <div style={styles.statusItem}>

                    <span style={styles.label}>
                      Payment
                    </span>

                    <span
                      style={{
                        ...styles.status,
                        ...getStatusStyle(
                          order.payment_status
                        ),
                      }}
                    >
                      {formatStatus(
                        order.payment_status
                      )}
                    </span>

                  </div>


                  <div style={styles.statusItem}>

                    <span style={styles.label}>
                      Order Status
                    </span>

                    <span
                      style={{
                        ...styles.status,
                        ...getStatusStyle(
                          order.order_status
                        ),
                      }}
                    >
                      {formatStatus(
                        order.order_status
                      )}
                    </span>

                  </div>

                </div>


                {/* ======================================== */}
                {/* RETURN REQUEST INFORMATION */}
                {/* ======================================== */}

                {isReturnRequested && (

                  <div style={styles.returnRequestBox}>

                    <div style={styles.returnRequestHeader}>

                      <div>

                        <h3 style={styles.returnTitle}>
                          Return Request
                        </h3>

                        <p style={styles.returnText}>
                          Customer has requested a return
                          for this order.
                        </p>

                      </div>

                      <span style={styles.returnBadge}>
                        Return Requested
                      </span>

                    </div>


                    {returnRequest ? (

                      <div style={styles.returnActions}>

                        <button
                          type="button"
                          disabled={
                            isReturnLoading
                          }
                          onClick={() =>
                            handleApproveReturn(
                              returnRequest.id
                            )
                          }
                          style={{
                            ...styles.approveButton,
                            ...(isReturnLoading
                              ? styles.disabledButton
                              : {}),
                          }}
                        >
                          {isReturnLoading
                            ? "Processing..."
                            : "✓ Approve Return"}
                        </button>


                        <button
                          type="button"
                          disabled={
                            isReturnLoading
                          }
                          onClick={() =>
                            handleRejectReturn(
                              returnRequest.id
                            )
                          }
                          style={{
                            ...styles.rejectButton,
                            ...(isReturnLoading
                              ? styles.disabledButton
                              : {}),
                          }}
                        >
                          {isReturnLoading
                            ? "Processing..."
                            : "✕ Reject Return"}
                        </button>

                      </div>

                    ) : (

                      <p style={styles.noReturnRecord}>
                        Return request details are not
                        available yet.
                      </p>

                    )}

                  </div>
                )}


                {/* ======================================== */}
                {/* DELIVERY TIMELINE */}
                {/* ======================================== */}

                <div style={styles.timeline}>


                  {/* PAID */}

                  <div
                    style={{
                      ...styles.timelineStep,
                      opacity:
                        [
                          "paid",
                          "shipped",
                          "delivered",
                        ].includes(
                          order.order_status
                        )
                          ? 1
                          : 0.4,
                    }}
                  >

                    <div style={styles.timelineCircle}>
                      ✓
                    </div>

                    <strong>
                      Paid
                    </strong>

                  </div>


                  <div style={styles.timelineLine} />


                  {/* SHIPPED */}

                  <div
                    style={{
                      ...styles.timelineStep,
                      opacity:
                        [
                          "shipped",
                          "delivered",
                        ].includes(
                          order.order_status
                        )
                          ? 1
                          : 0.4,
                    }}
                  >

                    <div style={styles.timelineCircle}>
                      2
                    </div>

                    <strong>
                      Shipped
                    </strong>

                  </div>


                  <div style={styles.timelineLine} />


                  {/* DELIVERED */}

                  <div
                    style={{
                      ...styles.timelineStep,
                      opacity:
                        order.order_status ===
                        "delivered"
                          ? 1
                          : 0.4,
                    }}
                  >

                    <div style={styles.timelineCircle}>
                      3
                    </div>

                    <strong>
                      Delivered
                    </strong>

                  </div>

                </div>


                {/* ======================================== */}
                {/* ITEMS */}
                {/* ======================================== */}

                {Array.isArray(order.items) &&
                  order.items.length > 0 && (

                    <div style={styles.items}>

                      <h3 style={styles.sectionTitle}>
                        Order Items
                      </h3>


                      {order.items.map(
                        (item) => (

                          <div
                            key={item.id}
                            style={styles.item}
                          >

                            <div>

                              <strong>
                                Product #
                                {item.product_id}
                              </strong>

                              <p style={styles.itemText}>
                                Quantity:{" "}
                                {item.quantity}
                              </p>

                            </div>


                            <strong
                              style={styles.itemPrice}
                            >
                              ₹
                              {formatAmount(
                                item.item_total
                              )}
                            </strong>

                          </div>

                        )
                      )}

                    </div>
                  )}


                {/* ======================================== */}
                {/* ACTIONS */}
                {/* ======================================== */}

                <div style={styles.actions}>

                  <button
                    type="button"
                    onClick={() =>
                      loadPayment(
                        order.id
                      )
                    }
                    style={styles.paymentButton}
                  >
                    View Payment
                  </button>

                </div>


                {/* ======================================== */}
                {/* PAYMENT DETAILS */}
                {/* ======================================== */}

                {paymentDetails[
                  order.id
                ] && (

                  <div style={styles.paymentBox}>

                    <h3 style={styles.paymentTitle}>
                      Payment Information
                    </h3>


                    <div style={styles.paymentRow}>

                      <span>
                        Payment Status
                      </span>

                      <strong>
                        {
                          paymentDetails[
                            order.id
                          ]
                            .order_payment_status
                        }
                      </strong>

                    </div>


                    <div style={styles.paymentRow}>

                      <span>
                        Payment Record
                      </span>

                      <strong>
                        {
                          paymentDetails[
                            order.id
                          ]
                            .payment_record_status
                        }
                      </strong>

                    </div>


                    <div
                      style={{
                        ...styles.paymentRow,
                        borderBottom: "none",
                      }}
                    >

                      <span>
                        Transaction ID
                      </span>

                      <strong
                        style={styles.transactionId}
                      >
                        {
                          paymentDetails[
                            order.id
                          ]
                            .transaction_id ||
                          "N/A"
                        }
                      </strong>

                    </div>

                  </div>
                )}

              </div>
            );
          })}

        </div>

      </div>

    </div>
  );
}


// ============================================================
// INLINE STYLES
// ============================================================

const styles = {

  // ----------------------------------------------------------
  // PAGE
  // ----------------------------------------------------------

  page: {
    minHeight: "100vh",
    background: "#f5f7fb",
    padding: "30px 20px",
    boxSizing: "border-box",
  },


  container: {
    width: "100%",
    maxWidth: "1200px",
    margin: "0 auto",
    boxSizing: "border-box",
  },


  // ----------------------------------------------------------
  // HEADER
  // ----------------------------------------------------------

  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    gap: "20px",
    marginBottom: "28px",
    flexWrap: "wrap",
  },


  title: {
    margin: 0,
    fontSize: "32px",
    fontWeight: "800",
    color: "#111827",
    lineHeight: "1.2",
  },


  subtitle: {
    margin: "8px 0 0",
    color: "#6b7280",
    fontSize: "15px",
  },


  refreshButton: {
    border: "none",
    borderRadius: "8px",
    padding: "11px 18px",
    background: "#2563eb",
    color: "#ffffff",
    fontSize: "14px",
    fontWeight: "700",
    cursor: "pointer",
  },


  // ----------------------------------------------------------
  // ERROR
  // ----------------------------------------------------------

  error: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    gap: "15px",
    padding: "14px 16px",
    marginBottom: "20px",
    background: "#fee2e2",
    color: "#991b1b",
    border: "1px solid #fecaca",
    borderRadius: "8px",
    fontSize: "14px",
    fontWeight: "600",
  },


  closeError: {
    border: "none",
    background: "transparent",
    color: "#991b1b",
    fontSize: "22px",
    cursor: "pointer",
    lineHeight: 1,
  },


  returnError: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    gap: "15px",
    padding: "14px 16px",
    marginBottom: "20px",
    background: "#fff7ed",
    color: "#9a3412",
    border: "1px solid #fed7aa",
    borderRadius: "8px",
    fontSize: "14px",
    fontWeight: "600",
  },


  closeReturnError: {
    border: "none",
    background: "transparent",
    color: "#9a3412",
    fontSize: "22px",
    cursor: "pointer",
    lineHeight: 1,
  },


  // ----------------------------------------------------------
  // LOADING
  // ----------------------------------------------------------

  loadingBox: {
    minHeight: "400px",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    textAlign: "center",
  },


  loadingSpinner: {
    fontSize: "36px",
    marginBottom: "10px",
  },


  loadingTitle: {
    margin: 0,
    color: "#111827",
  },


  loadingText: {
    color: "#6b7280",
  },


  // ----------------------------------------------------------
  // EMPTY
  // ----------------------------------------------------------

  empty: {
    background: "#ffffff",
    borderRadius: "12px",
    padding: "60px 20px",
    textAlign: "center",
    border: "1px solid #e5e7eb",
  },


  emptyIcon: {
    fontSize: "42px",
    marginBottom: "12px",
  },


  emptyTitle: {
    margin: "0 0 8px",
    color: "#111827",
  },


  emptyText: {
    margin: 0,
    color: "#6b7280",
  },


  // ----------------------------------------------------------
  // ORDERS
  // ----------------------------------------------------------

  orders: {
    display: "flex",
    flexDirection: "column",
    gap: "18px",
  },


  // ----------------------------------------------------------
  // ORDER CARD
  // ----------------------------------------------------------

  card: {
    background: "#ffffff",
    border: "1px solid #e5e7eb",
    borderRadius: "12px",
    padding: "22px",
    boxShadow:
      "0 3px 12px rgba(0, 0, 0, 0.05)",
    boxSizing: "border-box",
  },


  // ----------------------------------------------------------
  // ORDER HEADER
  // ----------------------------------------------------------

  orderHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "flex-start",
    gap: "20px",
    paddingBottom: "18px",
    borderBottom: "1px solid #e5e7eb",
    flexWrap: "wrap",
  },


  orderTitle: {
    margin: 0,
    fontSize: "21px",
    fontWeight: "800",
    color: "#111827",
  },


  date: {
    margin: "7px 0 3px",
    color: "#6b7280",
    fontSize: "13px",
  },


  user: {
    margin: 0,
    color: "#6b7280",
    fontSize: "13px",
  },


  amount: {
    fontSize: "23px",
    fontWeight: "800",
    color: "#111827",
    whiteSpace: "nowrap",
  },


  // ----------------------------------------------------------
  // STATUS
  // ----------------------------------------------------------

  statusSection: {
    display: "flex",
    alignItems: "center",
    gap: "35px",
    padding: "18px 0",
    borderBottom: "1px solid #e5e7eb",
    flexWrap: "wrap",
  },


  statusItem: {
    display: "flex",
    alignItems: "center",
    gap: "8px",
  },


  label: {
    fontSize: "14px",
    fontWeight: "700",
    color: "#374151",
  },


  status: {
    display: "inline-block",
    padding: "5px 10px",
    borderRadius: "20px",
    fontSize: "12px",
    fontWeight: "700",
    whiteSpace: "nowrap",
  },


  // ----------------------------------------------------------
  // RETURN REQUEST
  // ----------------------------------------------------------

  returnRequestBox: {
    marginTop: "18px",
    padding: "18px",
    background: "#fffbeb",
    border: "1px solid #fde68a",
    borderRadius: "10px",
  },


  returnRequestHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    gap: "15px",
    flexWrap: "wrap",
  },


  returnTitle: {
    margin: 0,
    fontSize: "17px",
    fontWeight: "800",
    color: "#78350f",
  },


  returnText: {
    margin: "5px 0 0",
    fontSize: "13px",
    color: "#92400e",
  },


  returnBadge: {
    display: "inline-block",
    padding: "6px 10px",
    borderRadius: "20px",
    background: "#fef3c7",
    color: "#92400e",
    fontSize: "12px",
    fontWeight: "700",
    whiteSpace: "nowrap",
  },


  returnActions: {
    display: "flex",
    gap: "10px",
    marginTop: "16px",
    flexWrap: "wrap",
  },


  approveButton: {
    border: "none",
    borderRadius: "7px",
    padding: "10px 16px",
    background: "#16a34a",
    color: "#ffffff",
    fontSize: "13px",
    fontWeight: "700",
    cursor: "pointer",
  },


  rejectButton: {
    border: "none",
    borderRadius: "7px",
    padding: "10px 16px",
    background: "#dc2626",
    color: "#ffffff",
    fontSize: "13px",
    fontWeight: "700",
    cursor: "pointer",
  },


  disabledButton: {
    opacity: 0.6,
    cursor: "not-allowed",
  },


  noReturnRecord: {
    margin: "15px 0 0",
    color: "#92400e",
    fontSize: "13px",
  },


  // ----------------------------------------------------------
  // TIMELINE
  // ----------------------------------------------------------

  timeline: {
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    width: "100%",
    padding: "25px 5px",
    gap: "8px",
    boxSizing: "border-box",
  },


  timelineStep: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    gap: "7px",
    minWidth: "75px",
    color: "#374151",
    fontSize: "13px",
  },


  timelineCircle: {
    width: "32px",
    height: "32px",
    borderRadius: "50%",
    background: "#2563eb",
    color: "#ffffff",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontWeight: "800",
    fontSize: "13px",
  },


  timelineLine: {
    height: "3px",
    background: "#d1d5db",
    flex: 1,
    maxWidth: "140px",
    minWidth: "30px",
  },


  // ----------------------------------------------------------
  // ITEMS
  // ----------------------------------------------------------

  items: {
    paddingTop: "5px",
  },


  sectionTitle: {
    margin: "0 0 12px",
    fontSize: "16px",
    color: "#111827",
  },


  item: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    gap: "15px",
    padding: "13px 15px",
    marginBottom: "8px",
    background: "#f8fafc",
    border: "1px solid #eef2f7",
    borderRadius: "8px",
    boxSizing: "border-box",
  },


  itemText: {
    margin: "4px 0 0",
    color: "#6b7280",
    fontSize: "13px",
  },


  itemPrice: {
    whiteSpace: "nowrap",
    color: "#111827",
  },


  // ----------------------------------------------------------
  // ACTIONS
  // ----------------------------------------------------------

  actions: {
    display: "flex",
    justifyContent: "flex-end",
    marginTop: "18px",
  },


  paymentButton: {
    border: "none",
    borderRadius: "7px",
    padding: "10px 16px",
    background: "#111827",
    color: "#ffffff",
    fontSize: "13px",
    fontWeight: "700",
    cursor: "pointer",
  },


  // ----------------------------------------------------------
  // PAYMENT
  // ----------------------------------------------------------

  paymentBox: {
    marginTop: "14px",
    padding: "16px",
    background: "#f8fafc",
    border: "1px solid #e5e7eb",
    borderRadius: "8px",
    boxSizing: "border-box",
  },


  paymentTitle: {
    margin: "0 0 12px",
    fontSize: "16px",
    color: "#111827",
  },


  paymentRow: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    gap: "15px",
    padding: "8px 0",
    borderBottom: "1px solid #e5e7eb",
    fontSize: "13px",
    color: "#4b5563",
  },


  transactionId: {
    maxWidth: "60%",
    textAlign: "right",
    wordBreak: "break-all",
    color: "#111827",
  },
};


export default AdminOrders;