const API_BASE = "";

function getToken() {
    return localStorage.getItem("sf_token");
}

function setToken(token) {
    localStorage.setItem("sf_token", token);
}

function clearToken() {
    localStorage.removeItem("sf_token");
}

async function apiRequest(path, options = {}) {
    const token = getToken();
    const headers = options.headers || {};
    if (!(options.body instanceof FormData)) {
        headers["Content-Type"] = headers["Content-Type"] || "application/json";
    }
    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }
    const resp = await fetch(API_BASE + path, {
        ...options,
        headers
    });
    if (resp.status === 401) {
        clearToken();
        if (!window.location.pathname.startsWith("/login") &&
            !window.location.pathname.startsWith("/signup")) {
            window.location.href = "/login";
        }
        throw new Error("Unauthorized");
    }
    if (!resp.ok) {
        let msg = "Request failed";
        try {
            const data = await resp.json();
            msg = data.detail || JSON.stringify(data);
        } catch (_) {}
        throw new Error(msg);
    }
    if (resp.status === 204) return null;
    try {
        return await resp.json();
    } catch (_) {
        return null;
    }
}

function requireAuthForAppPages() {
    const page = document.body.dataset.page;
    const isAuthPage = page === "login" || page === "signup";
    if (!isAuthPage && !getToken()) {
        window.location.href = "/login";
    }
}

/* -------- Page initializers -------- */

function initLoginPage() {
    const form = document.getElementById("login-form");
    const errorEl = document.getElementById("login-error");
    if (!form) return;

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        errorEl.textContent = "";
        const email = document.getElementById("login-email").value.trim();
        const password = document.getElementById("login-password").value;
        try {
            const data = await apiRequest("/login", {
                method: "POST",
                body: JSON.stringify({ email, password })
            });
            setToken(data.access_token);
            window.location.href = "/dashboard";
        } catch (err) {
            errorEl.textContent = err.message;
        }
    });
}

function initSignupPage() {
    const form = document.getElementById("signup-form");
    const errorEl = document.getElementById("signup-error");
    if (!form) return;

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        errorEl.textContent = "";
        const org = document.getElementById("signup-org").value.trim();
        const email = document.getElementById("signup-email").value.trim();
        const password = document.getElementById("signup-password").value;
        const confirm = document.getElementById("signup-password-confirm").value;

        if (password !== confirm) {
            errorEl.textContent = "Passwords do not match";
            return;
        }

        try {
            const data = await apiRequest("/signup", {
                method: "POST",
                body: JSON.stringify({
                    email,
                    password,
                    organization_name: org
                })
            });
            setToken(data.access_token);
            window.location.href = "/dashboard";
        } catch (err) {
            errorEl.textContent = err.message;
        }
    });
}

function initDashboardPage() {
    const errorEl = document.getElementById("dashboard-error");
    const totalProductsEl = document.getElementById("total-products");
    const totalUnitsEl = document.getElementById("total-units");
    const tableBody = document.querySelector("#low-stock-table tbody");
    if (!totalProductsEl) return;

    apiRequest("/dashboard")
        .then((data) => {
            totalProductsEl.textContent = data.total_products;
            totalUnitsEl.textContent = data.total_inventory_units;
            tableBody.innerHTML = "";
            if (data.low_stock_products.length === 0) {
                const row = document.createElement("tr");
                const cell = document.createElement("td");
                cell.colSpan = 4;
                cell.textContent = "No low stock products.";
                cell.style.color = "#6b7280";
                row.appendChild(cell);
                tableBody.appendChild(row);
            } else {
                data.low_stock_products.forEach((p) => {
                    const row = document.createElement("tr");
                    row.innerHTML = `
                        <td>${p.name}</td>
                        <td>${p.sku}</td>
                        <td>${p.quantity_on_hand}</td>
                        <td>${p.effective_threshold}</td>
                    `;
                    tableBody.appendChild(row);
                });
            }
        })
        .catch((err) => {
            errorEl.textContent = err.message;
        });
}

