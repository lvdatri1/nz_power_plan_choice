const API = '';

let allPlans = [];
let allRetailers = [];

document.addEventListener('DOMContentLoaded', async () => {
  initNav();
  await loadData();
  initDashboard();
  initPlans();
  initCalculator();
  initCompare();
});

async function loadData() {
  const [retailers, plans] = await Promise.all([
    api('/api/retailers').catch(() => []),
    api('/api/plans').catch(() => []),
  ]);
  allRetailers = retailers;
  allPlans = plans;
}

/* === Navigation === */
function initNav() {
  document.querySelectorAll('[data-tab]').forEach(a => {
    a.addEventListener('click', e => {
      e.preventDefault();
      setTab(a.dataset.tab);
    });
  });
}

function setTab(name) {
  document.querySelectorAll('[data-tab]').forEach(a => a.classList.toggle('active', a.dataset.tab === name));
  document.querySelectorAll('.tab-content').forEach(s => s.classList.toggle('active', s.id === `tab-${name}`));
  if (name === 'plans') renderPlans(allPlans);
}

async function api(path) {
  const res = await fetch(`${API}${path}`);
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json();
}

async function apiWithTimeout(path, ms) {
  const ctrl = new AbortController();
  const t = setTimeout(() => ctrl.abort(), ms);
  try {
    const res = await fetch(`${API}${path}`, { signal: ctrl.signal });
    if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
    return res.json();
  } finally {
    clearTimeout(t);
  }
}

