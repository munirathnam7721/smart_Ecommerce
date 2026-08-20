import { Link, useSearchParams } from "react-router-dom";
import Navbar from "../components/Navbar";

function PaymentSuccess() {
  const [searchParams] = useSearchParams();

  const sessionId = searchParams.get("session_id");

  return (
    <div className="page">
      <Navbar />

      <main className="container">
        <div className="hero">
          <h1>Payment Successful 🎉</h1>

          <p>
            Your payment has been completed successfully.
          </p>
        </div>

        <div className="empty">
          <h2>Thank you for your order!</h2>

          <p>
            Your order has been placed successfully.
          </p>

          {sessionId && (
            <p>
              Payment Session ID:
              <br />
              <strong>{sessionId}</strong>
            </p>
          )}

          <br />

          <Link to="/products">
            <button>
              Continue Shopping
            </button>
          </Link>
        </div>
      </main>
    </div>
  );
}

export default PaymentSuccess;