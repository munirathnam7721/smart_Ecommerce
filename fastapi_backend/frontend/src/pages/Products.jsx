import { useEffect, useMemo, useState } from "react";
import { apiFetch } from "../api";
import Navbar from "../components/Navbar";

function Products() {
  const [products, setProducts] = useState([]);

  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("all");

  const [minPrice, setMinPrice] = useState("");
  const [maxPrice, setMaxPrice] = useState("");

  const [popularity, setPopularity] = useState("all");
  const [stockFilter, setStockFilter] = useState("all");

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
        setError(data.detail || "Failed to load products");
        return;
      }

      setProducts(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error(err);
      setError("Cannot connect to backend");
    } finally {
      setLoading(false);
    }
  }

  // ---------------------------------------------------------
  // ADD PRODUCT TO CART
  // ---------------------------------------------------------

  async function addToCart(productId) {
    setMessage("");
    setError("");

    try {
      const response = await apiFetch("/cart/add", {
        method: "POST",

        headers: {
          "Content-Type": "application/json",
        },

        body: JSON.stringify({
          product_id: productId,
          quantity: 1,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        setError(
          data.detail || "Failed to add product to cart"
        );
        return;
      }

      setMessage(
        "Product added to cart successfully."
      );
    } catch (err) {
      console.error(err);
      setError("Cannot connect to backend");
    }
  }

  // ---------------------------------------------------------
  // CATEGORIES
  // ---------------------------------------------------------

  const categories = useMemo(() => {
    const values = products
      .map((product) => product.category)
      .filter(Boolean);

    return ["all", ...new Set(values)];
  }, [products]);

  // ---------------------------------------------------------
  // PRODUCT IMAGE
  // ---------------------------------------------------------

  function getProductImage(product) {
    if (!product || !product.images) {
      return null;
    }

    if (Array.isArray(product.images)) {
      return product.images.length > 0
        ? product.images[0]
        : null;
    }

    if (typeof product.images === "string") {
      return product.images.trim() || null;
    }

    return null;
  }

  // ---------------------------------------------------------
  // FILTER PRODUCTS
  // ---------------------------------------------------------

  const filteredProducts = useMemo(() => {
    let result = [...products];

    // Search filter
    result = result.filter((product) => {
      const text = `
        ${product.name || ""}
        ${product.description || ""}
        ${product.category || ""}
      `.toLowerCase();

      return text.includes(search.toLowerCase());
    });

    // Category filter
    if (category !== "all") {
      result = result.filter(
        (product) =>
          product.category === category
      );
    }

    // Minimum price
    if (minPrice !== "") {
      result = result.filter(
        (product) =>
          Number(product.price || 0) >=
          Number(minPrice)
      );
    }

    // Maximum price
    if (maxPrice !== "") {
      result = result.filter(
        (product) =>
          Number(product.price || 0) <=
          Number(maxPrice)
      );
    }

    // Popularity filter
    if (popularity === "high") {
      result = result.filter(
        (product) =>
          Number(product.popularity || 0) >= 50
      );
    }

    if (popularity === "medium") {
      result = result.filter((product) => {
        const value = Number(
          product.popularity || 0
        );

        return value >= 20 && value < 50;
      });
    }

    if (popularity === "low") {
      result = result.filter(
        (product) =>
          Number(product.popularity || 0) < 20
      );
    }

    // Stock filter
    if (stockFilter === "in_stock") {
      result = result.filter(
        (product) =>
          Number(product.stock || 0) > 0
      );
    }

    if (stockFilter === "out_of_stock") {
      result = result.filter(
        (product) =>
          Number(product.stock || 0) <= 0
      );
    }

    return result;
  }, [
    products,
    search,
    category,
    minPrice,
    maxPrice,
    popularity,
    stockFilter,
  ]);

  // ---------------------------------------------------------
  // CLEAR FILTERS
  // ---------------------------------------------------------

  function clearFilters() {
    setSearch("");
    setCategory("all");
    setMinPrice("");
    setMaxPrice("");
    setPopularity("all");
    setStockFilter("all");
  }

  // ---------------------------------------------------------
  // UI
  // ---------------------------------------------------------

  return (
    <div className="page">

      <Navbar />

      <main className="container">

        {/* Header */}
        <section className="hero">

          <h1>Products</h1>

          <p>
            Find the products you need.
          </p>

        </section>

        {/* Success message */}
        {message && (
          <div className="message">
            {message}
          </div>
        )}

        {/* Error message */}
        {error && (
          <div className="message error">
            {error}
          </div>
        )}

        {/* Filters */}
        <div className="toolbar">

          {/* Search */}
          <input
            className="search-input"
            type="search"
            placeholder="Search products..."
            value={search}
            onChange={(event) =>
              setSearch(event.target.value)
            }
          />

          {/* Category */}
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

          {/* Minimum price */}
          <input
            className="search-input"
            type="number"
            min="0"
            placeholder="Min price"
            value={minPrice}
            onChange={(event) =>
              setMinPrice(event.target.value)
            }
          />

          {/* Maximum price */}
          <input
            className="search-input"
            type="number"
            min="0"
            placeholder="Max price"
            value={maxPrice}
            onChange={(event) =>
              setMaxPrice(event.target.value)
            }
          />

          {/* Popularity */}
          <select
            className="select-input"
            value={popularity}
            onChange={(event) =>
              setPopularity(event.target.value)
            }
          >
            <option value="all">
              All Popularity
            </option>

            <option value="high">
              Highly Popular
            </option>

            <option value="medium">
              Medium Popularity
            </option>

            <option value="low">
              Low Popularity
            </option>
          </select>

          {/* Stock */}
          <select
            className="select-input"
            value={stockFilter}
            onChange={(event) =>
              setStockFilter(event.target.value)
            }
          >
            <option value="all">
              All Stock
            </option>

            <option value="in_stock">
              In Stock
            </option>

            <option value="out_of_stock">
              Out of Stock
            </option>
          </select>

          {/* Clear */}
          <button
            className="secondary-button"
            onClick={clearFilters}
          >
            Clear Filters
          </button>

        </div>

        {/* Product count */}
        {!loading && (
          <div className="product-count">

            Showing {filteredProducts.length} product
            {filteredProducts.length !== 1
              ? "s"
              : ""}

          </div>
        )}

        {/* Loading */}
        {loading ? (

          <div className="loading">
            Loading products...
          </div>

        ) : filteredProducts.length === 0 ? (

          /* Empty */

          <div className="empty">

            <h3>
              No products found
            </h3>

            <p>
              Try another search or change your
              filters.
            </p>

            <button
              className="secondary-button"
              onClick={clearFilters}
            >
              Clear Filters
            </button>

          </div>

        ) : (

          /* Products */

          <div className="product-grid">

            {filteredProducts.map((product) => {

              const imageUrl =
                getProductImage(product);

              const price = Number(
                product.price || 0
              );

              const stock = Number(
                product.stock || 0
              );

              const productPopularity =
                Number(
                  product.popularity || 0
                );

              return (

                <article
                  className="product-card"
                  key={product.id}
                >

                  {/* Product Image */}

                  <div className="product-image-wrapper">

                    {imageUrl ? (

                      <img
                        className="product-image"
                        src={imageUrl}
                        alt={
                          product.name ||
                          "Product"
                        }
                        onError={(event) => {

                          event.currentTarget.style.display =
                            "none";

                          const placeholder =
                            event.currentTarget
                              .parentElement
                              .querySelector(
                                ".product-image-error"
                              );

                          if (placeholder) {
                            placeholder.style.display =
                              "flex";
                          }

                        }}
                      />

                    ) : null}

                    <div
                      className="product-image-placeholder product-image-error"
                      style={{
                        display: imageUrl
                          ? "none"
                          : "flex",
                      }}
                    >
                      No Image
                    </div>

                  </div>

                  {/* Product Content */}

                  <div className="product-content">

                    <h3>
                      {product.name ||
                        "Unnamed Product"}
                    </h3>

                    <p className="product-description">
                      {product.description ||
                        "No description available."}
                    </p>

                    {/* Category */}

                    {product.category && (

                      <p className="product-category">

                        Category:{" "}

                        {product.category}

                      </p>

                    )}

                    {/* Price */}

                    <p className="price">
                      ₹{price.toFixed(2)}
                    </p>

                    {/* Popularity */}

                    <p className="popularity">

                      Popularity:{" "}

                      {productPopularity}

                    </p>

                    {/* Stock */}

                    <p className="stock">

                      {stock > 0
                        ? `${stock} available`
                        : "Out of stock"}

                    </p>

                    {/* Add to Cart */}

                    <button
                      className="primary-button"
                      disabled={stock <= 0}
                      onClick={() =>
                        addToCart(product.id)
                      }
                    >

                      {stock > 0
                        ? "Add to Cart"
                        : "Out of Stock"}

                    </button>

                  </div>

                </article>

              );
            })}

          </div>

        )}

      </main>

    </div>
  );
}

export default Products;