import React, { useEffect, useState } from "react";

import {
  getAdminProducts,
  createAdminProduct,
  updateAdminProduct,
  deleteAdminProduct,
  updateAdminProductStock,
  uploadAdminProductImage,
} from "../adminApi";

// ============================================================
// CONSTANTS
// ============================================================

const EMPTY_FORM = {
  name: "",
  description: "",
  category: "",
  price: "",
  stock: "0",
};

// ============================================================
// INLINE STYLES
// ============================================================

const styles = {
  page: {
    width: "100%",
    maxWidth: "1400px",
    margin: "0 auto",
    padding: "30px",
    boxSizing: "border-box",
    fontFamily:
      '-apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif',
    color: "#1f2937",
    backgroundColor: "#f8fafc",
    minHeight: "100vh",
  },

  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    gap: "20px",
    marginBottom: "25px",
    flexWrap: "wrap",
  },

  headerTitle: {
    margin: "0 0 6px",
    fontSize: "28px",
    fontWeight: "700",
    color: "#111827",
  },

  headerText: {
    margin: 0,
    color: "#6b7280",
    fontSize: "14px",
  },

  refreshButton: {
    border: "none",
    backgroundColor: "#111827",
    color: "#ffffff",
    padding: "10px 18px",
    borderRadius: "7px",
    cursor: "pointer",
    fontSize: "14px",
    fontWeight: "600",
  },

  card: {
    backgroundColor: "#ffffff",
    border: "1px solid #e5e7eb",
    borderRadius: "12px",
    marginBottom: "25px",
    overflow: "hidden",
    boxShadow: "0 2px 8px rgba(0, 0, 0, 0.04)",
  },

  cardTitle: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    gap: "15px",
    padding: "22px 24px",
    borderBottom: "1px solid #e5e7eb",
    flexWrap: "wrap",
  },

  cardHeading: {
    margin: "0 0 5px",
    fontSize: "20px",
    fontWeight: "700",
    color: "#111827",
  },

  cardDescription: {
    margin: 0,
    color: "#6b7280",
    fontSize: "13px",
  },

  form: {
    display: "grid",
    gridTemplateColumns: "repeat(2, minmax(0, 1fr))",
    gap: "20px",
    padding: "24px",
  },

  formGroup: {
    display: "flex",
    flexDirection: "column",
    gap: "7px",
  },

  formGroupFull: {
    gridColumn: "1 / -1",
    display: "flex",
    flexDirection: "column",
    gap: "7px",
  },

  label: {
    fontSize: "13px",
    fontWeight: "600",
    color: "#374151",
  },

  input: {
    width: "100%",
    boxSizing: "border-box",
    padding: "11px 13px",
    border: "1px solid #d1d5db",
    borderRadius: "7px",
    outline: "none",
    fontSize: "14px",
    backgroundColor: "#ffffff",
    color: "#111827",
  },

  textarea: {
    width: "100%",
    boxSizing: "border-box",
    padding: "11px 13px",
    border: "1px solid #d1d5db",
    borderRadius: "7px",
    outline: "none",
    fontSize: "14px",
    backgroundColor: "#ffffff",
    color: "#111827",
    resize: "vertical",
    minHeight: "100px",
    fontFamily: "inherit",
  },

  select: {
    width: "100%",
    boxSizing: "border-box",
    padding: "11px 13px",
    border: "1px solid #d1d5db",
    borderRadius: "7px",
    outline: "none",
    fontSize: "14px",
    backgroundColor: "#ffffff",
    color: "#111827",
  },

  fileInput: {
    width: "100%",
    boxSizing: "border-box",
    padding: "9px",
    border: "1px dashed #cbd5e1",
    borderRadius: "7px",
    backgroundColor: "#f8fafc",
    fontSize: "13px",
  },

  smallText: {
    fontSize: "12px",
    color: "#6b7280",
  },

  selectedImage: {
    fontSize: "13px",
    color: "#374151",
    marginTop: "3px",
  },

  formActions: {
    gridColumn: "1 / -1",
    display: "flex",
    alignItems: "center",
    gap: "10px",
    marginTop: "5px",
  },

  primaryButton: {
    border: "none",
    backgroundColor: "#2563eb",
    color: "#ffffff",
    padding: "11px 20px",
    borderRadius: "7px",
    cursor: "pointer",
    fontSize: "14px",
    fontWeight: "600",
  },

  secondaryButton: {
    border: "1px solid #d1d5db",
    backgroundColor: "#ffffff",
    color: "#374151",
    padding: "10px 18px",
    borderRadius: "7px",
    cursor: "pointer",
    fontSize: "14px",
    fontWeight: "600",
  },

  cancelButton: {
    border: "1px solid #d1d5db",
    backgroundColor: "#ffffff",
    color: "#374151",
    padding: "9px 15px",
    borderRadius: "7px",
    cursor: "pointer",
    fontSize: "13px",
    fontWeight: "600",
  },

  alert: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    gap: "15px",
    padding: "12px 15px",
    marginBottom: "20px",
    borderRadius: "8px",
    fontSize: "14px",
  },

  alertError: {
    backgroundColor: "#fef2f2",
    border: "1px solid #fecaca",
    color: "#b91c1c",
  },

  alertSuccess: {
    backgroundColor: "#f0fdf4",
    border: "1px solid #bbf7d0",
    color: "#15803d",
  },

  alertClose: {
    border: "none",
    background: "transparent",
    fontSize: "20px",
    cursor: "pointer",
    color: "inherit",
    lineHeight: 1,
  },

  tableWrapper: {
    width: "100%",
    overflowX: "auto",
  },

  table: {
    width: "100%",
    borderCollapse: "collapse",
    minWidth: "950px",
  },

  th: {
    textAlign: "left",
    padding: "13px 16px",
    backgroundColor: "#f8fafc",
    borderBottom: "1px solid #e5e7eb",
    color: "#475569",
    fontSize: "12px",
    fontWeight: "700",
    textTransform: "uppercase",
    whiteSpace: "nowrap",
  },

  td: {
    padding: "14px 16px",
    borderBottom: "1px solid #f1f5f9",
    verticalAlign: "middle",
    fontSize: "14px",
    color: "#374151",
  },

  productNameCell: {
    display: "flex",
    flexDirection: "column",
    gap: "4px",
    maxWidth: "240px",
  },

  productName: {
    fontSize: "14px",
    fontWeight: "600",
    color: "#111827",
    wordBreak: "break-word",
  },

  productDescription: {
    fontSize: "12px",
    color: "#6b7280",
    lineHeight: "1.4",
    display: "block",
    overflow: "hidden",
    textOverflow: "ellipsis",
    whiteSpace: "nowrap",
  },

  categoryBadge: {
    display: "inline-block",
    padding: "5px 9px",
    borderRadius: "20px",
    backgroundColor: "#eff6ff",
    color: "#1d4ed8",
    fontSize: "12px",
    fontWeight: "600",
    whiteSpace: "nowrap",
  },

  stockBadge: {
    display: "inline-block",
    minWidth: "32px",
    textAlign: "center",
    padding: "5px 9px",
    borderRadius: "20px",
    fontSize: "12px",
    fontWeight: "700",
  },

  stockLow: {
    backgroundColor: "#fef2f2",
    color: "#dc2626",
  },

  stockGood: {
    backgroundColor: "#f0fdf4",
    color: "#16a34a",
  },

  // ==========================================================
  // SMALL PRODUCT IMAGE
  // ==========================================================

  imageAction: {
    display: "flex",
    alignItems: "center",
    gap: "10px",
    minWidth: "130px",
  },

  productThumbnail: {
    width: "60px",
    height: "60px",
    minWidth: "60px",
    maxWidth: "60px",
    minHeight: "60px",
    maxHeight: "60px",
    objectFit: "cover",
    objectPosition: "center",
    borderRadius: "8px",
    border: "1px solid #e5e7eb",
    backgroundColor: "#f8fafc",
    display: "block",
  },

  noImage: {
    width: "60px",
    height: "60px",
    minWidth: "60px",
    borderRadius: "8px",
    border: "1px solid #e5e7eb",
    backgroundColor: "#f8fafc",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    textAlign: "center",
    fontSize: "10px",
    color: "#9ca3af",
  },

  uploadButton: {
    display: "inline-flex",
    alignItems: "center",
    justifyContent: "center",
    padding: "7px 10px",
    borderRadius: "6px",
    backgroundColor: "#f1f5f9",
    color: "#334155",
    border: "1px solid #cbd5e1",
    fontSize: "12px",
    fontWeight: "600",
    cursor: "pointer",
    whiteSpace: "nowrap",
  },

  actionButtons: {
    display: "flex",
    alignItems: "center",
    gap: "7px",
    flexWrap: "wrap",
  },

  actionButton: {
    border: "none",
    padding: "7px 10px",
    borderRadius: "6px",
    cursor: "pointer",
    fontSize: "12px",
    fontWeight: "600",
    whiteSpace: "nowrap",
  },

  editButton: {
    backgroundColor: "#eff6ff",
    color: "#2563eb",
  },

  stockButton: {
    backgroundColor: "#fefce8",
    color: "#ca8a04",
  },

  deleteButton: {
    backgroundColor: "#fef2f2",
    color: "#dc2626",
  },

  emptyState: {
    padding: "60px 20px",
    textAlign: "center",
    color: "#6b7280",
  },

  emptyHeading: {
    margin: "0 0 8px",
    color: "#374151",
    fontSize: "18px",
  },

  emptyText: {
    margin: 0,
    fontSize: "14px",
  },
};

