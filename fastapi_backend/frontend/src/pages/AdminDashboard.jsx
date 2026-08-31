import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  Line,
  Bar,
} from "react-chartjs-2";

import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";

import {
  getAdminDashboard,
} from "../adminApi";

import "./AdminDashboard.css";


// ============================================================
// CHART.JS REGISTRATION
// ============================================================

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
);


// ============================================================
// COMPONENT
// ============================================================

export default function AdminDashboard() {

  const navigate = useNavigate();

  const [
    dashboard,
    setDashboard,
  ] = useState(null);

  const [
    loading,
    setLoading,
  ] = useState(true);

  const [
    error,
    setError,
  ] = useState("");


  // ==========================================================
  // LOAD DASHBOARD
  // ==========================================================

  useEffect(() => {

    loadDashboard();

  }, []);


  async function loadDashboard() {

    try {

      setLoading(true);

      setError("");

      const data =
        await getAdminDashboard(5);

      setDashboard(data);

    } catch (err) {

      console.error(
        "Dashboard error:",
        err
      );

      setError(
        err.message ||
        "Unable to load dashboard"
      );

    } finally {

      setLoading(false);

    }
  }


  // ==========================================================
  // LOADING
  // ==========================================================

  if (loading) {

    return (
      <div className="admin-dashboard">

        <div className="dashboard-loading">
          Loading admin dashboard...
        </div>

      </div>
    );
  }


  // ==========================================================
  // ERROR
  // ==========================================================

  if (error) {

    return (
      <div className="admin-dashboard">

        <div className="dashboard-error">

          <h2>
            Unable to load dashboard
          </h2>

          <p>
            {error}
          </p>

          <button
            onClick={loadDashboard}
          >
            Try Again
          </button>

        </div>

      </div>
    );
  }


  if (!dashboard) {
    return null;
  }


  // ==========================================================
  // REVENUE CHART
  // ==========================================================

  const revenueLabels =
    dashboard.revenue_trends?.map(
      item => item.date
    ) || [];


  const revenueValues =
    dashboard.revenue_trends?.map(
      item => item.revenue
    ) || [];


  const revenueChartData = {

    labels: revenueLabels,

    datasets: [
      {
        label: "Revenue",

        data: revenueValues,

        tension: 0.3,

        borderWidth: 2,

        pointRadius: 4,

        fill: false,
      },
    ],

  };


  const revenueChartOptions = {

    responsive: true,

    maintainAspectRatio: false,

    plugins: {

      legend: {
        display: true,
      },

      title: {
        display: false,
      },

      tooltip: {
        callbacks: {
          label: function (
            context
          ) {

            return `Revenue: ₹${Number(
              context.raw
            ).toLocaleString("en-IN")}`;

          },
        },
      },

    },

    scales: {

      y: {
        beginAtZero: true,

        ticks: {
          callback: function (
            value
          ) {
            return `₹${Number(
              value
            ).toLocaleString("en-IN")}`;
          },
        },
      },

    },

  };


  // ==========================================================
  // TOP PRODUCTS CHART
  // ==========================================================

  const productLabels =
    dashboard.top_selling_products?.map(
      item => item.product_name
    ) || [];


  const productQuantities =
    dashboard.top_selling_products?.map(
      item => item.quantity_sold
    ) || [];


  const productChartData = {

    labels: productLabels,

    datasets: [
      {
        label: "Quantity Sold",

        data: productQuantities,

        borderWidth: 1,
      },
    ],

  };


  const productChartOptions = {

    responsive: true,

    maintainAspectRatio: false,

    plugins: {

      legend: {
        display: true,
      },

    },

    scales: {

      y: {
        beginAtZero: true,

        ticks: {
          precision: 0,
        },
      },

    },

  };


  // ==========================================================
  // RENDER
  // ==========================================================

  return (

    <div className="admin-dashboard">

      {/* ================================================== */}
      {/* HEADER */}
      {/* ================================================== */}

      <div className="dashboard-header">

        <div>

          <h1>
            Admin Dashboard
          </h1>

          <p>
            Sales, revenue and inventory overview
          </p>

        </div>

        <button
          className="refresh-button"
          onClick={loadDashboard}
        >
          Refresh
        </button>

      </div>


      {/* ================================================== */}
      {/* SUMMARY CARDS */}
      {/* ================================================== */}

      <div className="summary-grid">

        <div className="summary-card">

          <div className="summary-title">
            Total Sales
          </div>

          <div className="summary-value">
            {Number(
              dashboard.total_sales || 0
            ).toLocaleString("en-IN")}
          </div>

          <div className="summary-description">
            Paid orders
          </div>

        </div>


        <div className="summary-card">

          <div className="summary-title">
            Total Revenue
          </div>

          <div className="summary-value">

            ₹
            {Number(
              dashboard.total_revenue || 0
            ).toLocaleString(
              "en-IN",
              {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
              }
            )}

          </div>

          <div className="summary-description">
            Total paid revenue
          </div>

        </div>


        <div className="summary-card">

          <div className="summary-title">
            Top Products
          </div>

          <div className="summary-value">
            {dashboard
              .top_selling_products
              ?.length || 0}
          </div>

          <div className="summary-description">
            Products with sales
          </div>

        </div>


        <div className="summary-card warning-card">

          <div className="summary-title">
            Low Stock
          </div>

          <div className="summary-value">
            {dashboard
              .low_stock_products
              ?.length || 0}
          </div>

          <div className="summary-description">
            Products need attention
          </div>

        </div>

      </div>


      {/* ================================================== */}
      {/* REVENUE TREND */}
      {/* ================================================== */}

      <div className="dashboard-section">

        <div className="section-header">

          <div>

            <h2>
              Revenue Trends
            </h2>

            <p>
              Daily revenue from paid orders
            </p>

          </div>

        </div>


        <div className="chart-container">

          {revenueLabels.length > 0 ? (

            <Line
              data={revenueChartData}
              options={
                revenueChartOptions
              }
            />

          ) : (

            <div className="empty-chart">
              No revenue data available
            </div>

          )}

        </div>

      </div>


      {/* ================================================== */}
      {/* TWO COLUMN SECTION */}
      {/* ================================================== */}

      <div className="dashboard-columns">


        {/* ============================================== */}
        {/* TOP PRODUCTS */}
        {/* ============================================== */}

        <div className="dashboard-section">

          <div className="section-header">

            <div>

              <h2>
                Top-Selling Products
              </h2>

              <p>
                Best-performing products
              </p>

            </div>

          </div>


          <div className="chart-container">

            {productLabels.length > 0 ? (

              <Bar
                data={productChartData}
                options={
                  productChartOptions
                }
              />

            ) : (

              <div className="empty-chart">
                No product sales available
              </div>

            )}

          </div>

        </div>


        {/* ============================================== */}
        {/* LOW STOCK */}
        {/* ============================================== */}

        <div className="dashboard-section">

          <div className="section-header">

            <div>

              <h2>
                Low Stock Alerts
              </h2>

              <p>
                Products with 5 or fewer items
              </p>

            </div>

          </div>


          <div className="stock-list">

            {dashboard
              .low_stock_products
              ?.length > 0 ? (

              dashboard
                .low_stock_products
                .map(product => (

                  <div
                    className="stock-item"
                    key={product.product_id}
                  >

                    <div>

                      <div className="stock-name">
                        {product.product_name}
                      </div>

                      <div className="stock-id">
                        Product #
                        {product.product_id}
                      </div>

                    </div>


                    <div
                      className={
                        product.stock <= 2
                          ? "stock-danger"
                          : "stock-warning"
                      }
                    >
                      {product.stock} left
                    </div>

                  </div>

                ))

            ) : (

              <div className="no-stock-alert">
                No low-stock products.
              </div>

            )}

          </div>

        </div>

      </div>


      {/* ================================================== */}
      {/* REVENUE TABLE */}
      {/* ================================================== */}

      <div className="dashboard-section">

        <div className="section-header">

          <div>

            <h2>
              Revenue Details
            </h2>

            <p>
              Daily revenue summary
            </p>

          </div>

        </div>


        <div className="table-wrapper">

          <table>

            <thead>

              <tr>

                <th>
                  Date
                </th>

                <th>
                  Revenue
                </th>

              </tr>

            </thead>

            <tbody>

              {dashboard
                .revenue_trends
                ?.length > 0 ? (

                dashboard
                  .revenue_trends
                  .map(item => (

                    <tr key={item.date}>

                      <td>
                        {item.date}
                      </td>

                      <td>

                        ₹
                        {Number(
                          item.revenue
                        ).toLocaleString(
                          "en-IN",
                          {
                            minimumFractionDigits: 2,
                          }
                        )}

                      </td>

                    </tr>

                  ))

              ) : (

                <tr>

                  <td
                    colSpan="2"
                    className="empty-table"
                  >
                    No revenue records.
                  </td>

                </tr>

              )}

            </tbody>

          </table>

        </div>

      </div>


      {/* ================================================== */}
      {/* HOME BUTTON */}
      {/* ================================================== */}

      <div className="dashboard-home">

        <button
          className="home-button"
          onClick={() => navigate("/products")}
        >
          ← Back to Home
        </button>

      </div>

    </div>

  );
}