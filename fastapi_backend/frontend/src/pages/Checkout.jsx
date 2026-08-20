import { useEffect, useState } from "react";
import { apiFetch } from "../api";
import Navbar from "../components/Navbar";

function Checkout() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [checkoutData, setCheckoutData] = useState(null);

  useEffect(() => {
    startCheckout();
  }, []);

  async function startCheckout() {
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
        return;
      }

      setCheckoutData(data);

      // Redirect to Stripe checkout page
      if (data.checkout_url) {
        window.location.href = data.checkout_url;
      } else {
        setError("Checkout URL was not returned");
      }

    } catch (error) {
      console.error(error);
      setError("Cannot connect to backend");
    } finally {
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
            Preparing your checkout...
          </p>
        </section>

        {loading && (
          <div className="loading">
            Creating checkout session...
          </div>
        )}

        {error && (
          <div className="message error">
            {error}
          </div>
        )}

        {checkoutData && !error && (
          <div className="message">
            Checkout session created successfully.
          </div>
        )}

      </main>
    </div>
  );
}

export default Checkout;