// ============================================================
// ADMIN PRODUCTS
// ============================================================

export default function AdminProducts() {
  const [products, setProducts] = useState([]);

  const [formData, setFormData] = useState(EMPTY_FORM);

  const [editingProductId, setEditingProductId] =
    useState(null);

  const [selectedImage, setSelectedImage] =
    useState(null);

  const [loading, setLoading] =
    useState(false);

  const [saving, setSaving] =
    useState(false);

  const [deletingId, setDeletingId] =
    useState(null);

  const [uploadingId, setUploadingId] =
    useState(null);

  const [error, setError] =
    useState("");

  const [success, setSuccess] =
    useState("");

  // ==========================================================
  // LOAD PRODUCTS
  // ==========================================================

  async function loadProducts() {
    try {
      setLoading(true);
      setError("");

      const data =
        await getAdminProducts();

      setProducts(
        Array.isArray(data)
          ? data
          : []
      );
    } catch (err) {
      setError(
        err.message ||
        "Failed to load products"
      );
    } finally {
      setLoading(false);
    }
  }

  // ==========================================================
  // INITIAL LOAD
  // ==========================================================

  useEffect(() => {
    loadProducts();
  }, []);

  // ==========================================================
  // INPUT CHANGE
  // ==========================================================

  function handleChange(event) {
    const {
      name,
      value,
    } = event.target;

    setFormData(
      (previous) => ({
        ...previous,
        [name]: value,
      })
    );
  }

  // ==========================================================
  // RESET FORM
  // ==========================================================

  function resetForm() {
    setFormData({
      ...EMPTY_FORM,
    });

    setEditingProductId(null);

    setSelectedImage(null);

    setError("");
  }

  // ==========================================================
  // START EDIT
  // ==========================================================

  function handleEdit(product) {
    setEditingProductId(product.id);

    setFormData({
      name:
        product.name || "",

      description:
        product.description || "",

      category:
        product.category || "",

      price:
        product.price ?? "",

      stock:
        product.stock ?? 0,
    });

    setSelectedImage(null);

    setError("");

    setSuccess("");

    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  }

  // ==========================================================
  // VALIDATE FORM
  // ==========================================================

  function validateForm() {
    if (!formData.name.trim()) {
      setError(
        "Product name is required"
      );

      return false;
    }

    if (!formData.category.trim()) {
      setError(
        "Product category is required"
      );

      return false;
    }

    if (
      formData.price === "" ||
      Number.isNaN(
        Number(formData.price)
      )
    ) {
      setError(
        "Product price is required"
      );

      return false;
    }

    if (Number(formData.price) < 0) {
      setError(
        "Price cannot be negative"
      );

      return false;
    }

    if (
      formData.stock === "" ||
      Number.isNaN(
        Number(formData.stock)
      )
    ) {
      setError(
        "Product stock is required"
      );

      return false;
    }

    if (Number(formData.stock) < 0) {
      setError(
        "Stock cannot be negative"
      );

      return false;
    }

    return true;
  }

  // ==========================================================
  // CREATE / UPDATE PRODUCT
  // ==========================================================

  async function handleSubmit(event) {
    event.preventDefault();

    setError("");
    setSuccess("");

    if (!validateForm()) {
      return;
    }

    try {
      setSaving(true);

      const product = {
        name:
          formData.name.trim(),

        description:
          formData.description.trim(),

        category:
          formData.category.trim(),

        price:
          Number(formData.price),

        stock:
          Number(formData.stock),
      };

      let savedProduct;

      if (editingProductId) {
        savedProduct =
          await updateAdminProduct(
            editingProductId,
            product
          );

        setSuccess(
          "Product updated successfully"
        );
      } else {
        savedProduct =
          await createAdminProduct(
            product
          );

        setSuccess(
          "Product created successfully"
        );
      }

      // ======================================================
      // IMAGE UPLOAD
      // ======================================================

      if (
        selectedImage &&
        savedProduct?.id
      ) {
        try {
          await uploadAdminProductImage(
            savedProduct.id,
            selectedImage
          );
        } catch (imageError) {
          setError(
            `Product saved, but image upload failed: ${imageError.message}`
          );
        }
      }

      resetForm();

      await loadProducts();

    } catch (err) {
      setError(
        err.message ||
        "Failed to save product"
      );
    } finally {
      setSaving(false);
    }
  }

  // ==========================================================
  // DELETE PRODUCT
  // ==========================================================

  async function handleDelete(productId) {
    const confirmed =
      window.confirm(
        "Are you sure you want to delete this product?"
      );

    if (!confirmed) {
      return;
    }

    try {
      setDeletingId(productId);

      setError("");
      setSuccess("");

      await deleteAdminProduct(
        productId
      );

      setSuccess(
        "Product deleted successfully"
      );

      await loadProducts();

      if (
        editingProductId === productId
      ) {
        resetForm();
      }

    } catch (err) {
      setError(
        err.message ||
        "Failed to delete product"
      );
    } finally {
      setDeletingId(null);
    }
  }

  // ==========================================================
  // UPDATE STOCK
  // ==========================================================

  async function handleStockChange(
    productId,
    currentStock
  ) {
    const value =
      window.prompt(
        "Enter new stock:",
        String(currentStock ?? 0)
      );

    if (value === null) {
      return;
    }

    const stock =
      Number(value);

    if (
      Number.isNaN(stock) ||
      stock < 0 ||
      !Number.isInteger(stock)
    ) {
      setError(
        "Stock must be a whole number greater than or equal to 0"
      );

      return;
    }

    try {
      setError("");
      setSuccess("");

      await updateAdminProductStock(
        productId,
        stock
      );

      setSuccess(
        "Stock updated successfully"
      );

      await loadProducts();

    } catch (err) {
      setError(
        err.message ||
        "Failed to update stock"
      );
    }
  }

  // ==========================================================
  // IMAGE SELECT
  // ==========================================================

  function handleImageChange(event) {
    const file =
      event.target.files?.[0];

    if (!file) {
      setSelectedImage(null);
      return;
    }

    if (
      !file.type.startsWith("image/")
    ) {
      setError(
        "Please select a valid image file"
      );

      event.target.value = "";

      return;
    }

    setSelectedImage(file);
  }

  // ==========================================================
  // UPLOAD EXISTING IMAGE
  // ==========================================================

  async function handleExistingImageUpload(
    productId,
    file
  ) {
    if (!file) {
      return;
    }

    try {
      setUploadingId(productId);

      setError("");
      setSuccess("");

      await uploadAdminProductImage(
        productId,
        file
      );

      setSuccess(
        "Product image uploaded successfully"
      );

      await loadProducts();

    } catch (err) {
      setError(
        err.message ||
        "Image upload failed"
      );
    } finally {
      setUploadingId(null);
    }
  }

  // ==========================================================
  // FORMAT PRICE
  // ==========================================================

  function formatPrice(price) {
    const value =
      Number(price || 0);

    return value.toLocaleString(
      "en-IN",
      {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      }
    );
  }

  // ==========================================================
  // RENDER
  // ==========================================================

  return (
    <div style={styles.page}>

      {/* ====================================================
          HEADER
      ==================================================== */}

      <div style={styles.header}>

        <div>
          <h1 style={styles.headerTitle}>
            Admin Products
          </h1>

          <p style={styles.headerText}>
            Create, edit and manage your products.
          </p>
        </div>

        <button
          type="button"
          style={{
            ...styles.refreshButton,
            opacity: loading ? 0.6 : 1,
            cursor: loading
              ? "not-allowed"
              : "pointer",
          }}
          onClick={loadProducts}
          disabled={loading}
        >
          {loading
            ? "Refreshing..."
            : "Refresh"}
        </button>

      </div>

      {/* ====================================================
          ERROR
      ==================================================== */}

      {error && (
        <div
          style={{
            ...styles.alert,
            ...styles.alertError,
          }}
        >
          <span>
            {error}
          </span>

          <button
            type="button"
            style={styles.alertClose}
            onClick={() =>
              setError("")
            }
          >
            ×
          </button>
        </div>
      )}

      {/* ====================================================
          SUCCESS
      ==================================================== */}

      {success && (
        <div
          style={{
            ...styles.alert,
            ...styles.alertSuccess,
          }}
        >
          <span>
            {success}
          </span>

          <button
            type="button"
            style={styles.alertClose}
            onClick={() =>
              setSuccess("")
            }
          >
            ×
          </button>
        </div>
      )}

      {/* ====================================================
          PRODUCT FORM
      ==================================================== */}

      <section style={styles.card}>

        <div style={styles.cardTitle}>

          <div>

            <h2 style={styles.cardHeading}>
              {editingProductId
                ? "Edit Product"
                : "Create Product"}
            </h2>

            <p style={styles.cardDescription}>
              Enter all required product information.
            </p>

          </div>

          {editingProductId && (
            <button
              type="button"
              style={styles.cancelButton}
              onClick={resetForm}
            >
              Cancel Edit
            </button>
          )}

        </div>

        <form
          style={styles.form}
          onSubmit={handleSubmit}
        >

          {/* NAME */}

          <div style={styles.formGroup}>

            <label
              htmlFor="name"
              style={styles.label}
            >
              Product Name
            </label>

            <input
              id="name"
              name="name"
              type="text"
              value={formData.name}
              onChange={handleChange}
              placeholder="Enter product name"
              required
              style={styles.input}
            />

          </div>

          {/* CATEGORY */}

          <div style={styles.formGroup}>

            <label
              htmlFor="category"
              style={styles.label}
            >
              Category
            </label>

            <select
              id="category"
              name="category"
              value={formData.category}
              onChange={handleChange}
              required
              style={styles.select}
            >

              <option value="">
                Select category
              </option>

              <option value="Mobile">
                Mobile
              </option>

              <option value="Laptop">
                Laptop
              </option>

              <option value="Electronics">
                Electronics
              </option>

              <option value="Clothing">
                Clothing
              </option>

              <option value="Shoes">
                Shoes
              </option>

              <option value="Home">
                Home
              </option>

              <option value="Accessories">
                Accessories
              </option>

              <option value="Other">
                Other
              </option>

            </select>

          </div>

          {/* DESCRIPTION */}

          <div style={styles.formGroupFull}>

            <label
              htmlFor="description"
              style={styles.label}
            >
              Description
            </label>

            <textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleChange}
              placeholder="Enter product description"
              rows="4"
              style={styles.textarea}
            />

          </div>

          {/* PRICE */}

          <div style={styles.formGroup}>

            <label
              htmlFor="price"
              style={styles.label}
            >
              Price
            </label>

            <input
              id="price"
              name="price"
              type="number"
              min="0"
              step="0.01"
              value={formData.price}
              onChange={handleChange}
              placeholder="0.00"
              required
              style={styles.input}
            />

          </div>

          {/* STOCK */}

          <div style={styles.formGroup}>

            <label
              htmlFor="stock"
              style={styles.label}
            >
              Stock
            </label>

            <input
              id="stock"
              name="stock"
              type="number"
              min="0"
              step="1"
              value={formData.stock}
              onChange={handleChange}
              placeholder="0"
              required
              style={styles.input}
            />

          </div>

          {/* IMAGE */}

          <div style={styles.formGroupFull}>

            <label
              htmlFor="product-image"
              style={styles.label}
            >
              Product Image
            </label>

            <input
              id="product-image"
              type="file"
              accept="image/*"
              onChange={handleImageChange}
              style={styles.fileInput}
            />

            {selectedImage && (
              <div style={styles.selectedImage}>
                Selected: {selectedImage.name}
              </div>
            )}

            <small style={styles.smallText}>
              You can upload the image after creating
              the product as well.
            </small>

          </div>

          {/* BUTTONS */}

          <div style={styles.formActions}>

            <button
              type="submit"
              style={{
                ...styles.primaryButton,
                opacity: saving ? 0.6 : 1,
                cursor: saving
                  ? "not-allowed"
                  : "pointer",
              }}
              disabled={saving}
            >
              {saving
                ? "Saving..."
                : editingProductId
                  ? "Update Product"
                  : "Create Product"}
            </button>

            {editingProductId && (
              <button
                type="button"
                style={styles.secondaryButton}
                onClick={resetForm}
                disabled={saving}
              >
                Cancel
              </button>
            )}

          </div>

        </form>

      </section>

      {/* ====================================================
          PRODUCTS LIST
      ==================================================== */}

      <section style={styles.card}>

        <div style={styles.cardTitle}>

          <div>

            <h2 style={styles.cardHeading}>
              Products
            </h2>

            <p style={styles.cardDescription}>
              {products.length} product
              {products.length === 1
                ? ""
                : "s"}
            </p>

          </div>

        </div>

        {loading ? (
          <div style={styles.emptyState}>
            Loading products...
          </div>

        ) : products.length === 0 ? (

          <div style={styles.emptyState}>

            <h3 style={styles.emptyHeading}>
              No products found
            </h3>

            <p style={styles.emptyText}>
              Create your first product using
              the form above.
            </p>

          </div>

        ) : (

          <div style={styles.tableWrapper}>

            <table style={styles.table}>

              <thead>

                <tr>

                  <th style={styles.th}>
                    ID
                  </th>

                  <th style={styles.th}>
                    Product
                  </th>

                  <th style={styles.th}>
                    Category
                  </th>

                  <th style={styles.th}>
                    Price
                  </th>

                  <th style={styles.th}>
                    Stock
                  </th>

                  <th style={styles.th}>
                    Image
                  </th>

                  <th style={styles.th}>
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

                      {/* ID */}

                      <td style={styles.td}>
                        #{product.id}
                      </td>

                      {/* PRODUCT */}

                      <td style={styles.td}>

                        <div
                          style={
                            styles.productNameCell
                          }
                        >

                          <strong
                            style={
                              styles.productName
                            }
                          >
                            {product.name}
                          </strong>

                          {product.description && (
                            <span
                              style={
                                styles.productDescription
                              }
                              title={
                                product.description
                              }
                            >
                              {product.description}
                            </span>
                          )}

                        </div>

                      </td>

                      {/* CATEGORY */}

                      <td style={styles.td}>

                        <span
                          style={
                            styles.categoryBadge
                          }
                        >
                          {product.category ||
                            "No category"}
                        </span>

                      </td>

                      {/* PRICE */}

                      <td style={styles.td}>
                        ₹
                        {formatPrice(
                          product.price
                        )}
                      </td>

                      {/* STOCK */}

                      <td style={styles.td}>

                        <span
                          style={{
                            ...styles.stockBadge,
                            ...(Number(
                              product.stock
                            ) <= 5
                              ? styles.stockLow
                              : styles.stockGood),
                          }}
                        >
                          {product.stock ?? 0}
                        </span>

                      </td>

                      {/* IMAGE */}

                      <td style={styles.td}>

                        <div
                          style={
                            styles.imageAction
                          }
                        >

                          {product.images ? (

                            <img
                              src={
                                product.images
                              }
                              alt={
                                product.name
                              }
                              style={
                                styles.productThumbnail
                              }
                            />

                          ) : (

                            <div
                              style={
                                styles.noImage
                              }
                            >
                              No image
                            </div>

                          )}

                          <label
                            style={
                              styles.uploadButton
                            }
                          >

                            {uploadingId ===
                            product.id
                              ? "Uploading..."
                              : "Upload"}

                            <input
                              type="file"
                              accept="image/*"
                              hidden
                              disabled={
                                uploadingId ===
                                product.id
                              }
                              onChange={(
                                event
                              ) => {

                                const file =
                                  event.target
                                    .files?.[0];

                                if (file) {

                                  handleExistingImageUpload(
                                    product.id,
                                    file
                                  );

                                }

                                event.target.value =
                                  "";

                              }}
                            />

                          </label>

                        </div>

                      </td>

                      {/* ACTIONS */}

                      <td style={styles.td}>

                        <div
                          style={
                            styles.actionButtons
                          }
                        >

                          <button
                            type="button"
                            style={{
                              ...styles.actionButton,
                              ...styles.editButton,
                            }}
                            onClick={() =>
                              handleEdit(
                                product
                              )
                            }
                          >
                            Edit
                          </button>

                          <button
                            type="button"
                            style={{
                              ...styles.actionButton,
                              ...styles.stockButton,
                            }}
                            onClick={() =>
                              handleStockChange(
                                product.id,
                                product.stock
                              )
                            }
                          >
                            Stock
                          </button>

                          <button
                            type="button"
                            style={{
                              ...styles.actionButton,
                              ...styles.deleteButton,
                              opacity:
                                deletingId ===
                                product.id
                                  ? 0.6
                                  : 1,
                              cursor:
                                deletingId ===
                                product.id
                                  ? "not-allowed"
                                  : "pointer",
                            }}
                            disabled={
                              deletingId ===
                              product.id
                            }
                            onClick={() =>
                              handleDelete(
                                product.id
                              )
                            }
                          >

                            {deletingId ===
                            product.id
                              ? "Deleting..."
                              : "Delete"}

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

      </section>

    </div>
  );
}