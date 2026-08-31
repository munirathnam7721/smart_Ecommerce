import { useState } from "react";

import {
  downloadReport,
} from "../adminApi";

import "./AdminReports.css";


export default function AdminReports() {

  const [
    downloading,
    setDownloading,
  ] = useState("");


  async function handleDownload(
    reportType,
    format
  ) {

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
    label,
  }) {

    const key =
      `${reportType}-${format}`;

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
        disabled={downloading !== ""}
      >

        <span>
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

      <div className="reports-header">

        <h1>
          Export Reports
        </h1>

        <p>
          Download orders, sales and user
          reports.
        </p>

      </div>


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
            Export all customer orders.
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
            Export successfully paid orders.
          </p>

          <div className="report-buttons">

            <DownloadButton
              reportType="sales"
              format="csv"
              label="Sales CSV"
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
            Export registered users and roles.
          </p>

          <div className="report-buttons">

            <DownloadButton
              reportType="users"
              format="csv"
              label="Users CSV"
            />

          </div>

        </div>

      </div>

    </div>
  );
}