import { useEffect, useState } from "react";
import Navbar from "../components/Navbar";
import { apiFetch, getCurrentUser } from "../api";

function AdminProducts() {
  const user = getCurrentUser();

  const [products, setProducts] =
    useState([]);

  const [loading, setLoading] =
    useState(true);

  const [message, setMessage] =
    useState("");

  const [error, setError] =
    useState("");

  const [editingId, setEditingId] =
    useState(null);

  const [form, setForm] = useState({
    name: "",
    description: "",
    price: "",
    stock: "",
    category: "",
    image_url: "",
  });

  useEffect(() => {
    if (user?.role === "admin") {
      loadProducts();
    }
  }, []);

  function handleChange(event) {
    const {
      name,
      value,
    } = event.target;

    setForm((current) => ({
      ...current,
      [name]: value,
    }));
  }

  async function loadProducts() {
    setLoading(true);

    try {
      const response =
        await apiFetch("/products");

      const data =
        await response.json();

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

  function resetForm() {
    setForm({
      name: "",
      description: "",
      price: "",
      stock: "",
      category: "",
      image_url: "",
    });

    setEditingId(null);
  }

  function editProduct(product) {
    setEditingId(product.id);

    setForm({
      name: product.name || "",
      description:
        product.description || "",
      price: product.price || "",
      stock: product.stock || "",
      category:
        product.category || "",
      image_url:
        product.image_url || "",
    });

    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  }

  async function saveProduct(event) {
    event.preventDefault();

    setMessage("");
    setError("");

    const body = {
      name: form.name,
      description: form.description,
      price: Number(form.price),
      stock: Number(form.stock),
      category: form.category,
      image_url: form.image_url,
    };

    try {
      const endpoint = editingId
        ? `/products/${editingId}`
        : "/products";

      const method = editingId
        ? "PUT"
        : "POST";

      const response =
        await apiFetch(endpoint, {
          method,
          headers: {
            "Content-Type":
              "application/json",
          },
          body: JSON.stringify(body),
        });

      const data =
        await response.json();

      if (!response.ok) {
        setError(
          data.detail ||
            "Failed to save product"
        );
        return;
      }

      setMessage(
        editingId
          ? "Product updated successfully."
          : "Product created successfully."
      );

      resetForm();
      await loadProducts();
    } catch {
      setError(
        "Cannot connect to backend"
      );
    }
  }

  async function deleteProduct(
    productId
  ) {
    const confirmed =
      window.confirm(
        "Delete this product?"
      );

    if (!confirmed) {
      return;
    }

    try {
      const response =
        await apiFetch(
          `/products/${productId}`,
          {
            method: "DELETE",
          }
        );

      const data =
        await response.json();

      if (!response.ok) {
        setError(
          data.detail ||
            "Failed to delete product"
        );
        return;
      }

      setMessage(
        "Product deleted successfully."
      );

      await loadProducts();
    } catch {
      setError(
        "Cannot connect to backend"
      );
    }
  }

  if (user?.role !== "admin") {
    return (
      <div className="page">
        <Navbar />

        <main className="container">
          <div className="empty">
            <h2>
              Access denied
            </h2>

            <p>
              Administrator access is required.
            </p>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="page">
      <Navbar />

      <main className="container">
        <div className="hero">
          <h1>
            Product Management
          </h1>

          <p>
            Create, edit and delete products.
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

        <form
          className="admin-form"
          onSubmit={saveProduct}
        >
          <h2>
            {editingId
              ? "Edit Product"
              : "Add Product"}
          </h2>

          <div className="form-group">
            <label>
              Name
            </label>

            <input
              name="name"
              value={form.name}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label>
              Description
            </label>

            <textarea
              name="description"
              value={form.description}
              onChange={handleChange}
            />
          </div>

          <div className="form-group">
            <label>
              Price
            </label>

            <input
              type="number"
              step="0.01"
              min="0"
              name="price"
              value={form.price}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label>
              Stock
            </label>

            <input
              type="number"
              min="0"
              name="stock"
              value={form.stock}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label>
              Category
            </label>

            <input
              name="category"
              value={form.category}
              onChange={handleChange}
            />
          </div>

          <div className="form-group">
            <label>
              Image URL
            </label>

            <input
              name="image_url"
              value={form.image_url}
              onChange={handleChange}
            />
          </div>

          <div className="admin-actions">
            <button
              className="primary-button"
              type="submit"
            >
              {editingId
                ? "Update Product"
                : "Create Product"}
            </button>

            {editingId && (
              <button
                type="button"
                className="secondary-button"
                onClick={resetForm}
              >
                Cancel
              </button>
            )}
          </div>
        </form>

        {loading ? (
          <div className="loading">
            Loading products...
          </div>
        ) : (
          <div
            style={{
              overflowX: "auto",
            }}
          >
            <table className="admin-table">
              <thead>
                <tr>
                  <th>
                    Name
                  </th>

                  <th>
                    Price
                  </th>

                  <th>
                    Stock
                  </th>

                  <th>
                    Category
                  </th>

                  <th>
                    Actions
                  </th>
                </tr>
              </thead>

              <tbody>
                {products.map(
                  (product) => (
                    <tr
                      key={product.id}
                    >
                      <td>
                        {product.name}
                      </td>

                      <td>
                        ₹{product.price}
                      </td>

                      <td>
                        {product.stock}
                      </td>

                      <td>
                        {product.category ||
                          "-"}
                      </td>

                      <td>
                        <div className="admin-actions">
                          <button
                            className="secondary-button"
                            onClick={() =>
                              editProduct(
                                product
                              )
                            }
                          >
                            Edit
                          </button>

                          <button
                            className="danger-button"
                            onClick={() =>
                              deleteProduct(
                                product.id
                              )
                            }
                          >
                            Delete
                          </button>
                        </div>
                      </td>
                    </tr>
                  )
                )}
              </tbody>
            </table>
          </div>
        )}
      </main>
    </div>
  );
}

export default AdminProducts;