/* ── State ───────────────────────────────────────────────────── */
let allTransactions = [];
let barChart = null;
let pieChart = null;

/* ── Utilities ───────────────────────────────────────────────── */
const fmt = (n) =>
  new Intl.NumberFormat(undefined, { style: "currency", currency: "USD" }).format(n);

const todayISO = () => new Date().toISOString().slice(0, 10);

/* ── Fetch helpers ───────────────────────────────────────────── */
async function apiFetch(url, options = {}) {
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `HTTP ${res.status}`);
  }
  if (res.status === 204) return null;
  return res.json();
}

/* ── Charts ──────────────────────────────────────────────────── */
function renderBarChart(income, expenses) {
  const ctx = document.getElementById("barChart").getContext("2d");
  if (barChart) barChart.destroy();
  barChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: ["Income", "Expenses"],
      datasets: [
        {
          label: "Amount",
          data: [income, expenses],
          backgroundColor: ["rgba(34,197,94,.75)", "rgba(239,68,68,.75)"],
          borderColor: ["#16a34a", "#dc2626"],
          borderWidth: 2,
          borderRadius: 6,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            callback: (v) => "$" + v.toLocaleString(),
          },
        },
      },
    },
  });
}

function renderPieChart(breakdown) {
  const pieEmpty = document.getElementById("pieEmpty");
  const canvas = document.getElementById("pieChart");

  if (!breakdown.length) {
    canvas.classList.add("hidden");
    pieEmpty.classList.remove("hidden");
    if (pieChart) { pieChart.destroy(); pieChart = null; }
    return;
  }

  canvas.classList.remove("hidden");
  pieEmpty.classList.add("hidden");

  const palette = [
    "#6366f1","#f59e0b","#10b981","#ef4444","#3b82f6",
    "#ec4899","#14b8a6","#f97316","#8b5cf6","#84cc16",
  ];

  const ctx = canvas.getContext("2d");
  if (pieChart) pieChart.destroy();
  pieChart = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: breakdown.map((b) => b.category || "Uncategorized"),
      datasets: [
        {
          data: breakdown.map((b) => b.total),
          backgroundColor: breakdown.map((_, i) => palette[i % palette.length]),
          borderWidth: 2,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        legend: { position: "bottom" },
        tooltip: {
          callbacks: {
            label: (ctx) => ` ${fmt(ctx.parsed)} (${(
              (ctx.parsed / ctx.dataset.data.reduce((a, b) => a + b, 0)) * 100
            ).toFixed(1)}%)`,
          },
        },
      },
    },
  });
}

/* ── Summary cards ───────────────────────────────────────────── */
async function loadSummary() {
  try {
    const data = await apiFetch("/api/summary");
    const balance = data.total_income - data.total_expenses;

    document.getElementById("totalIncome").textContent = fmt(data.total_income);
    document.getElementById("totalExpenses").textContent = fmt(data.total_expenses);
    const balanceEl = document.getElementById("balance");
    balanceEl.textContent = fmt(balance);
    balanceEl.style.color =
      balance >= 0 ? "var(--success)" : "var(--danger)";

    renderBarChart(data.total_income, data.total_expenses);
    renderPieChart(data.expense_by_category);
  } catch (err) {
    console.error("Failed to load summary:", err);
  }
}

/* ── Transaction table ───────────────────────────────────────── */
function renderTable(transactions) {
  const tbody = document.getElementById("txBody");
  if (!transactions.length) {
    tbody.innerHTML =
      '<tr><td colspan="6" class="center">No transactions yet.</td></tr>';
    return;
  }

  tbody.innerHTML = transactions
    .map(
      (t) => `
    <tr data-id="${t.id}">
      <td>${t.date}</td>
      <td>${escHtml(t.name)}</td>
      <td>${escHtml(t.category || "—")}</td>
      <td><span class="type-badge type-${t.type}">${t.type}</span></td>
      <td class="amount-${t.type}">${t.type === "income" ? "+" : "-"}${fmt(t.amount)}</td>
      <td>
        <button class="btn-danger" onclick="deleteTransaction(${t.id})">Delete</button>
      </td>
    </tr>`
    )
    .join("");
}

function applyFilters() {
  const text = document.getElementById("filterInput").value.toLowerCase();
  const type = document.getElementById("filterType").value;
  const filtered = allTransactions.filter((t) => {
    const matchText =
      !text ||
      t.name.toLowerCase().includes(text) ||
      (t.category || "").toLowerCase().includes(text);
    const matchType = !type || t.type === type;
    return matchText && matchType;
  });
  renderTable(filtered);
}

async function loadTransactions() {
  try {
    allTransactions = await apiFetch("/api/transactions");
    applyFilters();
  } catch (err) {
    document.getElementById("txBody").innerHTML =
      '<tr><td colspan="6" class="center">Failed to load transactions.</td></tr>';
    console.error(err);
  }
}

/* ── Delete ──────────────────────────────────────────────────── */
async function deleteTransaction(id) {
  if (!confirm("Delete this transaction?")) return;
  try {
    await apiFetch(`/api/transactions/${id}`, { method: "DELETE" });
    allTransactions = allTransactions.filter((t) => t.id !== id);
    applyFilters();
    await loadSummary();
  } catch (err) {
    alert("Could not delete: " + err.message);
  }
}

/* ── Add transaction form ────────────────────────────────────── */
document.getElementById("txForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const errEl = document.getElementById("formError");
  errEl.classList.add("hidden");

  const body = {
    type: document.getElementById("txType").value,
    amount: parseFloat(document.getElementById("txAmount").value),
    name: document.getElementById("txName").value.trim(),
    category: document.getElementById("txCategory").value.trim(),
    date: document.getElementById("txDate").value,
  };

  try {
    const created = await apiFetch("/api/transactions", {
      method: "POST",
      body: JSON.stringify(body),
    });
    allTransactions.unshift(created);
    applyFilters();
    await loadSummary();
    e.target.reset();
    document.getElementById("txDate").value = todayISO();
  } catch (err) {
    errEl.textContent = err.message;
    errEl.classList.remove("hidden");
  }
});

/* ── Filter listeners ────────────────────────────────────────── */
document.getElementById("filterInput").addEventListener("input", applyFilters);
document.getElementById("filterType").addEventListener("change", applyFilters);

/* ── Escape HTML helper ──────────────────────────────────────── */
function escHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

/* ── Init ────────────────────────────────────────────────────── */
document.getElementById("txDate").value = todayISO();
loadTransactions();
loadSummary();
