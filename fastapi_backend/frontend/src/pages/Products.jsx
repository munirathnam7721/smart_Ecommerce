import { useEffect, useMemo, useState } from "react";
import { apiFetch } from "../api";
import Navbar from "../components/Navbar";

function Products() {
  const [products, setProducts] = useState([]);
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("all");
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    loadProducts();
  }, []);

  async function loadProducts() {
    setLoading(true);
    setError("");

    try {
      const response = await apiFetch("/products");
      const data = await response.json();

      if (!response.ok) {
        setError(
          data.detail ||
            "Failed to load products"
        );
        return;
      }

      setProducts(data);
    } catch {
      setError(
        "Cannot connect to backend"
      );
    } finally {
      setLoading(false);
    }
  }

  async function addToCart(productId) {
    setMessage("");
    setError("");

    try {
      const response = await apiFetch(
        "/cart",
        {
          method: "POST",
          headers: {
            "Content-Type":
              "application/json",
          },
          body: JSON.stringify({
            product_id: productId,
            quantity: 1,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        setError(
          data.detail ||
            "Failed to add product"
        );
        return;
      }

      setMessage(
        "Product added to cart successfully."
      );
    } catch {
      setError(
        "Cannot connect to backend"
      );
    }
  }

  const categories = useMemo(() => {
    const values = products
      .map((product) => product.category)
      .filter(Boolean);

    return ["all", ...new Set(values)];
  }, [products]);

  const filteredProducts = useMemo(() => {
    return products.filter((product) => {
      const text =
        `${product.name || ""} ${
          product.description || ""
        }`.toLowerCase();

      const matchesSearch =
        text.includes(
          search.toLowerCase()
        );

      const matchesCategory =
        category === "all" ||
        product.category === category;

      return (
        matchesSearch &&
        matchesCategory
      );
    });
  }, [products, search, category]);

  return (
    <div className="page">
      <Navbar />

      <main className="container">
        <section className="hero">
          <h1>Products</h1>
          <p>
            Find the products you need.
          </p>
        </section>

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

        <div className="toolbar">
          <input
            className="search-input"
            type="search"
            placeholder="Search products..."
            value={search}
            onChange={(event) =>
              setSearch(event.target.value)
            }
          />

          <select
            className="select-input"
            value={category}
            onChange={(event) =>
              setCategory(event.target.value)
            }
          >
            {categories.map((item) => (
              <option
                key={item}
                value={item}
              >
                {item === "all"
                  ? "All Categories"
                  : item}
              </option>
            ))}
          </select>
        </div>

        {loading ? (
          <div className="loading">
            Loading products...
          </div>
        ) : filteredProducts.length === 0 ? (
          <div className="empty">
            <h3>
              No products found
            </h3>

            <p>
              Try another search or category.
            </p>
          </div>
        ) : (
          <div className="product-grid">
            {filteredProducts.map(
              (product) => (
                <article
                  className="product-card"
                  key={product.id}
                >
                  {product.image_url ? (
                    <img
                      className="product-image"
                      src={product.image_url}
                      alt={product.name}
                    />
                  ) : (
                    <div className="product-image-placeholder">
                      No Image
                    </div>
                  )}

                  <div className="product-content">
                    <h3>
                      {product.name}
                    </h3>

                    <p className="product-description">
                      {product.description ||
                        "No description available."}
                    </p>

                    <p className="price">
                      ₹{product.price}
                    </p>

                    <p className="stock">
                      {product.stock > 0
                        ? `${product.stock} available`
                        : "Out of stock"}
                    </p>

                    <button
                      className="primary-button"
                      disabled={
                        product.stock <= 0
                      }
                      onClick={() =>
                        addToCart(
                          product.id
                        )
                      }
                    >
                      {product.stock > 0
                        ? "Add to Cart"
                        : "Out of Stock"}
                    </button>
                  </div>
                </article>
              )
            )}
          </div>
        )}
      </main>
    </div>
  );
}

export default Products;