import { useState } from "react";
import { downloadReport } from "../adminApi";

import "./AdminReports.css";

export default function AdminReports() {

  const [downloading, setDownloading] = useState("");

  async function handleDownload(reportType, format) {

    const key = `${reportType}-${format}`;

    try {

      setDownloading(key);

      await downloadReport(
        reportType,
        format
      );

    } catch (error) {

      console.error(
        "Report download failed:",
        error
      );

      alert(
        error.message ||
        "Unable to download report"
      );

    } finally {

      setDownloading("");

    }
  }

  function DownloadButton({
    reportType,
    format,
    label
  }) {

    const key = `${reportType}-${format}`;

    const isDownloading =
      downloading === key;

    return (
      <button
        className="report-button"
        onClick={() =>
          handleDownload(
            reportType,
            format
          )
        }
        disabled={
          downloading !== "" &&
          !isDownloading
        }
      >

        <span className="format-badge">
          {format.toUpperCase()}
        </span>

        <strong>
          {isDownloading
            ? "Downloading..."
            : label}
        </strong>

      </button>
    );
  }

  return (
    <div className="admin-reports">

      {/* HEADER */}

      <div className="reports-header">

        <div>
          <h1>
            Export Reports
          </h1>

          <p>
            Download orders, sales and user
            reports in CSV or PDF format.
          </p>
        </div>

      </div>


      {/* REPORTS */}

      <div className="reports-grid">


        {/* ORDERS */}

        <div className="report-card">

          <div className="report-icon">
            🧾
          </div>

          <h2>
            Orders Report
          </h2>

          <p>
            Export all customer orders,
            including payment status and
            order status.
          </p>

          <div className="report-buttons">

            <DownloadButton
              reportType="orders"
              format="csv"
              label="Orders CSV"
            />

            <DownloadButton
              reportType="orders"
              format="pdf"
              label="Orders PDF"
            />

          </div>

        </div>


        {/* SALES */}

        <div className="report-card">

          <div className="report-icon">
            📈
          </div>

          <h2>
            Sales Report
          </h2>

          <p>
            Export successfully paid orders
            and sales information.
          </p>

          <div className="report-buttons">

            <DownloadButton
              reportType="sales"
              format="csv"
              label="Sales CSV"
            />

            <DownloadButton
              reportType="sales"
              format="pdf"
              label="Sales PDF"
            />

          </div>

        </div>


        {/* USERS */}

        <div className="report-card">

          <div className="report-icon">
            👥
          </div>

          <h2>
            Users Report
          </h2>

          <p>
            Export registered users, roles,
            account status and registration
            dates.
          </p>

          <div className="report-buttons">

            <DownloadButton
              reportType="users"
              format="csv"
              label="Users CSV"
            />

            <DownloadButton
              reportType="users"
              format="pdf"
              label="Users PDF"
            />

          </div>

        </div>

      </div>


      {/* BACK TO HOME */}

      <div className="reports-home">

        <button
          className="home-button"
          onClick={() =>
            window.location.href = "/products"
          }
        >
          ← Back to Home
        </button>

      </div>

    </div>
  );
}