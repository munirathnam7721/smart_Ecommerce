import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";

import { apiFetch } from "../api";
import Navbar from "../components/Navbar";


function PaymentSuccess() {

  const [searchParams] = useSearchParams();

  const sessionId =
    searchParams.get("session_id");


  const [loading, setLoading] =
    useState(true);

  const [success, setSuccess] =
    useState(false);

  const [error, setError] =
    useState("");

  const [paymentData, setPaymentData] =
    useState(null);


  // ==========================================================
  // VERIFY PAYMENT WHEN PAGE LOADS
  // ==========================================================

  useEffect(() => {

    verifyPayment();

  }, [sessionId]);


  // ==========================================================
  // VERIFY PAYMENT
  // ==========================================================

  async function verifyPayment() {

    setLoading(true);
    setError("");
    setSuccess(false);


    // --------------------------------------------------------
    // Session ID validation
    // --------------------------------------------------------

    if (!sessionId) {

      setError(
        "Stripe session ID is missing."
      );

      setLoading(false);

      return;
    }


    // --------------------------------------------------------
    // Call backend
    // --------------------------------------------------------

    try {

      const response = await apiFetch(
        `/payment/verify?session_id=${encodeURIComponent(
          sessionId
        )}`
      );


      const data = await response.json();


      console.log(
        "Payment verification response:",
        data
      );


      // ------------------------------------------------------
      // Backend error
      // ------------------------------------------------------

      if (!response.ok) {

        setError(
          data.detail ||
          "Payment verification failed."
        );

        return;
      }


      // ------------------------------------------------------
      // Payment not completed
      // ------------------------------------------------------

      if (!data.success) {

        setError(
          data.message ||
          "Payment has not been completed."
        );

        return;
      }


      // ------------------------------------------------------
      // Payment verified
      // ------------------------------------------------------

      setPaymentData(data);

      setSuccess(true);


    } catch (err) {

      console.error(
        "Payment verification error:",
        err
      );


      setError(
        "Cannot connect to payment verification server."
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
      <div className="page">

        <Navbar />

        <main className="container">

          <div className="hero">

            <h1>
              Verifying Payment...
            </h1>

            <p>
              Please wait while we confirm your
              payment with Stripe.
            </p>

          </div>


          <div className="empty">

            <p>
              Do not close this page.
            </p>

          </div>

        </main>

      </div>
    );
  }


  // ==========================================================
  // PAYMENT VERIFICATION FAILED
  // ==========================================================

  if (!success) {

    return (
      <div className="page">

        <Navbar />

        <main className="container">

          <div className="hero">

            <h1>
              Payment Verification Failed
            </h1>

            <p>
              {error || "Unable to verify payment."}
            </p>

          </div>


          <div className="empty">

            <p>
              Your payment may have completed at
              Stripe, but we could not confirm it
              with our server.
            </p>


            {sessionId && (
              <p>

                Stripe Session ID:

                <br />

                <strong>
                  {sessionId}
                </strong>

              </p>
            )}


            <div
              style={{
                display: "flex",
                justifyContent: "center",
                gap: "12px",
                marginTop: "20px",
              }}
            >

              <button
                type="button"
                onClick={verifyPayment}
                className="primary-button"
              >
                Try Verification Again
              </button>


              <Link
                to="/orders"
                className="primary-button"
              >
                View My Orders
              </Link>

            </div>

          </div>

        </main>

      </div>
    );
  }


  // ==========================================================
  // PAYMENT SUCCESS
  // ==========================================================

  return (
    <div className="page">

      <Navbar />

      <main className="container">

        <div className="hero">

          <h1>
            Payment Successful 🎉
          </h1>

          <p>
            Your payment has been verified successfully.
          </p>

        </div>


        <div className="empty">

          <h2>
            Thank you for your order!
          </h2>


          <p>
            Your order has been successfully paid.
          </p>


          {/* ORDER ID */}

          {paymentData?.order_id && (

            <p>

              Order ID:

              <br />

              <strong>
                #{paymentData.order_id}
              </strong>

            </p>

          )}


          {/* PAYMENT STATUS */}

          <p>

            Payment Status:

            <br />

            <strong>
              {paymentData?.payment_status || "paid"}
            </strong>

          </p>


          {/* ORDER STATUS */}

          <p>

            Order Status:

            <br />

            <strong>
              {paymentData?.order_status || "paid"}
            </strong>

          </p>


          {/* TRANSACTION ID */}

          {paymentData?.transaction_id && (

            <p>

              Transaction ID:

              <br />

              <strong>
                {paymentData.transaction_id}
              </strong>

            </p>

          )}


          <br />


          <div
            style={{
              display: "flex",
              justifyContent: "center",
              gap: "12px",
              flexWrap: "wrap",
            }}
          >

            <Link
              to="/orders"
              className="primary-button"
            >
              View My Orders
            </Link>


            <Link
              to="/products"
              className="secondary-button"
            >
              Continue Shopping
            </Link>

          </div>

        </div>

      </main>

    </div>
  );
}


export default PaymentSuccess;