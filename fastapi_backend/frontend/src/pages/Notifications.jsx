import { useEffect, useState } from "react";
import { apiFetch } from "../api";
import Navbar from "../components/Navbar";

function Notifications() {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  useEffect(() => {
    loadNotifications();
  }, []);

  async function loadNotifications() {
    setLoading(true);
    setError("");

    try {
      const response = await apiFetch("/notifications");
      const data = await response.json();

      if (!response.ok) {
        setError(
          data.detail || "Failed to load notifications"
        );
        return;
      }

      setNotifications(
        Array.isArray(data) ? data : []
      );
    } catch (err) {
      console.error(err);

      setError("Cannot connect to backend");
    } finally {
      setLoading(false);
    }
  }

  async function markAsRead(notificationId) {
    setError("");
    setMessage("");

    try {
      const response = await apiFetch(
        `/notifications/read?notification_id=${notificationId}`,
        {
          method: "POST",
        }
      );

      const data = await response.json();

      if (!response.ok) {
        setError(
          data.detail ||
            "Failed to mark notification as read"
        );
        return;
      }

      setNotifications((currentNotifications) =>
        currentNotifications.map((notification) =>
          notification.id === notificationId
            ? {
                ...notification,
                read_status: true,
              }
            : notification
        )
      );

      setMessage("Notification marked as read.");

      setTimeout(() => {
        setMessage("");
      }, 3000);
    } catch (err) {
      console.error(err);

      setError("Cannot connect to backend");
    }
  }

  function formatDate(timestamp) {
    if (!timestamp) {
      return "Unknown";
    }

    return new Date(timestamp).toLocaleString();
  }

  function getNotificationTitle(type) {
    switch (type) {
      case "order_created":
        return "Order Confirmed";

      case "payment_success":
        return "Payment Successful";

      case "payment_failed":
        return "Payment Failed";

      case "order_shipped":
        return "Order Shipped";

      case "order_delivered":
        return "Order Delivered";

      default:
        return "Notification";
    }
  }

  function getNotificationIcon(type) {
    switch (type) {
      case "order_created":
        return "📦";

      case "payment_success":
        return "💳";

      case "payment_failed":
        return "⚠️";

      case "order_shipped":
        return "🚚";

      case "order_delivered":
        return "✅";

      default:
        return "🔔";
    }
  }

  const unreadCount = notifications.filter(
    (notification) => !notification.read_status
  ).length;

  return (
    <div className="page">

      <Navbar />

      {/* =====================================================
          INTERNAL CSS
      ===================================================== */}

      <style>{`

        .notifications-page {
          max-width: 900px;
          margin: 0 auto;
        }

        .notifications-hero {
          margin-bottom: 30px;
        }

        .notifications-hero h1 {
          margin-bottom: 8px;
          font-size: 34px;
          font-weight: 700;
          color: #111827;
        }

        .notifications-hero p {
          margin: 0;
          color: #6b7280;
          font-size: 16px;
        }

        .unread-summary {
          display: inline-flex;
          align-items: center;
          gap: 8px;
          margin-top: 16px;
          padding: 8px 14px;
          background: #eff6ff;
          color: #1d4ed8;
          border-radius: 20px;
          font-size: 14px;
          font-weight: 600;
        }

        .unread-dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background: #2563eb;
        }

        .notification-message {
          margin-bottom: 20px;
          padding: 13px 16px;
          border-radius: 8px;
          background: #ecfdf5;
          border: 1px solid #a7f3d0;
          color: #047857;
          font-size: 14px;
          font-weight: 500;
        }

        .notification-error {
          margin-bottom: 20px;
          padding: 13px 16px;
          border-radius: 8px;
          background: #fef2f2;
          border: 1px solid #fecaca;
          color: #b91c1c;
          font-size: 14px;
        }

        .notifications-list {
          display: flex;
          flex-direction: column;
          gap: 16px;
        }

        .notification-card {
          display: flex;
          align-items: flex-start;
          justify-content: space-between;
          gap: 20px;
          padding: 22px 24px;
          background: #ffffff;
          border-radius: 12px;
          border: 1px solid #e5e7eb;
          box-shadow:
            0 2px 8px rgba(0, 0, 0, 0.05);
          transition:
            transform 0.2s ease,
            box-shadow 0.2s ease,
            border-color 0.2s ease;
        }

        .notification-card:hover {
          transform: translateY(-2px);
          box-shadow:
            0 6px 18px rgba(0, 0, 0, 0.08);
        }

        .notification-card.unread {
          border-left: 4px solid #2563eb;
          background: #ffffff;
        }

        .notification-card.read {
          border-left: 4px solid #d1d5db;
          background: #f9fafb;
        }

        .notification-content {
          flex: 1;
          min-width: 0;
        }

        .notification-header {
          display: flex;
          align-items: center;
          gap: 12px;
          margin-bottom: 10px;
        }

        .notification-icon {
          width: 42px;
          height: 42px;
          flex-shrink: 0;
          display: flex;
          align-items: center;
          justify-content: center;
          background: #eff6ff;
          border-radius: 10px;
          font-size: 20px;
        }

        .notification-card.read
          .notification-icon {
          background: #f3f4f6;
        }

        .notification-title {
          margin: 0;
          color: #111827;
          font-size: 18px;
          font-weight: 700;
        }

        .notification-card.read
          .notification-title {
          color: #374151;
        }

        .notification-badge {
          display: inline-flex;
          align-items: center;
          padding: 4px 9px;
          background: #dbeafe;
          color: #1d4ed8;
          border-radius: 999px;
          font-size: 11px;
          font-weight: 700;
          text-transform: uppercase;
          letter-spacing: 0.4px;
        }

        .notification-text {
          margin: 0 0 12px;
          color: #4b5563;
          font-size: 15px;
          line-height: 1.6;
        }

        .notification-date {
          display: flex;
          align-items: center;
          gap: 6px;
          color: #9ca3af;
          font-size: 13px;
        }

        .notification-action {
          flex-shrink: 0;
          display: flex;
          align-items: center;
        }

        .mark-read-button {
          border: none;
          background: #111827;
          color: #ffffff;
          padding: 10px 16px;
          border-radius: 7px;
          font-size: 13px;
          font-weight: 600;
          cursor: pointer;
          transition:
            background 0.2s ease,
            transform 0.2s ease;
        }

        .mark-read-button:hover {
          background: #2563eb;
          transform: translateY(-1px);
        }

        .mark-read-button:active {
          transform: translateY(0);
        }

        .read-label {
          display: inline-flex;
          align-items: center;
          gap: 6px;
          padding: 8px 12px;
          color: #6b7280;
          font-size: 13px;
          font-weight: 600;
        }

        .read-check {
          width: 18px;
          height: 18px;
          display: flex;
          align-items: center;
          justify-content: center;
          background: #dcfce7;
          color: #16a34a;
          border-radius: 50%;
          font-size: 11px;
        }

        .notifications-loading {
          padding: 50px 20px;
          text-align: center;
          color: #6b7280;
          background: #ffffff;
          border-radius: 12px;
          border: 1px solid #e5e7eb;
        }

        .notifications-empty {
          padding: 60px 20px;
          text-align: center;
          background: #ffffff;
          border-radius: 12px;
          border: 1px solid #e5e7eb;
          box-shadow:
            0 2px 8px rgba(0, 0, 0, 0.04);
        }

        .empty-icon {
          width: 60px;
          height: 60px;
          margin: 0 auto 18px;
          display: flex;
          align-items: center;
          justify-content: center;
          background: #f3f4f6;
          border-radius: 50%;
          font-size: 28px;
        }

        .notifications-empty h2 {
          margin: 0 0 8px;
          color: #111827;
          font-size: 22px;
        }

        .notifications-empty p {
          margin: 0;
          color: #6b7280;
        }

        @media (max-width: 700px) {

          .notification-card {
            flex-direction: column;
            padding: 18px;
          }

          .notification-action {
            width: 100%;
          }

          .mark-read-button {
            width: 100%;
          }

          .notifications-hero h1 {
            font-size: 28px;
          }

          .notification-header {
            align-items: flex-start;
          }

          .notification-title {
            font-size: 16px;
          }

        }

      `}</style>

      <main className="container">

        <div className="notifications-page">

          {/* =================================================
              HEADER
          ================================================= */}

          <section className="notifications-hero">

            <h1>
              Notifications
            </h1>

            <p>
              Stay updated about your orders
              and payments.
            </p>

            {unreadCount > 0 && (
              <div className="unread-summary">

                <span className="unread-dot" />

                You have{" "}
                <strong>
                  {unreadCount}
                </strong>{" "}
                unread notification
                {unreadCount !== 1
                  ? "s"
                  : ""}

              </div>
            )}

          </section>


          {/* =================================================
              SUCCESS MESSAGE
          ================================================= */}

          {message && (
            <div className="notification-message">
              ✓ {message}
            </div>
          )}


          {/* =================================================
              ERROR MESSAGE
          ================================================= */}

          {error && (
            <div className="notification-error">
              {error}
            </div>
          )}


          {/* =================================================
              LOADING
          ================================================= */}

          {loading ? (

            <div className="notifications-loading">
              Loading notifications...
            </div>

          ) : notifications.length === 0 ? (

            /* ===============================================
               EMPTY
            =============================================== */

            <div className="notifications-empty">

              <div className="empty-icon">
                🔔
              </div>

              <h2>
                No notifications
              </h2>

              <p>
                You don't have any notifications yet.
              </p>

            </div>

          ) : (

            /* ===============================================
               NOTIFICATION LIST
            =============================================== */

            <section className="notifications-list">

              {notifications.map(
                (notification) => (

                  <article
                    className={`notification-card ${
                      notification.read_status
                        ? "read"
                        : "unread"
                    }`}
                    key={notification.id}
                  >

                    <div className="notification-content">

                      <div className="notification-header">

                        <div className="notification-icon">
                          {getNotificationIcon(
                            notification.type
                          )}
                        </div>

                        <h2 className="notification-title">
                          {getNotificationTitle(
                            notification.type
                          )}
                        </h2>

                        {!notification.read_status && (
                          <span className="notification-badge">
                            New
                          </span>
                        )}

                      </div>

                      <p className="notification-text">
                        {notification.message}
                      </p>

                      <div className="notification-date">
                        🕐
                        {formatDate(
                          notification.timestamp
                        )}
                      </div>

                    </div>


                    {/* =====================================
                        ACTION
                    ===================================== */}

                    <div className="notification-action">

                      {!notification.read_status ? (

                        <button
                          className="mark-read-button"
                          onClick={() =>
                            markAsRead(
                              notification.id
                            )
                          }
                        >
                          Mark as read
                        </button>

                      ) : (

                        <span className="read-label">

                          <span className="read-check">
                            ✓
                          </span>

                          Read

                        </span>

                      )}

                    </div>

                  </article>

                )
              )}

            </section>

          )}

        </div>

      </main>

    </div>
  );
}

export default Notifications;