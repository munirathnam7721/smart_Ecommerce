import { useEffect, useMemo, useState } from "react";
import { apiFetch } from "../api";
import Navbar from "../components/Navbar";

function Cart() {
  const [cart, setCart] = useState([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    loadCart();
  }, []);

  async function loadCart() {
    setLoading(true);
    setError("");

    try {
      const response =
        await apiFetch("/cart");

      const data =
        await response.json();

      if (!response.ok) {
        setError(
          data.detail ||
            "Failed to load cart"
        );
        return;
      }

      setCart(data);
    } catch {
      setError(
        "Cannot connect to backend"
      );
    } finally {
      setLoading(false);
    }
  }

  async function updateQuantity(
    itemId,
    quantity
  ) {
    if (quantity < 1) {
      return;
    }

    try {
      const response =
        await apiFetch(
          `/cart/${itemId}`,
          {
            method: "PUT",
            headers: {
              "Content-Type":
                "application/json",
            },
            body: JSON.stringify({
              quantity,
            }),
          }
        );

      const data =
        await response.json();

      if (!response.ok) {
        setError(
          data.detail ||
            "Failed to update cart"
        );
        return;
      }

      await loadCart();
    } catch {
      setError(
        "Cannot connect to backend"
      );
    }
  }

  async function removeItem(itemId) {
    try {
      const response =
        await apiFetch(
          `/cart/${itemId}`,
          {
            method: "DELETE",
          }
        );

      const data =
        await response.json();

      if (!response.ok) {
        setError(
          data.detail ||
            "Failed to remove item"
        );
        return;
      }

      setMessage(
        "Item removed from cart."
      );

      await loadCart();
    } catch {
      setError(
        "Cannot connect to backend"
      );
    }
  }

  const totalQuantity = useMemo(() => {
    return cart.reduce(
      (sum, item) =>
        sum + Number(item.quantity || 0),
      0
    );
  }, [cart]);

  const total = useMemo(() => {
    return cart.reduce(
      (sum, item) => {
        const price =
          Number(
            item.product?.price ??
              item.price ??
              0
          );

        return (
          sum +
          price *
            Number(item.quantity || 0)
        );
      },
      0
    );
  }, [cart]);

  return (
    <div className="page">
      <Navbar />

      <main className="container">
        <div className="hero">
          <h1>My Cart</h1>
        </div>

        {message && (
          <div className="message">
            {message}
          </div>
        )}

        {error && (
          <div className="message error">
            {error}
          </div>
        )}

        {loading ? (
          <div className="loading">
            Loading cart...
          </div>
        ) : cart.length === 0 ? (
          <div className="empty">
            <h2>
              Your cart is empty
            </h2>

            <p>
              Add some products to your cart.
            </p>
          </div>
        ) : (
          <div className="cart-layout">
            <section className="cart-items">
              {cart.map((item) => {
                const product =
                  item.product || {};

                const price = Number(
                  product.price ??
                    item.price ??
                    0
                );

                const quantity =
                  Number(
                    item.quantity || 0
                  );

                return (
                  <div
                    className="cart-item"
                    key={item.id}
                  >
                    <div>
                      <h3>
                        {product.name ||
                          `Product #${item.product_id}`}
                      </h3>

                      <p>
                        ₹{price}
                      </p>

                      <div className="quantity-control">
                        <button
                          onClick={() =>
                            updateQuantity(
                              item.id,
                              quantity - 1
                            )
                          }
                          disabled={
                            quantity <= 1
                          }
                        >
                          -
                        </button>

                        <strong>
                          {quantity}
                        </strong>

                        <button
                          onClick={() =>
                            updateQuantity(
                              item.id,
                              quantity + 1
                            )
                          }
                        >
                          +
                        </button>
                      </div>
                    </div>

                    <div>
                      <p>
                        ₹
                        {(
                          price *
                          quantity
                        ).toFixed(2)}
                      </p>

                      <button
                        className="danger-button"
                        onClick={() =>
                          removeItem(
                            item.id
                          )
                        }
                      >
                        Remove
                      </button>
                    </div>
                  </div>
                );
              })}
            </section>

            <aside className="cart-summary">
              <h2>
                Cart Summary
              </h2>

              <p>
                Items: {totalQuantity}
              </p>

              <hr />

              <p className="total">
                Total: ₹
                {total.toFixed(2)}
              </p>
            </aside>
          </div>
        )}
      </main>
    </div>
  );
}

export default Cart;