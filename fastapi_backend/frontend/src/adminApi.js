const API_BASE_URL = "http://localhost:8000";

// ============================================================
// TOKEN
// ============================================================

function getToken() {
  return (
    localStorage.getItem("access_token") ||
    localStorage.getItem("token")
  );
}


// ============================================================
// COMMON REQUEST
// ============================================================

async function request(url, options = {}) {
  const token = getToken();

  const response = await fetch(
    `${API_BASE_URL}${url}`,
    {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...(options.headers || {}),
        ...(token
          ? {
              Authorization: `Bearer ${token}`,
            }
          : {}),
      },
    }
  );

  if (!response.ok) {
    let message = "Request failed";

    try {
      const data = await response.json();

      if (typeof data.detail === "string") {
        message = data.detail;
      } else if (data.detail) {
        message = JSON.stringify(data.detail);
      }
    } catch {
      // Ignore JSON parsing error
    }

    throw new Error(message);
  }

  return response;
}


// ============================================================
// ADMIN DASHBOARD
// ============================================================

export async function getAdminDashboard(
  lowStockThreshold = 5
) {
  const response = await request(
    `/admin/analytics/dashboard?low_stock_threshold=${lowStockThreshold}`
  );

  return response.json();
}


// ============================================================
// ADMIN REPORTS
// ============================================================

export async function downloadReport(
  reportType,
  format
) {
  const response = await request(
    `/admin/reports/${reportType}/${format}`
  );

  const blob = await response.blob();

  const contentDisposition =
    response.headers.get("Content-Disposition");

  let filename = `${reportType}.${format}`;

  if (contentDisposition) {
    const match =
      contentDisposition.match(
        /filename="?([^"]+)"?/i
      );

    if (match) {
      filename = match[1];
    }
  }

  const url =
    window.URL.createObjectURL(blob);

  const link =
    document.createElement("a");

  link.href = url;
  link.download = filename;

  document.body.appendChild(link);

  link.click();

  link.remove();

  window.URL.revokeObjectURL(url);
}


// ============================================================
// ADMIN ORDERS
// ============================================================

export async function getAdminOrders() {
  const response = await request(
    "/admin/orders"
  );

  return response.json();
}


// ============================================================
// ADMIN SINGLE ORDER
// ============================================================

export async function getAdminOrder(orderId) {
  const response = await request(
    `/admin/orders/${orderId}`
  );

  return response.json();
}


// ============================================================
// ADMIN ORDER PAYMENT
// ============================================================

export async function getAdminOrderPayment(
  orderId
) {
  const response = await request(
    `/admin/orders/${orderId}/payment`
  );

  return response.json();
}


// ============================================================
// UPDATE ORDER STATUS
// ============================================================

export async function updateAdminOrderStatus(
  orderId,
  orderStatus
) {
  const response = await request(
    `/admin/orders/${orderId}/status`,
    {
      method: "PATCH",

      body: JSON.stringify({
        order_status: orderStatus,
      }),
    }
  );

  return response.json();
}


// ============================================================
// MARK PAYMENT REFUNDED
// ============================================================

export async function markPaymentRefunded(
  orderId
) {
  const response = await request(
    `/admin/orders/${orderId}/payment/refunded`,
    {
      method: "PATCH",
    }
  );

  return response.json();
}


// ============================================================
// ADMIN RETURNS
// ============================================================

export async function getAdminReturns() {
  const response = await request(
    "/admin/returns"
  );

  return response.json();
}


// ============================================================
// APPROVE RETURN
// ============================================================

export async function approveAdminReturn(
  returnId
) {
  const response = await request(
    `/admin/returns/${returnId}/approve`,
    {
      method: "POST",
    }
  );

  return response.json();
}


// ============================================================
// REJECT RETURN
// ============================================================

export async function rejectAdminReturn(
  returnId
) {
  const response = await request(
    `/admin/returns/${returnId}/reject`,
    {
      method: "POST",
    }
  );

  return response.json();
}


// ============================================================
// ADMIN PRODUCTS
// ============================================================

// GET ALL PRODUCTS

export async function getAdminProducts() {
  const response = await request(
    "/admin/products"
  );

  return response.json();
}


// ============================================================
// CREATE PRODUCT
// ============================================================

export async function createAdminProduct(
  product
) {
  const response = await request(
    "/admin/products",
    {
      method: "POST",

      body: JSON.stringify({
        name: product.name,
        description:
          product.description || null,
        category: product.category,
        price: Number(product.price),
        stock: Number(product.stock),
      }),
    }
  );

  return response.json();
}


// ============================================================
// UPDATE PRODUCT
// ============================================================

export async function updateAdminProduct(
  productId,
  product
) {
  const response = await request(
    `/admin/products/${productId}`,
    {
      method: "PUT",

      body: JSON.stringify({
        name: product.name,
        description:
          product.description || null,
        category: product.category,
        price: Number(product.price),
        stock: Number(product.stock),
      }),
    }
  );

  return response.json();
}


// ============================================================
// DELETE PRODUCT
// ============================================================

export async function deleteAdminProduct(
  productId
) {
  const response = await request(
    `/admin/products/${productId}`,
    {
      method: "DELETE",
    }
  );

  return response.json();
}


// ============================================================
// UPDATE PRODUCT STOCK
// ============================================================

export async function updateAdminProductStock(
  productId,
  stock
) {
  const response = await request(
    `/admin/products/${productId}/stock?stock=${Number(stock)}`,
    {
      method: "PATCH",
    }
  );

  return response.json();
}


// ============================================================
// UPLOAD PRODUCT IMAGE
// ============================================================

export async function uploadAdminProductImage(
  productId,
  file
) {
  const token = getToken();

  const formData = new FormData();

  formData.append(
    "file",
    file
  );

  const response = await fetch(
    `${API_BASE_URL}/admin/products/${productId}/image`,
    {
      method: "POST",

      headers: {
        ...(token
          ? {
              Authorization:
                `Bearer ${token}`,
            }
          : {}),
      },

      body: formData,
    }
  );

  if (!response.ok) {
    let message =
      "Image upload failed";

    try {
      const data =
        await response.json();

      message =
        data.detail || message;
    } catch {
      // Ignore
    }

    throw new Error(message);
  }

  return response.json();
}