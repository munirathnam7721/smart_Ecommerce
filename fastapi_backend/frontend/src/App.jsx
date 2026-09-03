import {
  BrowserRouter,
  Routes,
  Route,
} from "react-router-dom";

import Login from "./pages/Login";
import Register from "./pages/Register";
import Products from "./pages/Products";
import Cart from "./pages/Cart";
import Checkout from "./pages/Checkout";
import Profile from "./pages/Profile";

import PaymentSuccess from "./pages/PaymentSuccess";

import Orders from "./pages/Orders";
import OrderDetails from "./pages/OrderDetails";

import Notifications from "./pages/Notifications";

import AdminDashboard from "./pages/AdminDashboard";
import AdminProducts from "./pages/AdminProducts";
import AdminOrders from "./pages/AdminOrders";
import AdminReports from "./pages/AdminReports";

import ProtectedRoute from "./ProtectedRoute";


function App() {

  return (

    <BrowserRouter>

      <Routes>

        {/* =====================================================
            LOGIN
        ===================================================== */}

        <Route
          path="/"
          element={<Login />}
        />


        {/* =====================================================
            REGISTER
        ===================================================== */}

        <Route
          path="/register"
          element={<Register />}
        />


        {/* =====================================================
            CUSTOMER PRODUCTS
        ===================================================== */}

        <Route
          path="/products"
          element={
            <ProtectedRoute>
              <Products />
            </ProtectedRoute>
          }
        />


        {/* =====================================================
            CUSTOMER CART
        ===================================================== */}

        <Route
          path="/cart"
          element={
            <ProtectedRoute>
              <Cart />
            </ProtectedRoute>
          }
        />


        {/* =====================================================
            CHECKOUT
        ===================================================== */}

        <Route
          path="/checkout"
          element={
            <ProtectedRoute>
              <Checkout />
            </ProtectedRoute>
          }
        />


        {/* =====================================================
            PAYMENT SUCCESS
        ===================================================== */}

        <Route
          path="/payment/success"
          element={
            <ProtectedRoute>
              <PaymentSuccess />
            </ProtectedRoute>
          }
        />


        {/* =====================================================
            CUSTOMER ORDERS
        ===================================================== */}

        <Route
          path="/orders"
          element={
            <ProtectedRoute>
              <Orders />
            </ProtectedRoute>
          }
        />


        {/* =====================================================
            CUSTOMER ORDER DETAILS
        ===================================================== */}

        <Route
          path="/orders/:order_id"
          element={
            <ProtectedRoute>
              <OrderDetails />
            </ProtectedRoute>
          }
        />


        {/* =====================================================
            CUSTOMER NOTIFICATIONS
        ===================================================== */}

        <Route
          path="/notifications"
          element={
            <ProtectedRoute>
              <Notifications />
            </ProtectedRoute>
          }
        />


        {/* =====================================================
            CUSTOMER PROFILE
        ===================================================== */}

        <Route
          path="/profile"
          element={
            <ProtectedRoute>
              <Profile />
            </ProtectedRoute>
          }
        />


        {/* =====================================================
            ADMIN DASHBOARD
        ===================================================== */}

        <Route
          path="/admin/dashboard"
          element={
            <ProtectedRoute>
              <AdminDashboard />
            </ProtectedRoute>
          }
        />


        {/* =====================================================
            ADMIN PRODUCTS
        ===================================================== */}

        <Route
          path="/admin/products"
          element={
            <ProtectedRoute>
              <AdminProducts />
            </ProtectedRoute>
          }
        />


        {/* =====================================================
            ADMIN ORDERS
        ===================================================== */}

        <Route
          path="/admin/orders"
          element={
            <ProtectedRoute>
              <AdminOrders />
            </ProtectedRoute>
          }
        />


        {/* =====================================================
            ADMIN REPORTS
        ===================================================== */}

        <Route
          path="/admin/reports"
          element={
            <ProtectedRoute>
              <AdminReports />
            </ProtectedRoute>
          }
        />

      </Routes>

    </BrowserRouter>
  );
}


export default App;