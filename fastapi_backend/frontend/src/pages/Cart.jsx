import {
  useEffect,
  useState,
} from "react";

import { apiFetch } from "../api";
import Navbar from "../components/Navbar";

function Cart() {
  const [cart, setCart] = useState({
    items: [],
    subtotal: 0,
    tax: 0,
    grand_total: 0,
  });

  const [loading, setLoading] =
    useState(true);

  const [message, setMessage] =
    useState("");

  const [error, setError] =
    useState("");

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

    } catch (error) {
      console.error(error);

      setError(
        "Cannot connect to backend"
      );

    } finally {
      setLoading(false);
    }
  }

  async function updateQuantity(
    cartId,
    quantity
  ) {
    if (quantity < 1) {
      return;
    }

    setError("");
    setMessage("");

    try {
      const response =
        await apiFetch(
          `/cart/update?cart_id=${cartId}`,
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

      setMessage(
        "Cart updated successfully."
      );

      await loadCart();

    } catch (error) {
      console.error(error);

      setError(
        "Cannot connect to backend"
      );
    }
  }

  async function removeItem(
    cartId
  ) {
    setError("");
    setMessage("");

    try {
      const response =
        await apiFetch(
          `/cart/remove?cart_id=${cartId}`,
          {
            method: "DELETE",
          }
        );

      if (!response.ok) {
        let data = {};

        try {
          data =
            await response.json();
        } catch {
          // No response body
        }

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

    } catch (error) {
      console.error(error);

      setError(
        "Cannot connect to backend"
      );
    }
  }

  const items =
    cart.items || [];

  const totalQuantity =
    items.reduce(
      (sum, item) =>
        sum +
        Number(
          item.quantity || 0
        ),
      0
    );

  return (
    <div className="page">

      <Navbar />

      <main className="container">

        <div className="hero">

          <h1>
            My Cart
          </h1>

          <p>
            Review your products before checkout.
          </p>

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

        ) : items.length === 0 ? (

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

              {items.map(
                (item) => {

                  const price =
                    Number(
                      item.price || 0
                    );

                  const quantity =
                    Number(
                      item.quantity || 0
                    );

                  const itemTotal =
                    Number(
                      item.item_total ||
                        price * quantity
                    );

                  return (

                    <div
                      className="cart-item"
                      key={item.id}
                    >

                      <div>

                        <h3>
                          {
                            item.product_name
                          }
                        </h3>

                        <p>
                          Price: ₹
                          {price.toFixed(2)}
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
                          {itemTotal.toFixed(
                            2
                          )}
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
                }
              )}

            </section>

            <aside className="cart-summary">

              <h2>
                Cart Summary
              </h2>

              <p>
                Items:{" "}
                {totalQuantity}
              </p>

              <p>
                Subtotal: ₹
                {Number(
                  cart.subtotal || 0
                ).toFixed(2)}
              </p>

              <p>
                Tax: ₹
                {Number(
                  cart.tax || 0
                ).toFixed(2)}
              </p>

              <hr />

              <p className="total">
                Total: ₹
                {Number(
                  cart.grand_total || 0
                ).toFixed(2)}
              </p>

            </aside>

          </div>

        )}

      </main>

    </div>
  );
}

export default Cart;