function initProductsPage() {
    const errorEl = document.getElementById("products-error");
    const tableBody = document.querySelector("#products-table tbody");
    if (!tableBody) return;

    function loadProducts() {
        apiRequest("/products")
            .then((products) => {
                tableBody.innerHTML = "";
                if (products.length === 0) {
                    const row = document.createElement("tr");
                    const cell = document.createElement("td");
                    cell.colSpan = 6;
                    cell.textContent = "No products yet.";
                    cell.style.color = "#6b7280";
                    row.appendChild(cell);
                    tableBody.appendChild(row);
                    return;
                }
                products.forEach((p) => {
                    const row = document.createElement("tr");
                    const lowBadge = p.is_low_stock
                        ? `<span class="badge badge-danger">Low</span>`
                        : "";
                    row.innerHTML = `
                        <td>${p.name}</td>
                        <td>${p.sku}</td>
                        <td>${p.quantity_on_hand}</td>
                        <td>${p.selling_price.toFixed(2)}</td>
                        <td>${lowBadge}</td>
                        <td>
                            <a href="/products/${p.id}/edit" class="btn secondary-btn" style="font-size:12px;padding:4px 10px;">Edit</a>
                            <button data-id="${p.id}" class="btn primary-btn" style="font-size:12px;padding:4px 10px;background:#dc2626;">Delete</button>
                        </td>
                    `;
                    tableBody.appendChild(row);
                });

                tableBody.querySelectorAll("button[data-id]").forEach((btn) => {
                    btn.addEventListener("click", async () => {
                        const id = btn.getAttribute("data-id");
                        if (!confirm("Delete this product?")) return;
                        try {
                            await apiRequest(`/products/${id}`, { method: "DELETE" });
                            loadProducts();
                        } catch (err) {
                            errorEl.textContent = err.message;
                        }
                    });
                });
            })
            .catch((err) => {
                errorEl.textContent = err.message;
            });
    }

    loadProducts();
}

function initProductFormPage() {
    const form = document.getElementById("product-form");
    if (!form) return;
    const errorEl = document.getElementById("product-form-error");
    const mode = document.getElementById("product-mode").value;
    const id = document.getElementById("product-id").value;
    const titleEl = document.getElementById("product-form-title");

    if (mode === "create") {
        titleEl.textContent = "New Product";
    } else {
        titleEl.textContent = "Edit Product";
        // Load existing
        apiRequest(`/products/${id}`)
            .then((p) => {
                document.getElementById("product-name").value = p.name;
                document.getElementById("product-sku").value = p.sku;
                document.getElementById("product-description").value = p.description || "";
                document.getElementById("product-qty").value = p.quantity_on_hand;
                document.getElementById("product-cost").value = p.cost_price;
                document.getElementById("product-selling").value = p.selling_price;
                document.getElementById("product-threshold").value = p.low_stock_threshold || "";
            })
            .catch((err) => {
                errorEl.textContent = err.message;
            });
    }

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        errorEl.textContent = "";

        const payload = {
            name: document.getElementById("product-name").value.trim(),
            sku: document.getElementById("product-sku").value.trim(),
            description: document.getElementById("product-description").value.trim(),
            quantity_on_hand: Number(document.getElementById("product-qty").value || "0"),
            cost_price: Number(document.getElementById("product-cost").value || "0"),
            selling_price: Number(document.getElementById("product-selling").value || "0"),
        };
        const thresholdVal = document.getElementById("product-threshold").value;
        if (thresholdVal !== "") {
            payload.low_stock_threshold = Number(thresholdVal);
        } else if (mode === "edit") {
            // allow clearing in edit by explicitly sending null
            payload.low_stock_threshold = null;
        }

        try {
            if (mode === "create") {
                await apiRequest("/products", {
                    method: "POST",
                    body: JSON.stringify(payload)
                });
            } else {
                await apiRequest(`/products/${id}`, {
                    method: "PUT",
                    body: JSON.stringify(payload)
                });
            }
            window.location.href = "/products-page";
        } catch (err) {
            errorEl.textContent = err.message;
        }
    });
}

function initSettingsPage() {
    const form = document.getElementById("settings-form");
    if (!form) return;
    const errorEl = document.getElementById("settings-error");
    const input = document.getElementById("default-threshold");

    apiRequest("/settings")
        .then((data) => {
            input.value = data.default_low_stock_threshold;
        })
        .catch((err) => {
            errorEl.textContent = err.message;
        });

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        errorEl.textContent = "";
        const val = Number(input.value || "0");
        try {
            const data = await apiRequest("/settings", {
                method: "PUT",
                body: JSON.stringify({ default_low_stock_threshold: val })
            });
            input.value = data.default_low_stock_threshold;
        } catch (err) {
            errorEl.textContent = err.message;
        }
    });
}

function initLogoutButton() {
    const btn = document.getElementById("logout-btn");
    if (!btn) return;
    btn.addEventListener("click", () => {
        clearToken();
        window.location.href = "/login";
    });
}

document.addEventListener("DOMContentLoaded", () => {
    const page = document.body.dataset.page;
    requireAuthForAppPages();
    initLogoutButton();
    if (page === "login") initLoginPage();
    if (page === "signup") initSignupPage();
    if (page === "dashboard") initDashboardPage();
    if (page === "products") initProductsPage();
    if (page === "product-form") initProductFormPage();
    if (page === "settings") initSettingsPage();
});