async function apiPost(path, body) {
  const res = await fetch(`${API}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json();
}

/* === Dashboard === */
async function initDashboard() {
  const haStatus = await apiWithTimeout('/api/ha/status', 5000).catch(() => null);

  const haEl = document.getElementById('ha-info');
  const compareSection = document.getElementById('ha-compare-section');
  if (haStatus && haStatus.connected) {
    haEl.innerHTML = `<span class="connected">Connected</span> — sensor: ${haStatus.sensor}`;
    compareSection.style.display = 'block';
  } else if (haStatus && !haStatus.connected) {
    haEl.innerHTML = '<span class="disconnected">Not connected</span> (add-on or sensor not configured)';
    compareSection.style.display = 'none';
  } else {
    haEl.innerHTML = '<span class="disconnected">Not available</span> (not running as HA add-on)';
    compareSection.style.display = 'none';
  }

  document.getElementById('ha-compare-btn').addEventListener('click', doHaCompare);

  populateSelect('dash-plan', plans);
  document.getElementById('dash-calc').addEventListener('click', doDashCalc);
}

async function doDashCalc() {
  const planId = document.getElementById('dash-plan').value;
  const importKwh = parseFloat(document.getElementById('dash-import').value) || 0;
  const exportKwh = parseFloat(document.getElementById('dash-export').value) || 0;

  const usage = [];
  if (importKwh > 0) usage.push({ timestamp: new Date().toISOString(), kwh: importKwh });

  try {
    const result = await apiPost('/api/cost/calculate', {
      plan_id: parseInt(planId),
      usage,
      include_export: exportKwh > 0,
      export_usage: exportKwh > 0 ? [{ timestamp: new Date().toISOString(), kwh: exportKwh }] : [],
    });
    document.getElementById('dash-result').innerHTML = renderBreakdown(result);
  } catch (err) {
    document.getElementById('dash-result').innerHTML = `<p style="color:#dc2626">Error: ${err.message}</p>`;
  }
}

async function doHaCompare() {
  const days = parseInt(document.getElementById('ha-compare-days').value) || 30;
  const resultEl = document.getElementById('ha-compare-result');
  resultEl.innerHTML = '<p>Comparing all plans…</p>';

  try {
    const data = await api(`/api/ha/compare?days=${days}`);
    if (!data.results || data.results.length === 0) {
      resultEl.innerHTML = '<p style="color:var(--warning)">No plans to compare. Check sensor values.</p>';
      return;
    }
    const rows = data.results.map((r, i) => {
      const isCheapest = i === 0;
      return `<tr class="${isCheapest ? 'total' : ''}">
        <td>${isCheapest ? '★ ' : ''}${r.retailer_name}</td>
        <td>${r.plan_name}</td>
        <td>${r.rate_type}</td>
        <td>${r.has_export ? '✓' : '—'}</td>
        <td>$${r.import_cost.toFixed(2)}</td>
        <td>${r.export_credit > 0 ? '-$' + r.export_credit.toFixed(2) : '—'}</td>
        <td>$${r.daily_charges.toFixed(2)}</td>
        <td><strong>$${r.net_cost.toFixed(2)}</strong></td>
        <td><strong>$${r.monthly_cost.toFixed(2)}</strong></td>
      </tr>`;
    }).join('');
    resultEl.innerHTML = `
      <p style="margin-bottom:8px;font-size:.9rem;color:var(--text-secondary)">
        ${data.import_kwh.toFixed(2)} kWh import, ${data.export_kwh.toFixed(2)} kWh export over ${days} days
        — <strong>${data.plans_compared}</strong> plans compared
      </p>
      <div style="overflow-x:auto">
      <table class="breakdown-table">
        <tr>
          <th>Retailer</th><th>Plan</th><th>Type</th><th>Solar</th>
          <th>Import</th><th>Export</th><th>Daily</th><th>Total</th><th>/month</th>
        </tr>
        ${rows}
      </table>
      </div>`;
  } catch (err) {
    resultEl.innerHTML = `<p style="color:#dc2626">Error: ${err.message}</p>`;
  }
}

/* === Plans === */
function initPlans() {
  populateSelect('filter-retailer', allRetailers.map(r => ({ id: r.id, name: r.name })));
  document.getElementById('filter-retailer').addEventListener('change', applyFilters);
  document.getElementById('filter-rate').addEventListener('change', applyFilters);
}

function applyFilters() {
  const retailerId = document.getElementById('filter-retailer').value;
  const rateType = document.getElementById('filter-rate').value;
  let filtered = allPlans;
  if (retailerId) filtered = filtered.filter(p => p.retailer_id == retailerId || p.retailer?.id == retailerId);
  if (rateType) filtered = filtered.filter(p => p.rate_type === rateType);
  renderPlans(filtered);
}

function renderPlans(plans) {
  const grid = document.getElementById('plans-grid');
  grid.innerHTML = plans.map(p => {
    const retailerName = p.retailer?.name || p.retailer_name || '';
    return `<div class="plan-card" onclick="showPlanDetail(${p.id})">
      <h4>${p.name}</h4>
      <div class="retailer">${retailerName}</div>
      <div>
        <span class="rate-badge">${p.rate_type}</span>
      </div>
      ${p.daily_charge ? `<div class="daily-charge">Daily charge: $${p.daily_charge.toFixed(4)}</div>` : ''}
    </div>`;
  }).join('');
}

async function showPlanDetail(id) {
  const plan = await api(`/api/plans/${id}`);
  const overlay = document.createElement('div');
  overlay.className = 'modal-overlay';
  overlay.onclick = e => { if (e.target === overlay) overlay.remove(); };

  let ratesHtml = '';
  if (plan.rate_type === 'FLAT' && plan.flat_rates?.length) {
    ratesHtml += `<div class="rate-section"><h4>Flat Rate</h4>
      <table class="breakdown-table">
        <tr><th>Description</th><th>Rate (c/kWh)</th></tr>
        ${plan.flat_rates.map(r => `<tr><td>${r.description || 'Standard'}</td><td>${r.rate_cents_per_kwh.toFixed(4)}</td></tr>`).join('')}
      </table></div>`;
  }
  if (plan.rate_type === 'TIERED' && plan.tiered_rates?.length) {
    ratesHtml += `<div class="rate-section"><h4>Tiered Rates</h4>
      <table class="breakdown-table">
        <tr><th>Tier</th><th>Rate (c/kWh)</th></tr>
        ${plan.tiered_rates.map(r => `<tr><td>${r.tier_name || `Tier ${r.tier_order}`}${r.max_kwh ? ` (up to ${r.max_kwh} kWh)` : ' (unlimited)'}</td><td>${r.rate_cents_per_kwh.toFixed(4)}</td></tr>`).join('')}
      </table></div>`;
  }
  if (plan.rate_type === 'TOU') {
    if (plan.tou_rates?.length) {
      ratesHtml += `<div class="rate-section"><h4>TOU Import Rates</h4>
        <table class="breakdown-table">
          <tr><th>Period</th><th>Days</th><th>Time</th><th>Rate (c/kWh)</th></tr>
          ${plan.tou_rates.map(r => `<tr><td>${r.period_name}</td><td>${r.day_of_week || 'all'}</td><td>${r.start_hour}:00-${r.end_hour}:00</td><td>${r.rate_cents_per_kwh.toFixed(4)}</td></tr>`).join('')}
        </table></div>`;
    }
    if (plan.tou_export_rates?.length) {
      ratesHtml += `<div class="rate-section"><h4>TOU Export Rates</h4>
        <table class="breakdown-table">
          <tr><th>Period</th><th>Days</th><th>Time</th><th>Rate (c/kWh)</th></tr>
          ${plan.tou_export_rates.map(r => `<tr><td>${r.period_name}</td><td>${r.day_of_week || 'all'}</td><td>${r.start_hour}:00-${r.end_hour}:00</td><td>${r.rate_cents_per_kwh.toFixed(4)}</td></tr>`).join('')}
        </table></div>`;
    }
  }

  overlay.innerHTML = `<div class="modal">
    <button class="close-btn" onclick="this.closest('.modal-overlay').remove()">✕</button>
    <h2>${plan.name}</h2>
    <p style="color:var(--text-secondary);margin-bottom:8px">${plan.retailer?.name || ''}</p>
    <p>Rate type: <strong>${plan.rate_type}</strong></p>
    ${plan.daily_charge ? `<p>Daily charge: <strong>$${plan.daily_charge.toFixed(4)}/day</strong></p>` : ''}
    ${ratesHtml}
  </div>`;
  document.body.appendChild(overlay);
}

/* === Calculator === */
function initCalculator() {
  populateSelect('calc-plan', allPlans);
  document.getElementById('add-entry').addEventListener('click', () => {
    const container = document.getElementById('calc-entries');
    const row = document.createElement('div');
    row.className = 'entry-row';
    row.innerHTML = '<input type="number" class="entry-time" min="0" max="23" placeholder="Hour"><input type="number" class="entry-kwh" step="0.01" placeholder="kWh">';
    container.appendChild(row);
  });
  document.getElementById('calc-export-check').addEventListener('change', e => {
    document.getElementById('calc-export-entries').style.display = e.target.checked ? 'block' : 'none';
  });
  document.getElementById('calc-btn').addEventListener('click', doCalc);
}

async function doCalc() {
  const planId = document.getElementById('calc-plan').value;
  const days = parseInt(document.getElementById('calc-daily').value) || 30;

  const usage = [];
  document.querySelectorAll('#calc-entries .entry-row').forEach(row => {
    const hour = parseInt(row.querySelector('.entry-time').value);
    const kwh = parseFloat(row.querySelector('.entry-kwh').value);
    if (!isNaN(kwh) && kwh > 0) {
      const d = new Date(); d.setHours(hour, 0, 0, 0);
      usage.push({ timestamp: d.toISOString(), kwh });
    }
  });

  let exportUsage = [];
  if (document.getElementById('calc-export-check').checked) {
    document.querySelectorAll('#calc-export-entries .entry-row').forEach(row => {
      const hour = parseInt(row.querySelector('.export-time').value);
      const kwh = parseFloat(row.querySelector('.export-kwh').value);
      if (!isNaN(kwh) && kwh > 0) {
        const d = new Date(); d.setHours(hour, 0, 0);
        exportUsage.push({ timestamp: d.toISOString(), kwh });
      }
    });
  }

  try {
    const result = await apiPost('/api/cost/calculate', {
      plan_id: parseInt(planId),
      usage,
      days,
      include_export: exportUsage.length > 0,
      export_usage: exportUsage,
    });
    document.getElementById('calc-result-card').style.display = 'block';
    document.getElementById('calc-result').innerHTML = renderBreakdown(result);
  } catch (err) {
    document.getElementById('calc-result-card').style.display = 'block';
    document.getElementById('calc-result').innerHTML = `<p style="color:#dc2626">Error: ${err.message}</p>`;
  }
}

/* === Compare === */
function initCompare() {
  const sel = document.getElementById('compare-plans');
  allPlans.forEach(p => {
    const opt = document.createElement('option');
    opt.value = p.id;
    opt.textContent = `${p.retailer?.name || p.retailer_name || ''} — ${p.name}`;
    sel.appendChild(opt);
  });
  document.getElementById('compare-btn').addEventListener('click', doCompare);
}

async function doCompare() {
  const sel = document.getElementById('compare-plans');
  const selected = Array.from(sel.selectedOptions).map(o => parseInt(o.value));
  if (selected.length < 2) {
    document.getElementById('compare-results').innerHTML = '<p style="color:var(--warning)">Select at least 2 plans</p>';
    return;
  }

  const totalKwh = parseFloat(document.getElementById('compare-usage').value) || 300;
  const results = document.getElementById('compare-results');

  try {
    const costs = await Promise.all(selected.map(async planId => {
      const plan = await api(`/api/plans/${planId}`);
      const result = await apiPost('/api/cost/calculate', {
        plan_id: planId,
        usage: [{ timestamp: new Date().toISOString(), kwh: totalKwh }],
        days: 30,
        include_export: false,
        export_usage: [],
      });
      return { ...result, retailerName: plan.retailer?.name || '' };
    }));

    const minCost = Math.min(...costs.map(c => c.breakdown?.net_cost ?? Infinity));



    results.innerHTML = `<p style="margin-bottom:12px">Monthly cost for <strong>${totalKwh} kWh</strong>:</p>
      <div class="compare-grid">
        ${costs.map(c => {
          const net = c.breakdown?.net_cost ?? 0;
          const isCheapest = net === minCost;
          return `<div class="compare-card ${isCheapest ? 'cheapest' : ''}">
            <h4>${c.plan_name}</h4>
            <div class="retailer-name">${c.retailerName}</div>
            <div class="cost-amount">$${net.toFixed(2)}</div>
            <div class="cost-label">${isCheapest ? '★ Cheapest' : c.rate_type}</div>
          </div>`;
        }).join('')}
      </div>`;
  } catch (err) {
    results.innerHTML = `<p style="color:#dc2626">Error: ${err.message}</p>`;
  }
}

/* === Helpers === */
function populateSelect(id, items) {
  const sel = document.getElementById(id);
  if (!sel) return;
  sel.innerHTML = items.map(i => `<option value="${i.id}">${i.name || i.retailer_name || i.plan_name || ''}</option>`).join('');
}

function renderBreakdown(result) {
  const b = result.breakdown;
  if (!b) return '<p>No breakdown data</p>';
  const net = b.net_cost ?? 0;
  let itemsHtml = '';
  if (b.items && b.items.length) {
    itemsHtml = b.items.map(i => `<tr><td>${i.label}</td><td>${i.kwh.toFixed(2)} kWh × ${i.rate.toFixed(4)} c/kWh = <strong>$${i.cost.toFixed(2)}</strong></td></tr>`).join('');
  }
  return `<table class="breakdown-table">
    <tr><th>Item</th><th>Amount</th></tr>
    ${itemsHtml}
    <tr><td>Import cost</td><td>$${(b.import_cost ?? 0).toFixed(2)}</td></tr>
    ${b.daily_charges != null && b.daily_charges > 0 ? `<tr><td>Daily charges</td><td>$${b.daily_charges.toFixed(2)}</td></tr>` : ''}
    ${b.export_credit ? `<tr><td class="negative">Export credit</td><td class="negative">-$${Math.abs(b.export_credit).toFixed(2)}</td></tr>` : ''}
    <tr class="total"><td>Net cost (${b.total_days || ''} day${b.total_days !== 1 ? 's' : ''})</td><td>$${net.toFixed(2)}</td></tr>
  </table>
  <p style="font-size:.8rem;color:var(--text-secondary)">${result.retailer_name} — ${result.plan_name} (${result.rate_type})</p>`;
}
