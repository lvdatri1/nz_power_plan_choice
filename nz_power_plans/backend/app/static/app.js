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
    fetchJSON('/api/retailers').catch(() => []),
    fetchJSON('/api/plans').catch(() => []),
  ]);
  allRetailers = retailers;
  allPlans = plans;
}

async function fetchJSON(path) {
  const res = await fetch(`${API}${path}`);
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json();
}

async function fetchJSONTimeout(path, ms) {
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

async function postJSON(path, body) {
  const res = await fetch(`${API}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json();
}

/* === Navigation === */
function initNav() {
  document.querySelectorAll('[data-tab]').forEach(a => {
    a.addEventListener('click', e => {
      e.preventDefault();
      const tab = a.dataset.tab;
      document.querySelectorAll('[data-tab]').forEach(l => l.classList.remove('active'));
      a.classList.add('active');
      document.querySelectorAll('.tab-content').forEach(s => s.classList.remove('active'));
      document.getElementById(`tab-${tab}`).classList.add('active');
      if (tab === 'plans') renderPlans(allPlans);
    });
  });
}

/* === Dashboard === */
async function initDashboard() {
  const haStatus = await fetchJSONTimeout('/api/ha/status', 5000).catch(() => null);
  const haAlert = document.getElementById('ha-alert');
  const haInfo = document.getElementById('ha-info');
  const compareSection = document.getElementById('ha-compare-section');

  if (haStatus && haStatus.connected) {
    haAlert.className = 'alert alert-success';
    haAlert.textContent = `Connected — sensor: ${haStatus.sensor}`;
    haAlert.classList.remove('d-none');
    haInfo.classList.add('d-none');
    compareSection.classList.remove('d-none');
  } else if (haStatus && !haStatus.connected) {
    haAlert.className = 'alert alert-warning';
    haAlert.textContent = 'Home Assistant not connected (sensor not found)';
    haAlert.classList.remove('d-none');
    haInfo.classList.add('d-none');
    compareSection.classList.add('d-none');
  } else {
    haInfo.textContent = 'Not available (not running as HA add-on)';
    compareSection.classList.add('d-none');
  }

  populateSelect('dash-plan', plans => plans);
  document.getElementById('dash-calc').addEventListener('click', doDashCalc);
}

async function doDashCalc() {
  const planId = document.getElementById('dash-plan').value;
  const importKwh = parseFloat(document.getElementById('dash-import').value) || 0;
  const exportKwh = parseFloat(document.getElementById('dash-export').value) || 0;
  const usage = importKwh > 0 ? [{ timestamp: new Date().toISOString(), kwh: importKwh }] : [];
  try {
    const result = await postJSON('/api/cost/calculate', {
      plan_id: parseInt(planId), usage,
      include_export: exportKwh > 0,
      export_usage: exportKwh > 0 ? [{ timestamp: new Date().toISOString(), kwh: exportKwh }] : [],
    });
    document.getElementById('dash-result').innerHTML = renderBreakdown(result);
  } catch (err) {
    document.getElementById('dash-result').innerHTML = `<div class="alert alert-danger py-2">${err.message}</div>`;
  }
}

async function doHaCompare() {
  const days = parseInt(document.getElementById('ha-compare-days').value) || 30;
  const el = document.getElementById('ha-compare-result');
  el.innerHTML = '<div class="spinner-border spinner-border-sm me-2" role="status"></div> Comparing all plans…';
  try {
    const data = await fetchJSON(`/api/ha/compare?days=${days}`);
    if (!data.results || data.results.length === 0) {
      el.innerHTML = '<div class="alert alert-warning py-2">No plans to compare. Check sensor values.</div>';
      return;
    }
    el.innerHTML = `<p class="text-muted small mb-2">${data.import_kwh.toFixed(2)} kWh import, ${data.export_kwh.toFixed(2)} kWh export over ${days} days — <strong>${data.plans_compared}</strong> plans compared</p>${renderCompareTable(data.results)}`;
  } catch (err) {
    el.innerHTML = `<div class="alert alert-danger py-2">${err.message}</div>`;
  }
}

/* === Plans === */
function initPlans() {
  document.getElementById('filter-retailer').innerHTML = '<option value="">All Retailers</option>' +
    allRetailers.map(r => `<option value="${r.id}">${esc(r.name)}</option>`).join('');
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
  if (!plans.length) {
    grid.innerHTML = '<div class="text-muted">No plans found.</div>';
    return;
  }
  grid.innerHTML = plans.map(p => {
    const name = p.retailer?.name || p.retailer_name || '';
    return `<div class="col">
      <div class="card plan-card shadow-sm h-100" onclick="showPlanDetail(${p.id})">
        <div class="card-body">
          <h6 class="card-title mb-1">${esc(p.name)}</h6>
          <p class="card-text text-muted small mb-2">${esc(name)}</p>
          <span class="badge bg-primary">${p.rate_type}</span>
          ${p.daily_charge ? `<span class="text-muted small ms-2">$${p.daily_charge.toFixed(4)}/day</span>` : ''}
        </div>
      </div>
    </div>`;
  }).join('');
}

async function showPlanDetail(id) {
  const plan = await fetchJSON(`/api/plans/${id}`);
  document.getElementById('modal-title').textContent = plan.name;

  let html = `<p class="text-muted">${esc(plan.retailer?.name || '')}</p>`;
  html += `<p>Rate type: <strong>${plan.rate_type}</strong></p>`;
  if (plan.daily_charge) html += `<p>Daily charge: <strong>$${plan.daily_charge.toFixed(4)}/day</strong></p>`;

  const renderTable = (rows, cols) => {
    if (!rows || !rows.length) return '';
    return `<table class="table table-sm table-bordered mt-2">
      <thead class="table-light"><tr>${cols.map(c => `<th>${c}</th>`).join('')}</tr></thead>
      <tbody>${rows.join('')}</tbody>
    </table>`;
  };

  if (plan.rate_type === 'FLAT' && plan.flat_rates?.length) {
    html += `<h6 class="mt-3">Flat Rate</h6>`;
    html += renderTable(
      plan.flat_rates.map(r => `<tr><td>${esc(r.description || 'Standard')}</td><td>${r.rate_cents_per_kwh.toFixed(4)} c/kWh</td></tr>`),
      ['Description', 'Rate'],
    );
  }
  if (plan.rate_type === 'TIERED' && plan.tiered_rates?.length) {
    html += `<h6 class="mt-3">Tiered Rates</h6>`;
    html += renderTable(
      plan.tiered_rates.map(r => `<tr><td>${esc(r.tier_name || `Tier ${r.tier_order}`)}</td><td>${r.max_kwh ? `up to ${r.max_kwh} kWh` : 'unlimited'}</td><td>${r.rate_cents_per_kwh.toFixed(4)} c/kWh</td></tr>`),
      ['Tier', 'Threshold', 'Rate'],
    );
  }
  if (plan.rate_type === 'TOU') {
    if (plan.tou_rates?.length) {
      html += `<h6 class="mt-3">TOU Import Rates</h6>`;
      html += renderTable(
        plan.tou_rates.map(r => `<tr><td>${esc(r.period_name)}</td><td>${r.day_of_week || 'all'}</td><td>${r.start_hour}:00-${r.end_hour}:00</td><td>${r.rate_cents_per_kwh.toFixed(4)} c/kWh</td></tr>`),
        ['Period', 'Days', 'Time', 'Rate'],
      );
    }
    if (plan.tou_export_rates?.length) {
      html += `<h6 class="mt-3">TOU Export Rates</h6>`;
      html += renderTable(
        plan.tou_export_rates.map(r => `<tr><td>${esc(r.period_name)}</td><td>${r.day_of_week || 'all'}</td><td>${r.start_hour}:00-${r.end_hour}:00</td><td>${r.rate_cents_per_kwh.toFixed(4)} c/kWh</td></tr>`),
        ['Period', 'Days', 'Time', 'Rate'],
      );
    }
  }

  document.getElementById('modal-body').innerHTML = html;
  const modal = new bootstrap.Modal(document.getElementById('plan-modal'));
  modal.show();
}

/* === Calculator === */
function initCalculator() {
  const container = document.getElementById('calc-entries');
  addCalcRow(container, 8, 2);
  addCalcRow(container, 18, 5);
  document.getElementById('add-entry').addEventListener('click', () => addCalcRow(container));
  document.getElementById('calc-export-check').addEventListener('change', e => {
    const el = document.getElementById('calc-export-entries');
    el.classList.toggle('d-none', !e.target.checked);
    if (e.target.checked) addExportRow(el);
  });
  document.getElementById('calc-btn').addEventListener('click', doCalc);
  populateSelect('calc-plan', plans => plans);
}

function addCalcRow(container, hour, kwh) {
  const row = document.createElement('div');
  row.className = 'entry-row';
  row.innerHTML = `<input type="number" class="form-control form-control-sm" min="0" max="23" placeholder="Hour" value="${hour != null ? hour : ''}"><input type="number" class="form-control form-control-sm" step="0.01" placeholder="kWh" value="${kwh != null ? kwh : ''}">`;
  container.appendChild(row);
}

function addExportRow(container) {
  container.innerHTML = '';
  const row = document.createElement('div');
  row.className = 'entry-row';
  row.innerHTML = '<input type="number" class="form-control form-control-sm" min="0" max="23" placeholder="Hour"><input type="number" class="form-control form-control-sm" step="0.01" placeholder="kWh">';
  container.appendChild(row);
}

async function doCalc() {
  const planId = document.getElementById('calc-plan').value;
  const days = parseInt(document.getElementById('calc-daily').value) || 30;

  const usage = [];
  document.querySelectorAll('#calc-entries .entry-row').forEach(row => {
    const hour = parseInt(row.children[0].value);
    const kwh = parseFloat(row.children[1].value);
    if (!isNaN(kwh) && kwh > 0) {
      const d = new Date(); d.setHours(hour || 0, 0, 0, 0);
      usage.push({ timestamp: d.toISOString(), kwh });
    }
  });

  let exportUsage = [];
  if (document.getElementById('calc-export-check').checked) {
    document.querySelectorAll('#calc-export-entries .entry-row').forEach(row => {
      const hour = parseInt(row.children[0].value);
      const kwh = parseFloat(row.children[1].value);
      if (!isNaN(kwh) && kwh > 0) {
        const d = new Date(); d.setHours(hour || 0, 0, 0);
        exportUsage.push({ timestamp: d.toISOString(), kwh });
      }
    });
  }

  try {
    const result = await postJSON('/api/cost/calculate', { plan_id: parseInt(planId), usage, days, include_export: exportUsage.length > 0, export_usage: exportUsage });
    document.getElementById('calc-result-card').classList.remove('d-none');
    document.getElementById('calc-result').innerHTML = renderBreakdown(result);
  } catch (err) {
    document.getElementById('calc-result-card').classList.remove('d-none');
    document.getElementById('calc-result').innerHTML = `<div class="alert alert-danger py-2">${err.message}</div>`;
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
    document.getElementById('compare-results').innerHTML = '<div class="alert alert-warning py-2">Select at least 2 plans</div>';
    return;
  }

  const totalKwh = parseFloat(document.getElementById('compare-usage').value) || 300;
  const resultsEl = document.getElementById('compare-results');

  try {
    const costs = await Promise.all(selected.map(async planId => {
      const plan = await fetchJSON(`/api/plans/${planId}`);
      const result = await postJSON('/api/cost/calculate', {
        plan_id: planId, usage: [{ timestamp: new Date().toISOString(), kwh: totalKwh }], days: 30, include_export: false, export_usage: [],
      });
      return { ...result, retailerName: plan.retailer?.name || '' };
    }));

    const minCost = Math.min(...costs.map(c => c.breakdown?.net_cost ?? Infinity));
    resultsEl.innerHTML = `<p class="text-muted mb-3">Monthly cost for <strong>${totalKwh} kWh</strong>:</p>
      <div class="compare-grid">${costs.map(c => {
        const net = c.breakdown?.net_cost ?? 0;
        const isCheapest = net === minCost;
        return `<div class="card ${isCheapest ? 'cheapest-card border-success' : 'shadow-sm'}">
          <div class="card-body text-center">
            <h6 class="card-title">${esc(c.plan_name)}</h6>
            <p class="text-muted small">${esc(c.retailerName)}</p>
            <p class="display-6 text-primary fw-bold mb-1">$${net.toFixed(2)}</p>
            <p class="small ${isCheapest ? 'text-success fw-bold' : 'text-muted'}">${isCheapest ? '★ Cheapest' : c.rate_type}</p>
          </div>
        </div>`;
      }).join('')}</div>`;
  } catch (err) {
    resultsEl.innerHTML = `<div class="alert alert-danger py-2">${err.message}</div>`;
  }
}

/* === Helpers === */
function populateSelect(id, getItems) {
  const sel = document.getElementById(id);
  if (!sel) return;
  const items = typeof getItems === 'function' ? getItems(allPlans) : getItems;
  sel.innerHTML = items.map(i => `<option value="${i.id}">${esc(i.name || i.retailer_name || i.plan_name || '')}</option>`).join('');
}

function renderBreakdown(result) {
  const b = result.breakdown;
  if (!b) return '<div class="alert alert-warning py-2">No breakdown data</div>';
  const net = b.net_cost ?? 0;
  let rows = '';
  if (b.items && b.items.length) {
    rows = b.items.map(i => `<tr><td>${esc(i.label)}</td><td class="text-end">${i.kwh.toFixed(2)} kWh × ${i.rate.toFixed(4)} c/kWh</td><td class="text-end fw-medium">$${i.cost.toFixed(2)}</td></tr>`).join('');
  }
  return `<table class="table table-sm table-bordered mt-2">
    <thead class="table-light"><tr><th>Item</th><th class="text-end">Calculation</th><th class="text-end">Amount</th></tr></thead>
    <tbody>
      ${rows}
      <tr><td>Import cost</td><td></td><td class="text-end">$${(b.import_cost ?? 0).toFixed(2)}</td></tr>
      ${b.daily_charges != null && b.daily_charges > 0 ? `<tr><td>Daily charges</td><td></td><td class="text-end">$${b.daily_charges.toFixed(2)}</td></tr>` : ''}
      ${b.export_credit ? `<tr><td class="text-success">Export credit</td><td></td><td class="text-end text-success">-$${Math.abs(b.export_credit).toFixed(2)}</td></tr>` : ''}
      <tr class="table-active fw-bold"><td>Net cost (${b.total_days || ''} day${b.total_days !== 1 ? 's' : ''})</td><td></td><td class="text-end">$${net.toFixed(2)}</td></tr>
    </tbody>
  </table>
  <p class="text-muted small mb-0">${esc(result.retailer_name)} — ${esc(result.plan_name)} (${result.rate_type})</p>`;
}

function renderCompareTable(results) {
  const rows = results.map((r, i) => {
    const isCheapest = i === 0;
    return `<tr class="${isCheapest ? 'table-success' : ''}">
      <td>${isCheapest ? '★ ' : ''}${esc(r.retailer_name)}</td>
      <td>${esc(r.plan_name)}</td>
      <td>${r.rate_type}</td>
      <td>${r.has_export ? '✓' : '—'}</td>
      <td class="text-end">$${r.import_cost.toFixed(2)}</td>
      <td class="text-end">${r.export_credit > 0 ? '-$' + r.export_credit.toFixed(2) : '—'}</td>
      <td class="text-end">$${r.daily_charges.toFixed(2)}</td>
      <td class="text-end"><strong>$${r.net_cost.toFixed(2)}</strong></td>
      <td class="text-end"><strong>$${r.monthly_cost.toFixed(2)}</strong></td>
    </tr>`;
  }).join('');
  return `<div class="table-responsive"><table class="table table-sm table-hover">
    <thead class="table-light">
      <tr><th>Retailer</th><th>Plan</th><th>Type</th><th>Solar</th><th class="text-end">Import</th><th class="text-end">Export</th><th class="text-end">Daily</th><th class="text-end">Total</th><th class="text-end">/month</th></tr>
    </thead>
    <tbody>${rows}</tbody>
  </table></div>`;
}

function esc(s) {
  const d = document.createElement('div');
  d.textContent = s;
  return d.innerHTML;
}
