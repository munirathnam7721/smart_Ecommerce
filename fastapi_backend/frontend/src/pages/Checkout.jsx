import { useState } from "react";
import { apiFetch } from "../api";
import Navbar from "../components/Navbar";

function Checkout() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function startCheckout() {
    // Prevent multiple clicks
    if (loading) {
      return;
    }

    setLoading(true);
    setError("");

    try {
      const response = await apiFetch("/checkout", {
        method: "POST",
      });

      const data = await response.json();

      if (!response.ok) {
        setError(
          data.detail || "Failed to start checkout"
        );

        setLoading(false);
        return;
      }

      // Redirect to Stripe
      if (data.checkout_url) {
        window.location.href = data.checkout_url;
        return;
      }

      setError(
        "Checkout URL was not returned"
      );

    } catch (error) {
      console.error(error);

      setError(
        "Cannot connect to backend"
      );

      setLoading(false);
    }
  }

  return (
    <div className="page">

      <Navbar />

      <main className="container">

        <section className="hero">

          <h1>Checkout</h1>

          <p>
            Review your cart and continue to payment.
          </p>

        </section>

        {error && (
          <div className="message error">
            {error}
          </div>
        )}

        <div className="checkout-card">

          <button
            className="primary-button"
            onClick={startCheckout}
            disabled={loading}
          >
            {loading
              ? "Creating checkout..."
              : "Proceed to Payment"}
          </button>

        </div>

      </main>

    </div>
  );
}

export default Checkout;