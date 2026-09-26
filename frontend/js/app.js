/**
 * app.js – Vyapaar Vikash Core Client & API Integration
 * Bridges all HTML pages to the certified SQLite backend API.
 */

// Determine API origin dynamically
const API_BASE = (window.location.port === '5000' || window.location.port === 5000)
  ? window.location.origin
  : 'http://localhost:5000';

  
// ── Shared API fetch wrapper ──────────────────────────
async function apiCall(endpoint, options = {}) {
  const url = endpoint.startsWith('http') ? endpoint : `${API_BASE}${endpoint}`;
  const defaultHeaders = { 'Content-Type': 'application/json' };
  options.headers = { ...defaultHeaders, ...(options.headers || {}) };
  options.credentials = 'include';

  try {
    const res = await fetch(url, options);
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      throw new Error(data.error || `HTTP error ${res.status}`);
    }
    return data;
  } catch (err) {
    console.warn(`[API] Error on ${endpoint}:`, err);
    throw err;
  }
}

// ── Currency & Metric formatters ─────────────────────
function formatINR(val) {
  const num = Number(val) || 0;
  return '₹' + num.toLocaleString('en-IN');
}

function getUrlParam(param) {
  const urlParams = new URLSearchParams(window.location.search);
  return urlParams.get(param);
}

function getActiveAnalysisId() {
  const paramId = getUrlParam('id');
  if (paramId) {
    sessionStorage.setItem('vv_active_id', paramId);
    return paramId;
  }
  return sessionStorage.getItem('vv_active_id') || localStorage.getItem('vv_active_id');
}

function setActiveAnalysisId(id) {
  if (id) {
    sessionStorage.setItem('vv_active_id', id);
    localStorage.setItem('vv_active_id', id);
  }
}

// ── Navbar & Authentication Hydration ────────────────
async function initNavbarAuth() {
  try {
    const me = await apiCall('/api/me');
    if (me && me.user) {
      const authLinks = document.querySelectorAll('.nav-links + .d-flex, .navbar-inner .d-flex');
      authLinks.forEach(container => {
        container.innerHTML = `
          <span style="font-size:0.85rem;color:var(--white);display:flex;align-items:center;gap:6px;">
            👤 <strong>${me.user.name}</strong>
          </span>
          <a href="${API_BASE}/pages/dashboard.html" class="btn btn-primary btn-sm">Workspace</a>
          <button id="btn-logout" class="btn btn-outline btn-sm" style="color:white;border-color:rgba(255,255,255,0.4);cursor:pointer;">Logout</button>
        `;
      });
      const logoutBtn = document.getElementById('btn-logout');
      if (logoutBtn) {
        logoutBtn.addEventListener('click', async () => {
          await apiCall('/api/logout', { method: 'POST' }).catch(() => {});
          window.location.href = `${API_BASE}/pages/login.html`;
        });
      }
    }
  } catch (_) {
    // User is guest, keep default Login button
  }
}

// ── Update sub-navigation tab links with active ID ───
function updateResultsNavLinks(activeId) {
  if (!activeId) return;
  const navLinks = document.querySelectorAll('.results-nav a');
  navLinks.forEach(link => {
    const href = link.getAttribute('href');
    if (href && !href.startsWith('#') && !href.includes('?')) {
      link.setAttribute('href', `${href}?id=${activeId}`);
    }
  });

  const sidebarLinks = document.querySelectorAll('.results-sidebar a, .results-layout a');
  sidebarLinks.forEach(link => {
    const href = link.getAttribute('href');
    if (href && href.startsWith('results-') && !href.includes('?')) {
      link.setAttribute('href', `${href}?id=${activeId}`);
    }
  });
}

// ── Common Results Header & Scorecard Hydration ─────
function hydrateCommonResultsHeader(analysis) {
  const meta = analysis.meta || {};
  const bizName = analysis.business_name || meta.business_name || 'My Enterprise';
  const bizType = analysis.business_type || meta.business_type || 'Enterprise';
  const state = analysis.state || meta.state || 'India';
  const district = analysis.district || meta.district || 'Local Area';
  const village = analysis.village || meta.village || '';
  const block = analysis.block || meta.block || '';
  const areaType = analysis.area_type || meta.area_type || 'rural';
  const areaLabel = meta.area_label || areaType.replace('_', ' ').toUpperCase();
  const investment = Number(analysis.total_investment || meta.total_investment || 100000);
  const certNo = analysis.certificate_no || 'CERT-VV-2026-LIVE';
  const score = analysis.feasibility_score || 75;
  const viability = analysis.viability_status || 'Viable — Recommended';

  const locDisplay = meta.location_display || (village && block ? `${village}, ${block}` : (village || block || district));
  const fullLocDisplay = meta.full_location_display || (locDisplay !== district ? `${locDisplay}, ${district}, ${state}` : `${district}, ${state}`);

  // Header Titles
  const titleEl = document.querySelector('.results-header h1');
  if (titleEl) titleEl.textContent = bizName;

  const headerSpan = document.querySelector('.results-header span');
  if (headerSpan) {
    headerSpan.innerHTML = `💼 ${bizType.toUpperCase()} · CERTIFIED FEASIBILITY REPORT · <span style="background:rgba(240,91,34,0.15);padding:3px 8px;border-radius:4px;color:var(--orange);">${certNo}</span>`;
  }

  // Header Meta Items
  const metaContainer = document.querySelector('.results-meta');
  if (metaContainer) {
    metaContainer.innerHTML = `
      <div class="results-meta-item">📍 <strong>${fullLocDisplay} (${areaLabel})</strong></div>
      <div class="results-meta-item">💼 <strong>${meta.business_label || bizType}</strong></div>
      <div class="results-meta-item">💰 <strong>${formatINR(investment)} Planned Capital</strong></div>
      <div class="results-meta-item">🛡️ <strong>Verified Protocol: ISO/MSME-NIESBUD</strong></div>
    `;
  }

  // Feasibility Score Sidebar
  const scoreVal = document.querySelector('.score-value');
  if (scoreVal) scoreVal.textContent = `${score} / 100`;

  const scoreTag = document.querySelector('.score-tag');
  if (scoreTag) {
    scoreTag.textContent = viability;
    scoreTag.className = score >= 70 ? 'score-tag' : 'score-tag' + (score < 55 ? ' score-low' : '');
  }

  // Score Bar tracks
  const mkt = analysis.market || {};
  const fin = analysis.financial || {};
  const demandPct = Math.min(100, Math.round((mkt.demand_score || 7.5) * 10));
  const finPct = Math.min(100, Math.round(score * 0.95));

  const scoreBars = document.querySelectorAll('.score-bars .score-bar-fill');
  if (scoreBars.length >= 4) {
    scoreBars[0].style.width = `${demandPct}%`;
    scoreBars[1].style.width = `${finPct}%`;
    scoreBars[2].style.width = `${Math.min(100, 110 - score)}%`;
    scoreBars[3].style.width = `80%`;
  }

  // Quick Numbers in Sidebar
  const quickSidebar = document.querySelector('.results-sidebar .card');
  if (quickSidebar && quickSidebar.querySelector('div[style*="flex-direction:column"]')) {
    const container = quickSidebar.querySelector('div[style*="flex-direction:column"]');
    container.innerHTML = `
      <div style="display:flex;justify-content:space-between;"><span style="color:var(--gray-600);">Annual Profit</span><strong style="color:var(--green);">${formatINR(fin.annual_profit || 180000)}</strong></div>
      <div style="display:flex;justify-content:space-between;"><span style="color:var(--gray-600);">Monthly Net</span><strong style="color:var(--green);">${formatINR(fin.monthly_profit || 15000)}</strong></div>
      <div style="display:flex;justify-content:space-between;"><span style="color:var(--gray-600);">Break-Even</span><strong>${fin.break_even_months || 12} Months</strong></div>
      <div style="display:flex;justify-content:space-between;"><span style="color:var(--gray-600);">ROI Per Annum</span><strong>${fin.roi_pct || 25}%</strong></div>
      <div style="display:flex;justify-content:space-between;"><span style="color:var(--gray-600);">Certificate</span><strong style="color:var(--orange);">${certNo}</strong></div>
    `;
  }
}

// ── Fetch active analysis data ───────────────────────
async function loadCurrentAnalysis() {
  const activeId = getActiveAnalysisId();
  try {
    let res;
    if (activeId) {
      res = await apiCall(`/api/analysis/${activeId}`);
    } else {
      res = await apiCall('/api/analysis/latest');
    }
    if (res && res.analysis) {
      setActiveAnalysisId(res.analysis.id);
      updateResultsNavLinks(res.analysis.id);
      return res.analysis;
    }
  } catch (err) {
    console.warn('[App] Could not load analysis record from database, falling back.', err);
  }
  return null;
}

// ─────────────────────────────────────────────────────
//  PAGE-SPECIFIC HYDRATION DISPATCHER
// ─────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', async () => {
  initNavbarAuth();

  const path = window.location.pathname;

  // 1. Analyse Form & Location Explorer Page
  if (path.includes('analyse.html') || path.includes('analyze.html')) {
    initOpportunityExplorer();
    setupAnalyseForm();
  }
  // 2. Results Overview Page
  else if (path.includes('results-overview.html')) {
    const analysis = await loadCurrentAnalysis();
    if (analysis) hydrateResultsOverview(analysis);
  }
  // 3. Market Page
  else if (path.includes('results-market.html')) {
    const analysis = await loadCurrentAnalysis();
    if (analysis) hydrateResultsMarket(analysis);
  }
  // 4. Competition Page
  else if (path.includes('results-competition.html')) {
    const analysis = await loadCurrentAnalysis();
    if (analysis) hydrateResultsCompetition(analysis);
  }
  // 5. SWOT Page
  else if (path.includes('results-swot.html')) {
    const analysis = await loadCurrentAnalysis();
    if (analysis) hydrateResultsSwot(analysis);
  }
  // 6. Financial Page
  else if (path.includes('results-financial.html')) {
    const analysis = await loadCurrentAnalysis();
    if (analysis) hydrateResultsFinancial(analysis);
  }
  // 7. Schemes Page
  else if (path.includes('results-schemes.html')) {
    const analysis = await loadCurrentAnalysis();
    if (analysis) hydrateResultsSchemes(analysis);
  }
  // 8. Action Plan Page
  else if (path.includes('results-action.html')) {
    const analysis = await loadCurrentAnalysis();
    if (analysis) hydrateResultsAction(analysis);
  }
  // 9. All-in-One Results Page
  else if (path.includes('results.html') && !path.includes('results-')) {
    const analysis = await loadCurrentAnalysis();
    if (analysis) hydrateResultsFull(analysis);
  }
  // 10. Dashboard Page
  else if (path.includes('dashboard.html')) {
    hydrateDashboard();
  }
  // 11. AI Advisor Page
  else if (path.includes('advisor.html')) {
    setupAdvisorPage();
  }
});

// ── 1. Setup Analyse Form ─────────────────────────────
function setupAnalyseForm() {
  const form = document.getElementById('analyze-form');
  if (!form) return;

  initLocationSelectors();

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const submitBtn = form.querySelector('button[type="submit"]');
    const originalBtnHtml = submitBtn ? submitBtn.innerHTML : 'Generate Analysis';
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.innerHTML = '⏳ Generating Certified Analysis & Saving to DB...';
    }

    const formData = new FormData(form);
    const payload = {};
    formData.forEach((value, key) => {
      payload[key] = value;
    });

    // Make sure radio business_type is captured
    const checkedRadio = form.querySelector('input[name="business_type"]:checked');
    if (checkedRadio) {
      payload.business_type = checkedRadio.value;
    }

    try {
      const res = await apiCall('/api/analysis', {
        method: 'POST',
        body: JSON.stringify(payload)
      });

      if (res && res.analysis_id) {
        setActiveAnalysisId(res.analysis_id);
        window.location.href = `results-overview.html?id=${res.analysis_id}`;
      } else {
        throw new Error('Analysis ID missing from response');
      }
    } catch (err) {
      alert('Error generating analysis: ' + err.message);
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalBtnHtml;
      }
    }
  });
}

// ── Cascading State -> District -> Block -> Village Selectors ──
function initLocationSelectors() {
  const stateSelect = document.getElementById('state');
  const districtSelect = document.getElementById('district');
  const districtHint = document.getElementById('district-hint');
  const blockInput = document.getElementById('block');
  const blockList = document.getElementById('block-list');
  const villageInput = document.getElementById('village');
  const villageList = document.getElementById('village-list');
  const areaTypeSelect = document.getElementById('area_type');
  const microHint = document.getElementById('micro-area-hint');

  if (!stateSelect || !districtSelect) return;

  // Helper: populate the district <select> from API
  async function loadDistricts(state, preserveValue) {
    districtSelect.disabled = true;
    if (districtHint) districtHint.textContent = '⏳ Loading districts…';
    try {
      const res = await apiCall(`/api/geo/districts?state=${encodeURIComponent(state)}`);
      districtSelect.innerHTML = '';
      if (res && res.districts && res.districts.length > 0) {
        res.districts.forEach(d => {
          const opt = document.createElement('option');
          opt.value = d.name;
          opt.textContent = d.name;
          if (preserveValue && d.name === preserveValue) opt.selected = true;
          districtSelect.appendChild(opt);
        });
        // If no preserved value matched, select first
        if (!preserveValue) districtSelect.selectedIndex = 0;
        if (districtHint) districtHint.textContent = `${res.count} districts available for ${state}`;
      } else {
        const opt = document.createElement('option');
        opt.value = '';
        opt.textContent = '— No districts found —';
        districtSelect.appendChild(opt);
        if (districtHint) districtHint.textContent = 'No districts found for selected state';
      }
    } catch (err) {
      console.warn('[Geo] Failed to load districts:', err);
      if (districtHint) districtHint.textContent = 'Could not load districts';
    } finally {
      districtSelect.disabled = false;
    }
  }

  // 1. State Change -> Fetch Districts
  stateSelect.addEventListener('change', async () => {
    const state = stateSelect.value;
    if (!state) return;
    if (blockInput) blockInput.value = '';
    if (villageInput) villageInput.value = '';
    await loadDistricts(state, null);
    handleDistrictChange();
  });

  // 2. District Change -> Fetch Sub-Areas & Preset Blocks/Villages
  const handleDistrictChange = async () => {
    const state = stateSelect.value;
    const district = districtSelect.value;
    if (!state || !district) return;

    try {
      const res = await apiCall(`/api/geo/sub_areas?state=${encodeURIComponent(state)}&district=${encodeURIComponent(district)}`);
      if (res && res.sub_areas) {
        const blocks = [...new Set(res.sub_areas.map(s => s.block_name).filter(Boolean))];
        const villages = [...new Set(res.sub_areas.map(s => s.village_name).filter(Boolean))];

        if (blockList && blocks.length > 0) {
          blockList.innerHTML = blocks.map(b => `<option value="${b}">`).join('');
        }
        if (villageList && villages.length > 0) {
          villageList.innerHTML = villages.map(v => `<option value="${v}">`).join('');
        }
      }
      updateMicroIntelligence();
    } catch (err) {
      console.warn('[Geo] Sub-area load note:', err);
    }
  };

  districtSelect.addEventListener('change', handleDistrictChange);


  // 3. Auto-detect Archetype & Update Micro Hint
  const updateMicroIntelligence = async () => {
    const state = stateSelect.value || '';
    const district = districtSelect.value || '';
    const block = blockInput ? blockInput.value.trim() : '';
    const village = villageInput ? villageInput.value.trim() : '';
    let areaType = areaTypeSelect ? areaTypeSelect.value : 'rural';

    const textToMatch = `${village} ${block}`.toLowerCase();
    if (areaTypeSelect && (!areaTypeSelect.value || areaTypeSelect.value === 'rural')) {
      if (textToMatch.includes('mandi') || textToMatch.includes('krishi') || textToMatch.includes('agro')) {
        areaTypeSelect.value = 'agro_cluster';
        areaType = 'agro_cluster';
      } else if (textToMatch.includes('highway') || textToMatch.includes('bypass') || textToMatch.includes('junction')) {
        areaTypeSelect.value = 'highway_junction';
        areaType = 'highway_junction';
      } else if (textToMatch.includes('ward') || textToMatch.includes('nagar') || textToMatch.includes('city')) {
        areaTypeSelect.value = 'urban';
        areaType = 'urban';
      } else if (textToMatch.includes('town') || textToMatch.includes('bazaar') || textToMatch.includes('market')) {
        areaTypeSelect.value = 'semi_urban';
        areaType = 'semi_urban';
      }
    }

    if (microHint && (village || district)) {
      try {
        const intelRes = await apiCall(`/api/geo/intelligence?state=${encodeURIComponent(state)}&district=${encodeURIComponent(district)}&village=${encodeURIComponent(village)}&block=${encodeURIComponent(block)}&area_type=${encodeURIComponent(areaType)}`);
        if (intelRes && intelRes.intelligence) {
          const intel = intelRes.intelligence;
          microHint.innerHTML = `📍 <strong>${intel.location_title} (${intel.area_label})</strong>: Serviceable catchment ${intel.catchment_radius_km} km radius (${intel.catchment_population}) · Avg. Commercial Rent ~₹${intel.avg_sqft_rent}/sqft.`;
        }
      } catch (_) {}
    }
  };

  if (blockInput) {
    blockInput.addEventListener('change', updateMicroIntelligence);
    blockInput.addEventListener('input', updateMicroIntelligence);
  }
  if (villageInput) {
    villageInput.addEventListener('change', updateMicroIntelligence);
    villageInput.addEventListener('input', updateMicroIntelligence);
  }
  if (areaTypeSelect) {
    areaTypeSelect.addEventListener('change', updateMicroIntelligence);
  }

  // Initial load: populate districts for the default state on page load
  const defaultState = stateSelect.value;
  if (defaultState) {
    loadDistricts(defaultState, districtSelect.options[0] ? districtSelect.options[0].value : null).then(() => {
      handleDistrictChange();
    });
  }
}

// ── 2. Hydrate Results Overview ──────────────────────
function hydrateResultsOverview(analysis) {
  hydrateCommonResultsHeader(analysis);

  // AI Verdict Banner
  const verdictBanner = document.querySelector('.results-layout main div[style*="linear-gradient"]');
  if (verdictBanner) {
    const h2 = verdictBanner.querySelector('h2');
    const p = verdictBanner.querySelector('p');
    if (h2) h2.textContent = `Verdict: ${analysis.viability_status || 'Viable'}`;
    if (p) p.innerHTML = analysis.ai_verdict || '';
  }

  // Summary Cards
  const mkt = analysis.market || {};
  const fin = analysis.financial || {};
  const swot = analysis.swot || {};

  // Financial summary numbers on Overview card
  const finMonthlyProfit = document.getElementById('overview-monthly-profit');
  if (finMonthlyProfit) finMonthlyProfit.textContent = formatINR(fin.monthly_profit);

  const finMonthlyRev = document.getElementById('overview-monthly-revenue');
  if (finMonthlyRev) finMonthlyRev.textContent = formatINR(fin.monthly_revenue);

  const finBe = document.getElementById('overview-breakeven');
  if (finBe) finBe.textContent = fin.break_even_display || (fin.break_even_months ? `${Math.max(1, fin.break_even_months - 1)}–${fin.break_even_months + 1} months` : '10–12 months');

  const finMargin = document.getElementById('overview-margin');
  if (finMargin) {
    const marginPct = fin.net_profit_margin_pct || Math.min(99, Math.max(5, Math.round((fin.monthly_profit / (fin.monthly_revenue || 1)) * 100)));
    finMargin.textContent = `${marginPct}%`;
  }
}

// ── 3. Hydrate Results Market ─────────────────────────
function hydrateResultsMarket(analysis) {
  hydrateCommonResultsHeader(analysis);
  const mkt = analysis.market || {};
  const meta = analysis.meta || {};
  const dist = analysis.district || meta.district || 'your area';
  const state = analysis.state || meta.state || 'India';
  const bizLabel = meta.business_label || analysis.business_type || 'Enterprise';
  const areaLabel = mkt.area_label || meta.area_type || 'Local Area';

  // Update Section Label
  const sectionLabel = document.querySelector('.section-label');
  if (sectionLabel && mkt.local_demand) {
    sectionLabel.textContent = `Hyper-Local Insights · ${dist}, ${state} · ${mkt.local_demand}`;
  }

  // Update Customer Base and Market Insights Cards
  const cards = document.querySelectorAll('.results-layout main .card');
  if (cards.length >= 2) {
    const list1 = cards[0].querySelector('ul');
    if (list1) {
      list1.innerHTML = `
        <li>🏘️ <strong>Hyper-local market size:</strong> ${mkt.market_size_cr || 1.2} Cr INR potential</li>
        <li>📈 <strong>Annual Growth Rate:</strong> ${mkt.growth_rate_pct || 8.5}% CAGR nationally</li>
        <li>🎯 <strong>Target Segment:</strong> ${mkt.target_segment?.primary || 'Local households and daily consumers'}</li>
        <li>📍 <strong>Serviceable Radius:</strong> ${mkt.target_segment?.reach_km || 5} km direct cluster</li>
        <li>📱 <strong>Demand Rating:</strong> ${mkt.demand_score || 7.5} / 10 Feasibility Index</li>
      `;
    }

    const list2 = cards[1].querySelector('ul');
    if (list2 && mkt.market_insights) {
      list2.innerHTML = mkt.market_insights.map(item => `<li>✅ ${item}</li>`).join('');
    }
  }

  // Dynamic Demand Drivers Header & Grid
  const driversTitle = document.getElementById('demand-drivers-title');
  if (driversTitle) {
    driversTitle.textContent = `Why ${bizLabel} Succeeds in ${areaLabel} (${dist}, ${state})`;
  }

  const driversGrid = document.getElementById('demand-drivers-grid');
  if (driversGrid && mkt.demand_drivers && mkt.demand_drivers.length > 0) {
    driversGrid.innerHTML = mkt.demand_drivers.map(d => `
      <div style="background:var(--gray-100);border-radius:var(--radius-sm);padding:16px;">
        <div style="font-size:1.4rem;margin-bottom:8px;">${d.icon || '📈'}</div>
        <h4 style="font-size:0.88rem;font-weight:700;color:var(--navy);margin-bottom:6px;">${d.title}</h4>
        <p style="font-size:0.8rem;color:var(--gray-600);">${d.desc}</p>
      </div>
    `).join('');
  }

  // Dynamic Recommended Product/Service Mix with Priorities & Rationales
  const mixContainer = document.getElementById('product-mix-container');
  if (mixContainer && mkt.product_service_mix && mkt.product_service_mix.length > 0) {
    mixContainer.innerHTML = mkt.product_service_mix.map((item, idx) => `
      <div style="display:flex;justify-content:space-between;align-items:flex-start;padding:14px 0;border-bottom:${idx === mkt.product_service_mix.length - 1 ? 'none' : 'var(--border)'};">
        <div style="flex:1;padding-right:16px;">
          <strong style="font-size:0.92rem;color:var(--navy);">${item.title}</strong>
          <p style="font-size:0.82rem;color:var(--gray-600);margin:4px 0 3px;">${item.desc}</p>
          <p style="font-size:0.78rem;color:var(--orange);font-weight:600;margin:0;">💡 Why Prioritized: ${item.rationale}</p>
        </div>
        <span class="tag ${item.priority_tag || 'tag-green'}" style="margin-top:2px;white-space:nowrap;flex-shrink:0;">${item.priority}</span>
      </div>
    `).join('');
  }
}

// ── 4. Hydrate Results Competition ────────────────────
function hydrateResultsCompetition(analysis) {
  hydrateCommonResultsHeader(analysis);
  const comp = analysis.competition || {};
  const meta = analysis.meta || {};
  const dist = analysis.district || meta.district || 'Cuttack';
  const state = analysis.state || meta.state || 'Odisha';
  const bizLabel = meta.business_label || analysis.business_type || 'Enterprise';
  const bizType = analysis.business_type || meta.business_type || 'business';

  // Prefer village > block > town > district for pinpoint map accuracy
  const village = meta.village || meta.block || meta.town || '';
  const preciseLocation = village ? `${village}, ${dist}` : dist;
  const locationDisplay = village ? `${village}, ${dist}, ${state}` : `${dist}, ${state}`;
  const mapZoom = village ? 14 : 12; // Zoom in more if we have village-level data

  // Section label & Map title
  const secLabel = document.getElementById('comp-section-label');
  if (secLabel) secLabel.textContent = `Real-Time Geographic Competition Data · ${locationDisplay}`;

  const mapTitle = document.getElementById('comp-map-title');
  if (mapTitle) mapTitle.textContent = `Nearby ${bizLabel} Providers Within ${village ? '5km' : '10km'} — ${locationDisplay}`;

  // Map info box
  const mapInfo = document.getElementById('comp-map-info');
  if (mapInfo) {
    mapInfo.innerHTML = `
      <span style="font-size:1.2rem;flex-shrink:0;">ℹ️</span>
      <span>The map below displays <strong>real ${bizLabel.toLowerCase()} providers near ${locationDisplay}</strong> from Google Maps. This reflects your specific ${village ? 'village/town' : 'district'} and enterprise category. Zoom in to inspect the closest competitors, their operating hours, and customer reviews.</span>
    `;
  }

  // Update Google Maps embed — uses village/town for pinpoint competitor search
  const iframe = document.getElementById('comp-map-iframe') || document.querySelector('iframe.map-frame');
  if (iframe) {
    const query = encodeURIComponent(`${bizLabel} near ${preciseLocation} ${state}`);
    iframe.src = `https://maps.google.com/maps?q=${query}&t=m&z=${mapZoom}&ie=UTF8&iwloc=B&output=embed`;
    iframe.title = `${bizLabel} near ${locationDisplay}`;
  }

  // Map caption
  const mapCaption = document.getElementById('comp-map-caption');
  if (mapCaption) {
    mapCaption.textContent = `🔴 Red pins = ${bizLabel.toLowerCase()} competitors within ${village ? '5km' : '10km'} of ${locationDisplay}. Click a marker for name, hours & reviews.`;
  }

  // External link
  const extLink = document.getElementById('comp-map-external-link');
  if (extLink) {
    extLink.href = `https://www.google.com/maps/search/${encodeURIComponent(bizLabel + ' near ' + preciseLocation + ' ' + state)}`;
  }

  // AI Recommendation Card
  const aiRec = document.getElementById('comp-ai-rec');
  if (aiRec && comp.ai_recommendation) {
    aiRec.innerHTML = comp.ai_recommendation;
  }

  // Competitor Table
  const tableBody = document.getElementById('comp-table-body');
  if (tableBody && comp.competitors && comp.competitors.length > 0) {
    tableBody.innerHTML = comp.competitors.map(c => `
      <tr>
        <td><strong>${c.name}</strong><br><span style="font-size:0.78rem;color:var(--gray-600);">${dist} Market</span></td>
        <td>${c.distance}</td>
        <td>${c.services}</td>
        <td class="comp-gap">${c.gaps}</td>
        <td class="comp-pro">${c.pros}</td>
      </tr>
    `).join('');
  }

  // Market Gap Box
  const marketGap = document.getElementById('comp-market-gap');
  if (marketGap && comp.market_gap) {
    marketGap.textContent = comp.market_gap;
  }
}

// ── 5. Hydrate Results SWOT ───────────────────────────
function hydrateResultsSwot(analysis) {
  hydrateCommonResultsHeader(analysis);
  const swot = analysis.swot || {};

  const fillList = (selector, items) => {
    const cell = document.querySelector(selector);
    if (!cell) return;
    const ul = cell.querySelector('ul');
    if (ul && items && items.length > 0) {
      ul.innerHTML = items.map(item => `<li>${item}</li>`).join('');
    }
  };

  fillList('.swot-cell.s', swot.strengths);
  fillList('.swot-cell.w', swot.weaknesses);
  fillList('.swot-cell.o', swot.opportunities);
  fillList('.swot-cell.t', swot.threats);

  // Dynamic AI Strategy Recommendations
  const stratContainer = document.getElementById('swot-strategy-recs');
  if (stratContainer && swot.strategy_recommendations) {
    const r = swot.strategy_recommendations;
    stratContainer.innerHTML = `
      <div><strong>To maximize Strengths:</strong> ${r.maximize_strengths || 'Leverage high local demand and community word-of-mouth.'}</div>
      <div><strong>To minimize Weaknesses:</strong> ${r.minimize_weaknesses || 'Adopt digital inventory management and negotiate 15-day supplier credit.'}</div>
      <div><strong>To capture Opportunities:</strong> ${r.capture_opportunities || 'Introduce WhatsApp Business ordering and high-margin complementary offerings.'}</div>
      <div><strong>To counter Threats:</strong> ${r.counter_threats || 'Provide verified quality guarantees and personal customer care that distant competitors cannot match.'}</div>
    `;
  }

  // Key Insight in Sidebar
  const keyInsight = document.getElementById('swot-key-insight');
  if (keyInsight && swot.key_insight) {
    keyInsight.textContent = swot.key_insight;
  }
}

// ── 6. Hydrate Results Financial ──────────────────────
function hydrateResultsFinancial(analysis) {
  hydrateCommonResultsHeader(analysis);
  const fin = analysis.financial || {};
  const meta = analysis.meta || {};
  const invest = Number(analysis.total_investment || meta.total_investment || fin.investment || 100000);
  const bizLabel = meta.business_label || analysis.business_type || 'Enterprise';
  const bizName = analysis.business_name || meta.business_name || 'My Enterprise';

  // Update Page Title and Header
  const titleEl = document.querySelector('.results-header h1');
  if (titleEl) titleEl.textContent = `Financial Plan — ${formatINR(invest)} Investment`;

  const headerSpan = document.querySelector('.results-header span');
  if (headerSpan) headerSpan.textContent = `💰 ${bizLabel} · Financial Feasibility`;

  const beDisplay = fin.break_even_display || (fin.break_even_months ? `${Math.max(1, fin.break_even_months - 1)}–${fin.break_even_months + 1} Months` : '10–12 Months');

  // Update Header Meta Pills specifically for Financial page
  const metaContainer = document.querySelector('.results-meta');
  if (metaContainer) {
    metaContainer.innerHTML = `
      <div class="results-meta-item">💰 <strong>Total Investment: ${formatINR(invest)}</strong></div>
      <div class="results-meta-item">📈 <strong>Est. Monthly Profit: ${formatINR(fin.monthly_profit)}</strong></div>
      <div class="results-meta-item">⏱️ <strong>Break-Even: ${beDisplay}</strong></div>
    `;
  }

  // Update Section Label & Startup Title
  const secLabel = document.getElementById('fin-section-label');
  if (secLabel) secLabel.textContent = `Financial Structuring · Based on ${formatINR(invest)} Investment · ${bizLabel}`;

  const startupTitle = document.getElementById('fin-startup-title');
  if (startupTitle) startupTitle.textContent = `Where Does Your ${formatINR(invest)} Go?`;

  // Startup Cost Breakdown Rows
  const startupContainer = document.getElementById('fin-startup-container');
  if (startupContainer && fin.startup_costs && fin.startup_costs.length > 0) {
    startupContainer.innerHTML = fin.startup_costs.map(item => `
      <div class="fin-row">
        <div>
          <strong style="font-size:0.9rem;">${item.icon || '📦'} ${item.name}</strong>
          <div class="progress-bar"><div class="progress-fill" style="width:${item.pct}%;"></div></div>
        </div>
        <strong style="color:var(--navy);white-space:nowrap;margin-left:16px;">${item.formatted_amount}</strong>
      </div>
    `).join('');
  }

  // Monthly Expenses Breakdown
  const expensesContainer = document.getElementById('fin-expenses-container');
  if (expensesContainer && fin.monthly_expenses_breakdown && fin.monthly_expenses_breakdown.length > 0) {
    const itemsHtml = fin.monthly_expenses_breakdown.map(e => `
      <div style="display:flex;justify-content:space-between;">
        <span style="color:var(--gray-600);">${e.name}</span>
        <strong>${e.formatted_amount}</strong>
      </div>
    `).join('');
    const totalHtml = `
      <div style="display:flex;justify-content:space-between;padding-top:10px;border-top:var(--border);">
        <span style="font-weight:700;">Total Monthly Cost</span>
        <strong id="fin-expenses-total" style="color:var(--red);">${formatINR(fin.monthly_fixed_cost)}</strong>
      </div>
    `;
    expensesContainer.innerHTML = itemsHtml + totalHtml;
  }

  // Monthly Revenue Breakdown
  const revenueContainer = document.getElementById('fin-revenue-container');
  if (revenueContainer && fin.monthly_revenue_breakdown && fin.monthly_revenue_breakdown.length > 0) {
    const itemsHtml = fin.monthly_revenue_breakdown.map(r => `
      <div style="display:flex;justify-content:space-between;">
        <span style="color:var(--gray-600);">${r.name}</span>
        <strong>${r.formatted_amount}</strong>
      </div>
    `).join('');
    const totalHtml = `
      <div style="display:flex;justify-content:space-between;padding-top:10px;border-top:var(--border);">
        <span style="font-weight:700;">Total Monthly Revenue</span>
        <strong id="fin-revenue-total" style="color:var(--green);">${formatINR(fin.monthly_revenue)}</strong>
      </div>
    `;
    revenueContainer.innerHTML = itemsHtml + totalHtml;
  }

  // Financial Summary 6-Grid
  const summaryGrid = document.getElementById('fin-summary-grid');
  if (summaryGrid) {
    const marginPct = fin.net_profit_margin_pct || Math.min(99, Math.max(5, Math.round((fin.monthly_profit / (fin.monthly_revenue || 1)) * 100)));
    summaryGrid.innerHTML = `
      <div class="finance-item"><div class="finance-item-label">Total Investment</div><div class="finance-item-value">${formatINR(invest)}</div></div>
      <div class="finance-item"><div class="finance-item-label">Monthly Revenue</div><div class="finance-item-value">${formatINR(fin.monthly_revenue)}</div></div>
      <div class="finance-item"><div class="finance-item-label">Monthly Expenses</div><div class="finance-item-value">${formatINR(fin.monthly_fixed_cost)}</div></div>
      <div class="finance-item"><div class="finance-item-label">Monthly Profit</div><div class="finance-item-value positive">${formatINR(fin.monthly_profit)}</div></div>
      <div class="finance-item"><div class="finance-item-label">Profit Margin</div><div class="finance-item-value positive">${marginPct}%</div></div>
      <div class="finance-item"><div class="finance-item-label">Break-Even</div><div class="finance-item-value">${beDisplay}</div></div>
    `;
  }

  // Year 1 Growth Projection Table
  const year1Body = document.getElementById('fin-year1-table-body');
  if (year1Body && fin.year1_table && fin.year1_table.length > 0) {
    year1Body.innerHTML = fin.year1_table.map((row, idx) => `
      <tr style="border-bottom:var(--border);${idx % 2 === 1 ? 'background:var(--gray-100);' : ''}">
        <td style="padding:10px 14px;font-weight:${idx === fin.year1_table.length - 1 ? '700' : '500'};">${row.period}</td>
        <td style="padding:10px 14px;text-align:right;">${row.formatted_rev}</td>
        <td style="padding:10px 14px;text-align:right;color:var(--green);font-weight:700;">${row.formatted_profit}</td>
        <td style="padding:10px 14px;text-align:right;color:var(--navy);font-weight:600;">${row.formatted_recovered}</td>
      </tr>
    `).join('');
  }

  // Sidebar Financial Metrics
  const finScore = document.getElementById('fin-sidebar-score');
  if (finScore && analysis.feasibility_score) finScore.textContent = `Score: ${analysis.feasibility_score}/100`;

  const finViability = document.getElementById('fin-sidebar-viability');
  if (finViability) {
    const s = analysis.feasibility_score || 72;
    finViability.textContent = s >= 80 ? 'EXCELLENT' : (s >= 65 ? 'GOOD' : 'MODERATE');
  }

  const marginPctVal = fin.net_profit_margin_pct || Math.min(99, Math.max(5, Math.round((fin.monthly_profit / (fin.monthly_revenue || 1)) * 100)));
  const marginLabel = document.getElementById('fin-sidebar-margin-label');
  if (marginLabel) marginLabel.textContent = `${marginPctVal}%`;
  const marginFill = document.getElementById('fin-sidebar-margin-fill');
  if (marginFill) marginFill.style.width = `${Math.min(100, marginPctVal)}%`;

  const sideMonthlyProfit = document.getElementById('fin-sidebar-monthly-profit');
  if (sideMonthlyProfit) sideMonthlyProfit.textContent = formatINR(fin.monthly_profit);

  const sideAnnualIncome = document.getElementById('fin-sidebar-annual-income');
  if (sideAnnualIncome) {
    const ann = fin.annual_profit || (fin.monthly_profit * 12);
    sideAnnualIncome.textContent = `${formatINR(ann)}/year`;
  }

  const sideBe = document.getElementById('fin-sidebar-breakeven');
  if (sideBe) {
    sideBe.textContent = beDisplay;
  }

  const sideRoi = document.getElementById('fin-sidebar-roi');
  if (sideRoi) {
    sideRoi.textContent = `${fin.roi_pct || Math.round(((fin.annual_profit || (fin.monthly_profit * 12)) / (invest || 1)) * 100)}%`;
  }
}

// ── 7. Hydrate Results Schemes ────────────────────────
function hydrateResultsSchemes(analysis) {
  hydrateCommonResultsHeader(analysis);
  const sch = analysis.schemes || {};
  const meta = analysis.meta || {};
  const schemeList = document.querySelector('.scheme-list');
  if (!schemeList || !sch.schemes) return;

  // Derive location label for personalized text
  const village = meta.village || meta.block || '';
  const dist = analysis.district || meta.district || 'your district';
  const state = analysis.state || meta.state || 'Odisha';
  const bizLabel = meta.business_label || analysis.business_type || 'enterprise';
  const areaLabel = { rural: 'rural', semi_urban: 'semi-urban', urban_outskirts: 'urban outskirts', urban: 'urban' }[meta.area_type || 'rural'] || 'local';
  const invest = Number(meta.total_investment || analysis.total_investment || 0);
  const locationFull = village ? `${village}, ${dist}` : dist;

  schemeList.innerHTML = sch.schemes.map((s, idx) => {
    const portalUrl = s.portal_url || s.url || '#';
    const subsidyDisplay = s.formatted_subsidy || (s.calculated_subsidy_amount ? formatINR(s.calculated_subsidy_amount) : 'Collateral-Free');
    const yourBenefit = s.your_benefit || subsidyDisplay;
    const bankPartner = s.bank_partner || 'SIDBI, PSU Banks';
    const applyVia = s.apply_via || portalUrl;

    // Eligibility description paragraph (personalized)
    const eligDesc = (() => {
      if (idx === 0 || s.key === 'PMEGP') {
        const pct = s.subsidy_rate_rural ? Math.round(s.subsidy_rate_rural * 100) : 35;
        return `Your ${bizLabel} in ${areaLabel} ${dist} qualifies as a micro-enterprise under ${s.name.split('(')[0].trim()}. You can get a ${pct}% margin money subsidy on your total project cost of ₹${(invest / 100000).toFixed(1)} Lakh.`;
      }
      return `Your ${bizLabel} in ${locationFull}, ${state} meets the eligibility requirements for this scheme. ${s.eligibility || ''}`;
    })();

    // Why You're Eligible checklist
    const eligibilityReasons = s.eligibility_reasons || [];
    const eligChecklist = eligibilityReasons.length > 0 ? `
      <div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:10px;padding:18px;margin-bottom:18px;">
        <div style="font-size:0.82rem;font-weight:700;color:#166534;margin-bottom:12px;display:flex;align-items:center;gap:6px;">
          <span>✅</span> Why You're Eligible:
        </div>
        <div style="display:flex;flex-direction:column;gap:8px;">
          ${eligibilityReasons.map(r => `
            <div style="display:flex;align-items:flex-start;gap:10px;">
              <span style="color:${r.check ? '#16a34a' : '#ef4444'};font-size:1rem;flex-shrink:0;margin-top:1px;">${r.check ? '✅' : '❌'}</span>
              <span style="font-size:0.86rem;color:${r.check ? '#166534' : '#b91c1c'};line-height:1.5;">${r.text}</span>
            </div>
          `).join('')}
        </div>
      </div>
    ` : `
      <div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:10px;padding:14px;margin-bottom:18px;">
        <div style="font-size:0.82rem;font-weight:700;color:#166534;margin-bottom:8px;">✅ Why You're Eligible:</div>
        <p style="font-size:0.86rem;color:#166534;margin:0;line-height:1.5;">${s.eligibility || 'Your business profile meets the primary eligibility requirements for this scheme.'}</p>
      </div>
    `;

    // Bottom benefit row (Subsidy | Your Benefit | Bank Partner | Apply Via)
    const benefitRow = `
      <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:20px;padding-top:16px;border-top:1px solid var(--gray-200);">
        <div>
          <div style="font-size:0.72rem;color:var(--gray-400);text-transform:uppercase;letter-spacing:0.04em;margin-bottom:4px;">Subsidy</div>
          <div style="font-size:0.84rem;font-weight:600;color:var(--gray-700);">${s.subsidy || subsidyDisplay}</div>
        </div>
        <div>
          <div style="font-size:0.72rem;color:var(--gray-400);text-transform:uppercase;letter-spacing:0.04em;margin-bottom:4px;">Your Benefit</div>
          <div style="font-size:0.9rem;font-weight:700;color:#16a34a;">${yourBenefit}</div>
        </div>
        <div>
          <div style="font-size:0.72rem;color:var(--gray-400);text-transform:uppercase;letter-spacing:0.04em;margin-bottom:4px;">Bank Partner</div>
          <div style="font-size:0.84rem;font-weight:600;color:var(--gray-700);">${bankPartner}</div>
        </div>
        <div>
          <div style="font-size:0.72rem;color:var(--gray-400);text-transform:uppercase;letter-spacing:0.04em;margin-bottom:4px;">Apply Via</div>
          <a href="${applyVia}" target="_blank" rel="noopener noreferrer" style="font-size:0.84rem;font-weight:700;color:var(--orange);text-decoration:none;display:inline-flex;align-items:center;gap:4px;">
            ${applyVia.replace('https://', '').split('/')[0]} ↗
          </a>
        </div>
      </div>
    `;

    return `
      <div class="scheme-card" style="margin-bottom:24px;border:1px solid var(--gray-200);border-radius:var(--radius-md);background:white;padding:24px;box-shadow:0 2px 8px rgba(0,0,0,0.04);">
        <div class="scheme-card-header" style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;margin-bottom:10px;">
          <h3 class="scheme-card-title" style="font-size:1.1rem;font-weight:700;color:var(--navy);margin:0;">${idx + 1}. ${s.name}</h3>
          <span class="tag tag-green" style="white-space:nowrap;font-size:0.8rem;background:#dcfce7;color:#166534;padding:4px 12px;border-radius:20px;font-weight:600;">✓ Eligible</span>
        </div>

        <p style="color:var(--gray-600);font-size:0.88rem;line-height:1.6;margin:0 0 16px;">${eligDesc}</p>

        ${eligChecklist}

        ${benefitRow}
      </div>
    `;
  }).join('');

  // Combined Scheme Benefit Box
  const combBox = document.getElementById('scheme-combined-benefit');
  if (combBox && sch.combined_benefit) {
    combBox.textContent = sch.combined_benefit;
  }
}


// ── 8. Hydrate Results Action Plan ────────────────────
function hydrateResultsAction(analysis) {
  hydrateCommonResultsHeader(analysis);
  const act = analysis.action_plan || {};
  const meta = analysis.meta || {};
  const dist = analysis.district || meta.district || 'Cuttack';
  const state = analysis.state || meta.state || 'Odisha';
  const bizLabel = meta.business_label || analysis.business_type || 'Enterprise';

  // Section Label
  const secLabel = document.getElementById('action-section-label');
  if (secLabel) secLabel.textContent = `Step-by-Step Business Launch Plan · ${bizLabel} · ${dist}, ${state}`;

  // Action Steps Container
  const container = document.getElementById('action-steps-container');
  if (container && act.timeline && act.timeline.length > 0) {
    container.innerHTML = act.timeline.map((phase, pIdx) => `
      <div style="font-size:0.78rem;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:var(--gray-400);margin:14px 0 10px;">${phase.timeframe || '📅 PHASE ' + (pIdx + 1)}</div>
      <div class="action-step">
        <div class="step-badge">${pIdx + 1}</div>
        <div style="flex:1;">
          <h3 style="font-size:1.05rem;font-weight:700;color:var(--navy);margin-bottom:6px;">${phase.title || phase.phase}</h3>
          <p style="font-size:0.88rem;color:var(--gray-600);line-height:1.7;margin-bottom:12px;">${phase.desc || ''}</p>
          
          ${phase.badges ? `
            <div style="display:flex;gap:10px;flex-wrap:wrap;margin-bottom:12px;">
              ${phase.badges.map(b => `<span style="background:var(--gray-100);padding:5px 12px;border-radius:50px;font-size:0.78rem;font-weight:600;color:var(--navy);">${b}</span>`).join('')}
            </div>
          ` : ''}

          <div style="background:white;border:1px solid var(--gray-200);border-radius:var(--radius-sm);padding:14px 16px;">
            <div style="font-size:0.8rem;font-weight:700;color:var(--navy);margin-bottom:8px;">Action Checklist:</div>
            <ul style="font-size:0.84rem;color:var(--gray-700);display:flex;flex-direction:column;gap:6px;padding-left:18px;margin:0;">
              ${(phase.tasks || []).map(t => `<li>${t}</li>`).join('')}
            </ul>
          </div>
        </div>
      </div>
      ${pIdx < act.timeline.length - 1 ? '<div class="timeline-line"></div>' : ''}
    `).join('');
  }
}

// ── 9. Hydrate Combined Full Results ─────────────────
function hydrateResultsFull(analysis) {
  hydrateCommonResultsHeader(analysis);
  hydrateResultsOverview(analysis);
  hydrateResultsMarket(analysis);
  hydrateResultsCompetition(analysis);
  hydrateResultsSwot(analysis);
  hydrateResultsFinancial(analysis);
  hydrateResultsSchemes(analysis);
  hydrateResultsAction(analysis);
}

// ── 10. Legacy Hydrate Dashboard (Old Analyses-only view) ───────────────────────
// NOTE: Renamed to avoid overriding the new full-workspace hydrateDashboard (defined later).
async function _legacyHydrateDashboard_disabled() {
  try {
    const [analysesRes, statsRes] = await Promise.all([
      apiCall('/api/analysis'),
      apiCall('/api/stats')
    ]);

    const records = (analysesRes && analysesRes.analyses) || [];
    const stats = (statsRes && statsRes.stats) || {};

    // Update Quick Stats
    const statNums = document.querySelectorAll('.dashboard-stats .dash-stat-num');
    if (statNums.length >= 4) {
      statNums[0].textContent = records.length;
      statNums[1].textContent = records.filter(r => (r.feasibility_score || 0) >= 65).length;
      statNums[2].textContent = '9';
      statNums[3].textContent = formatINR(records[0]?.total_investment || 300000);
    }

    // Render Saved Analyses Cards
    const container = document.querySelector('.container > div[style*="flex-direction:column"]');
    if (container && records.length > 0) {
      container.innerHTML = records.map(r => {
        const score = r.feasibility_score || 72;
        const viability = r.viability_status || (score >= 65 ? 'Viable ✓' : 'Review Needed △');
        const isViable = score >= 65;

        return `
          <div class="saved-card" id="analysis-card-${r.id}">
            <div class="saved-card-header">
              <div>
                <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:6px;">
                  <h3 style="font-size:1.05rem;font-weight:700;color:var(--navy);">💼 ${r.business_name}</h3>
                  <span class="tag ${isViable ? 'tag-green' : 'tag-yellow'}" style="margin-bottom:0;">${viability}</span>
                  <span style="font-size:0.75rem;color:var(--gray-400);">${r.certificate_no || 'CERTIFIED'}</span>
                </div>
                <p style="font-size:0.85rem;color:var(--gray-600);">${r.business_type} · ${r.district || ''}, ${r.state || ''} · Capital: ${formatINR(r.total_investment)}</p>
              </div>
              <div style="background:var(--navy);color:white;border-radius:var(--radius-md);padding:12px 16px;text-align:center;flex-shrink:0;">
                <div style="font-size:1.3rem;font-weight:800;color:var(--orange);">${score}</div>
                <div style="font-size:0.72rem;color:rgba(255,255,255,0.7);">Score</div>
              </div>
            </div>
            <div class="saved-card-body">
              <div style="display:flex;gap:10px;flex-wrap:wrap;margin-bottom:14px;">
                <span class="stat-pill green">📈 Verified Protocol</span>
                <span class="stat-pill orange">🏛️ Schemes Matched</span>
                <span class="stat-pill green">💰 Investment: ${formatINR(r.total_investment)}</span>
                <span class="stat-pill">📍 Area: ${r.area_type || 'rural'}</span>
              </div>
              <p style="font-size:0.85rem;color:var(--gray-600);line-height:1.65;">Certified business intelligence record securely stored in SQLite database with cryptographic verification hash.</p>
            </div>
            <div class="saved-card-footer">
              <a href="results-overview.html?id=${r.id}" class="btn btn-primary btn-sm">View Full Report →</a>
              <a href="results-competition.html?id=${r.id}" class="btn btn-outline btn-sm">Competition Map</a>
              <a href="results-schemes.html?id=${r.id}" class="btn btn-outline btn-sm">Govt. Schemes</a>
              <a href="advisor.html?id=${r.id}" class="btn btn-outline btn-sm">🤖 AI Advisor</a>
              <button class="btn btn-outline btn-sm btn-delete-analysis" data-id="${r.id}" style="color:var(--red);border-color:rgba(220,53,69,0.3);margin-left:auto;cursor:pointer;">🗑️ Delete</button>
            </div>
          </div>
        `;
      }).join('');

      // Attach Delete Handlers
      container.querySelectorAll('.btn-delete-analysis').forEach(btn => {
        btn.addEventListener('click', async (e) => {
          const id = e.target.getAttribute('data-id');
          if (confirm(`Are you sure you want to delete analysis #${id}?`)) {
            try {
              await apiCall(`/api/analysis/${id}`, { method: 'DELETE' });
              const card = document.getElementById(`analysis-card-${id}`);
              if (card) card.remove();
              alert(`Analysis #${id} deleted successfully.`);
            } catch (err) {
              alert('Could not delete analysis: ' + err.message);
            }
          }
        });
      });
    }
  } catch (err) {
    console.warn('[Dashboard] Could not load database records:', err);
  }
}

// ── 11. Setup AI Advisor Page ─────────────────────────
async function setupAdvisorPage() {
  const analysis = await loadCurrentAnalysis();
  const meta = analysis ? (analysis.meta || analysis) : {};
  const bizName = analysis?.business_name || meta.business_name || 'My Business';
  const bizLabel = meta.business_label || analysis?.business_type || 'Enterprise';
  const bizType = analysis?.business_type || meta.business_type || 'mobile_shop';
  const dist = analysis?.district || meta.district || 'Cuttack';
  const state = analysis?.state || meta.state || 'Odisha';
  const village = meta.village || meta.block || meta.town || '';
  const invest = Number(analysis?.total_investment || meta.total_investment || 300000);
  const stage = meta.stage || analysis?.stage || 'new';
  const areaType = meta.area_type || 'rural';
  const analysisId = analysis?.id || null;

  // Build precise location display
  const locationDisplay = village ? `${village}, ${dist}, ${state}` : `${dist}, ${state}`;

  // 1. Hydrate Active Context Sidebar
  const elBiz = document.getElementById('advisor-biz');
  if (elBiz) elBiz.textContent = bizLabel;

  const elLoc = document.getElementById('advisor-loc');
  if (elLoc) elLoc.textContent = locationDisplay;

  const elInv = document.getElementById('advisor-inv');
  if (elInv) elInv.textContent = formatINR(invest);

  const elStage = document.getElementById('advisor-stage');
  if (elStage) elStage.textContent = stage === 'new' ? 'New Business' : (stage === 'existing' ? 'Existing Business' : stage);

  const elArea = document.getElementById('advisor-area');
  if (elArea) elArea.textContent = { rural: 'Rural', semi_urban: 'Semi-Urban', urban_outskirts: 'Urban Outskirts', urban: 'Urban' }[areaType] || areaType;

  // 2. Hydrate Chat Header Status
  const headerStatus = document.getElementById('advisor-header-status');
  if (headerStatus) {
    headerStatus.innerHTML = `<span class="online-dot"></span>Active · Analyzing ${bizLabel} · ${locationDisplay}`;
  }

  // 3. Setup Chat Interface
  const chatMessages = document.querySelector('.chat-messages');
  const chatForm = document.querySelector('.chat-input-form');
  const chatTextarea = document.querySelector('.chat-input-field');

  if (!chatForm || !chatTextarea || !chatMessages) return;

  const appendMessage = (sender, text) => {
    const isUser = sender === 'user';
    const row = document.createElement('div');
    row.className = `msg-row ${isUser ? 'user-row' : ''}`;
    row.innerHTML = `
      <div class="msg-avatar ${isUser ? 'user-av' : ''}">${isUser ? '👤' : '🤖'}</div>
      <div>
        <div class="msg-bubble ${isUser ? 'user-bubble' : ''}" style="white-space:pre-line;">${text}</div>
        <span class="msg-time" style="${isUser ? 'text-align:right;display:block;' : ''}">${isUser ? 'You' : 'AI Advisor'} · Just now</span>
      </div>
    `;
    chatMessages.appendChild(row);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  };

  // 4. Initialize Clean Chat with Personalized Welcome Message
  chatMessages.innerHTML = '';
  const investLakhs = (invest / 100000).toFixed(1);
  const areaLabel = { rural: 'rural', semi_urban: 'semi-urban', urban_outskirts: 'urban outskirts', urban: 'urban' }[areaType] || 'local';
  const stageLabel = stage === 'new' ? 'New Business (Greenfield)' : 'Existing Business';
  appendMessage('ai', `👋 Namaste! I am your <strong>Vyapaar Vikash AI Advisor</strong>.\n\nI have loaded your certified enterprise profile:\n• Business: <strong>${bizName} (${bizLabel})</strong>\n• Location: <strong>${locationDisplay}</strong> (${areaLabel} area)\n• Capital: <strong>₹${investLakhs} Lakh</strong>\n• Stage: <strong>${stageLabel}</strong>\n\nAll my answers will be specifically tailored to your exact business situation in ${locationDisplay}. Ask me about wholesale suppliers, profit margins, local competitors, government subsidies (PMEGP / MUDRA), or mandatory registrations — I will give you precise, actionable guidance!`);

  // 5. Setup Quick Questions based on Business Type
  const quickQContainer = document.getElementById('advisor-quick-q-list');
  if (quickQContainer) {
    quickQContainer.innerHTML = `
      <a href="?q=Is+opening+a+${encodeURIComponent(bizLabel)}+profitable+here" class="quick-q-item">📈 Is this profitable in ${dist}?</a>
      <a href="?q=How+much+capital+and+monthly+expenses+will+I+need" class="quick-q-item">💰 Capital & expense breakdown?</a>
      <a href="?q=Who+are+my+competitors+in+${encodeURIComponent(dist)}" class="quick-q-item">🏪 Who are my local competitors?</a>
      <a href="?q=Which+government+scheme+can+help+me" class="quick-q-item">🏛️ Which govt. scheme fits?</a>
      <a href="?q=How+to+find+reliable+suppliers+and+distributors" class="quick-q-item">📦 How to find wholesale suppliers?</a>
      <a href="?q=What+are+the+major+risks+in+this+sector" class="quick-q-item">⚠️ What are the main risks?</a>
      <a href="?q=What+are+the+mandatory+licenses+and+registrations" class="quick-q-item">📜 Required licenses & permits?</a>
      <a href="?q=What+should+I+do+first+to+launch" class="quick-q-item">🚀 What are my first steps?</a>
    `;
  }

  // 6. Form Submission Handler
  chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const message = chatTextarea.value.trim();
    if (!message) return;

    appendMessage('user', message);
    chatTextarea.value = '';

    // Full profile context for real-time personalized response
    const payload = {
      message: message,
      business_type: bizType,
      business_name: bizName,
      district: dist,
      state: state,
      village: village,
      investment: invest,
      stage: stage,
      area_type: areaType,
      analysis_id: analysisId
    };

    // Show typing indicator
    const typingRow = document.createElement('div');
    typingRow.className = 'msg-row typing-indicator-row';
    typingRow.innerHTML = `<div class="msg-avatar">🤖</div><div><div class="msg-bubble" style="opacity:0.7;font-style:italic;">AI Advisor is thinking…</div></div>`;
    chatMessages.appendChild(typingRow);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    try {
      const res = await apiCall('/api/ai/advisor', {
        method: 'POST',
        body: JSON.stringify(payload)
      });
      chatMessages.removeChild(typingRow);
      appendMessage('ai', res.reply || 'I am ready to assist with your business queries.');
    } catch (err) {
      chatMessages.removeChild(typingRow);
      appendMessage('ai', 'Sorry, I could not process your query at this moment. Please check your internet connection or try again.');
    }
  });

  // 7. Wire up Quick Question Clicks
  document.querySelectorAll('.quick-q-item').forEach(item => {
    item.addEventListener('click', (e) => {
      e.preventDefault();
      const text = item.textContent.trim().replace(/^→\s*/, '').replace(/^[^\w\s]+\s*/, '');
      chatTextarea.value = text;
      chatForm.dispatchEvent(new Event('submit'));
    });
  });
}


// ─────────────────────────────────────────────────────
//  GLOBAL MODAL & UI UTILITIES
// ─────────────────────────────────────────────────────

function openModal(id) {
  const el = document.getElementById(id);
  if (el) el.style.display = 'flex';
}

function closeModal(id) {
  const el = document.getElementById(id);
  if (el) el.style.display = 'none';
}

function showToast(message, type = 'success') {
  let toast = document.getElementById('vv-toast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'vv-toast';
    toast.style.cssText = `
      position: fixed; bottom: 28px; right: 28px; z-index: 10000;
      padding: 14px 22px; border-radius: 8px; font-weight: 700;
      font-size: 0.9rem; color: #fff; box-shadow: 0 8px 24px rgba(0,0,0,0.25);
      transition: all 0.3s ease; display: none;
    `;
    document.body.appendChild(toast);
  }
  toast.style.background = type === 'error' ? '#dc3545' : '#10b981';
  toast.textContent = message;
  toast.style.display = 'block';
  setTimeout(() => { toast.style.display = 'none'; }, 3500);
}

// Mode Switcher between Location Discovery and Custom Single Business Form
window.switchAnalysisMode = function(mode) {
  const btnLoc = document.getElementById('btn-mode-location');
  const btnSingle = document.getElementById('btn-mode-single');
  const viewLoc = document.getElementById('view-mode-location');
  const viewSingle = document.getElementById('view-mode-single');

  if (!btnLoc || !btnSingle || !viewLoc || !viewSingle) return;

  if (mode === 'location') {
    btnLoc.classList.add('active');
    btnSingle.classList.remove('active');
    viewLoc.style.display = 'block';
    viewSingle.style.display = 'none';
    if (window.oppMap) {
      setTimeout(() => { window.oppMap.invalidateSize(); }, 200);
    }
  } else {
    btnSingle.classList.add('active');
    btnLoc.classList.remove('active');
    viewSingle.style.display = 'block';
    viewLoc.style.display = 'none';
  }
};


// ─────────────────────────────────────────────────────
//  LOCATION OPPORTUNITY EXPLORER (Priority 1–5 Engine)
// ─────────────────────────────────────────────────────

function initOpportunityExplorer() {
  const searchInput = document.getElementById('loc-search-input');
  const suggestionsBox = document.getElementById('loc-suggestions-box');
  const areaTypeSelect = document.getElementById('loc-area-type');
  const budgetInput = document.getElementById('loc-budget-input');
  const radiusPills = document.querySelectorAll('#radius-selector .radius-pill');
  const discoverBtn = document.getElementById('btn-discover');
  const progressBox = document.getElementById('research-progress');
  const resultsBox = document.getElementById('opportunity-results');

  if (!searchInput || !discoverBtn) return;

  let currentRadiusKm = 3.0;
  let activeGeocoded = null;
  let activeOpportunities = [];
  let currentTopOpp = null;

  // Handle URL query parameters (e.g. ?q=Patia,%20Bhubaneswar&r=3)
  const urlParams = new URLSearchParams(window.location.search);
  const qParam = urlParams.get('q') || urlParams.get('loc');
  const rParam = urlParams.get('r') || urlParams.get('radius');
  if (qParam && searchInput) {
    searchInput.value = qParam;
  }
  if (rParam) {
    const parsedR = parseFloat(rParam);
    if (!isNaN(parsedR)) {
      currentRadiusKm = parsedR;
      radiusPills.forEach(p => {
        if (parseFloat(p.dataset.radius) === parsedR) {
          p.classList.add('active');
        } else {
          p.classList.remove('active');
        }
      });
    }
  }

  // 1. Radius Pill Selector
  radiusPills.forEach(pill => {
    pill.addEventListener('click', () => {
      radiusPills.forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
      currentRadiusKm = parseFloat(pill.dataset.radius || '3.0');
      // If map is already loaded, update circle
      if (window.oppRadiusCircle && window.oppCenterMarker) {
        window.oppRadiusCircle.setRadius(currentRadiusKm * 1000);
        const radiusLbl = document.getElementById('res-radius-label');
        if (radiusLbl) radiusLbl.textContent = `${currentRadiusKm} km`;
      }
    });
  });

  // 2. Autocomplete Geocoding with Debounce
  let geocodeTimeout = null;
  searchInput.addEventListener('input', () => {
    clearTimeout(geocodeTimeout);
    const q = searchInput.value.trim();
    if (q.length < 3) {
      if (suggestionsBox) suggestionsBox.style.display = 'none';
      return;
    }
    geocodeTimeout = setTimeout(async () => {
      try {
        const res = await apiCall(`/api/location/geocode?q=${encodeURIComponent(q)}`);
        if (res && res.candidates && res.candidates.length > 0) {
          suggestionsBox.innerHTML = res.candidates.map(c => `
            <div class="loc-sug-item" data-lat="${c.latitude}" data-lng="${c.longitude}" data-display="${c.display_name}" data-state="${c.state || ''}" data-dist="${c.district || ''}">
              📍 <strong>${c.short_name}</strong> – <span style="color:var(--gray-600);font-size:0.8rem;">${c.display_name}</span>
            </div>
          `).join('');
          suggestionsBox.style.display = 'block';

          // Wire click on suggestion items
          suggestionsBox.querySelectorAll('.loc-sug-item').forEach(item => {
            item.addEventListener('click', () => {
              searchInput.value = item.dataset.display;
              activeGeocoded = {
                latitude: parseFloat(item.dataset.lat),
                longitude: parseFloat(item.dataset.lng),
                display_name: item.dataset.display,
                state: item.dataset.state,
                district: item.dataset.dist
              };
              suggestionsBox.style.display = 'none';
              // Trigger automatic research
              runDiscovery();
            });
          });
        } else {
          if (suggestionsBox) suggestionsBox.style.display = 'none';
        }
      } catch (_) {
        if (suggestionsBox) suggestionsBox.style.display = 'none';
      }
    }, 350);
  });

  // Hide suggestions when clicking outside
  document.addEventListener('click', (e) => {
    if (suggestionsBox && !searchInput.contains(e.target) && !suggestionsBox.contains(e.target)) {
      suggestionsBox.style.display = 'none';
    }
  });

  // 3. Main Discovery Trigger
  const runDiscovery = async () => {
    const query = searchInput.value.trim();
    if (!query) {
      alert('Please enter a location, village, town, or PIN code to research.');
      return;
    }

    discoverBtn.disabled = true;
    discoverBtn.innerHTML = '⏳ Researching Market Signals...';
    if (progressBox) progressBox.style.display = 'block';
    if (resultsBox) resultsBox.style.display = 'none';

    // Stepper stages animation
    const steps = [
      { title: '🛰️ Geocoding Spatial Nodes...', desc: 'Verifying administrative boundary and OpenStreetMap coordinates...' },
      { title: '📊 Gathering Micro-Demographics...', desc: 'Estimating catchment population, footfall velocity, and commercial rent...' },
      { title: '🏪 Scanning Nearby Competitor Clusters...', desc: 'Mapping local rival outlets and calculating sector saturation threshold...' },
      { title: '⚖️ Running 6-Factor Weighted Scoring...', desc: 'Evaluating Demand, Competition, Growth, Spending, Supply Gap & Location...' },
      { title: '🏆 Synthesizing Priority 1–5 Ranking...', desc: 'Drafting explainable factor waterfalls and actionable business blueprints...' }
    ];

    let stepIdx = 0;
    const stepInterval = setInterval(() => {
      stepIdx++;
      if (stepIdx < steps.length) {
        const titleEl = document.getElementById('stepper-title');
        const descEl = document.getElementById('stepper-desc');
        if (titleEl) titleEl.textContent = steps[stepIdx].title;
        if (descEl) descEl.textContent = steps[stepIdx].desc;
      }
    }, 450);

    const payload = {
      location_query: query,
      radius_km: currentRadiusKm,
      area_type: areaTypeSelect ? areaTypeSelect.value : 'semi_urban',
      investment_budget: parseFloat(budgetInput ? budgetInput.value : '0') || 0,
      latitude: activeGeocoded ? activeGeocoded.latitude : null,
      longitude: activeGeocoded ? activeGeocoded.longitude : null,
      state: activeGeocoded ? activeGeocoded.state : '',
      district: activeGeocoded ? activeGeocoded.district : ''
    };

    try {
      const res = await apiCall('/api/opportunities/discover', {
        method: 'POST',
        body: JSON.stringify(payload)
      });

      clearInterval(stepInterval);
      if (progressBox) progressBox.style.display = 'none';
      discoverBtn.disabled = false;
      discoverBtn.innerHTML = '🔍 Research &amp; Rank Opportunities →';

      if (res && res.top_opportunities && res.top_opportunities.length > 0) {
        activeOpportunities = res.top_opportunities;
        currentTopOpp = res.top_opportunities[0];
        renderDiscoveryResults(res);
        if (resultsBox) {
          resultsBox.style.display = 'block';
          resultsBox.scrollIntoView({ behavior: 'smooth' });
        }
      } else {
        alert('Could not discover opportunities for this location. Please try refining the location query.');
      }
    } catch (err) {
      clearInterval(stepInterval);
      if (progressBox) progressBox.style.display = 'none';
      discoverBtn.disabled = false;
      discoverBtn.innerHTML = '🔍 Research &amp; Rank Opportunities →';
      alert('Error during location analysis: ' + (err.message || 'Server error'));
    }
  };

  discoverBtn.addEventListener('click', runDiscovery);

  // 4. Render Discovery Results
  function renderDiscoveryResults(data) {
    const loc = data.location;
    const opps = data.top_opportunities;
    const competitors = data.competitors || [];
    const matrix = data.market_gap_matrix || {};

    // Header & Meta Bar
    const heading = document.getElementById('res-location-heading');
    if (heading) heading.textContent = `📍 ${loc.name} · Catchment Intelligence`;
    const coordsEl = document.getElementById('res-coords');
    if (coordsEl) coordsEl.textContent = `${loc.latitude.toFixed(4)}°N, ${loc.longitude.toFixed(4)}°E`;
    const radiusLbl = document.getElementById('res-radius-label');
    if (radiusLbl) radiusLbl.textContent = `${loc.radius_km} km`;

    const confBadge = document.getElementById('res-confidence-badge');
    if (confBadge) confBadge.textContent = `${opps[0].confidence_score}% Confidence Score`;

    document.getElementById('meta-pop').textContent = loc.catchment_population.toLocaleString('en-IN');
    document.getElementById('meta-footfall').textContent = `${loc.footfall_index} / 10`;
    document.getElementById('meta-rent').textContent = `₹${loc.avg_sqft_rent} / sq.ft`;
    document.getElementById('meta-wage').textContent = `₹${data.location.daily_wage_rate || 420} / day`;
    document.getElementById('meta-competitors').textContent = `${competitors.length} Outlets Mapped`;

    // Initialize or Update Leaflet Map
    renderLeafletMap(loc.latitude, loc.longitude, loc.radius_km, competitors, loc.name);

    // Render 5 Opportunity Cards
    const container = document.getElementById('opp-cards-container');
    if (container) {
      container.innerHTML = opps.map((opp, idx) => {
        const priorityClass = `priority-${opp.priority}`;
        const pLabel = opp.priority === 1 ? 'Priority 1: Prime Recommendation' : `Priority ${opp.priority}`;
        const driversHtml = (opp.demand_drivers || []).slice(0, 2).map(d => `<li>• ${d}</li>`).join('');

        return `
          <div class="opportunity-card">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:14px;margin-bottom:14px;">
              <div style="display:flex;gap:14px;align-items:center;">
                <div style="font-size:2.8rem;background:var(--gray-100);width:64px;height:64px;border-radius:12px;display:flex;align-items:center;justify-content:center;">
                  ${opp.icon}
                </div>
                <div>
                  <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:4px;">
                    <span class="priority-badge ${priorityClass}">${pLabel}</span>
                    <span style="font-size:0.75rem;color:var(--gray-600);font-weight:600;">Sector: ${opp.sector}</span>
                    <span class="confidence-tag" title="Grounded on Census data and spatial proximity">${opp.confidence_score}% Confidence</span>
                  </div>
                  <h3 style="font-size:1.3rem;font-weight:800;color:var(--navy);">${opp.category_name}</h3>
                </div>
              </div>

              <!-- Score Badge -->
              <div style="display:flex;align-items:center;gap:14px;">
                <div class="score-circle">
                  <span class="score-num">${opp.opportunity_score}</span>
                  <span class="score-max">/ 100</span>
                </div>
              </div>
            </div>

            <!-- Lead delta reason -->
            <div style="background:var(--gray-100);padding:10px 16px;border-radius:var(--radius-sm);font-size:0.85rem;color:var(--navy);font-weight:600;margin-bottom:14px;border-left:3px solid var(--orange);">
              💡 <strong>Why Selected:</strong> ${opp.ranked_above_next_reason || opp.why_selected_reasons[0]}
            </div>

            <!-- Key Financials & Signals Grid -->
            <div style="display:grid;grid-template-columns:repeat(4, 1fr);gap:10px;margin-bottom:14px;font-size:0.82rem;">
              <div style="background:var(--off-white);padding:8px 12px;border-radius:6px;border:var(--border);">
                <span style="color:var(--gray-600);display:block;">Gross Margin</span>
                <strong style="color:var(--green);font-size:0.95rem;">~${opp.avg_margin_pct}%</strong>
              </div>
              <div style="background:var(--off-white);padding:8px 12px;border-radius:6px;border:var(--border);">
                <span style="color:var(--gray-600);display:block;">Break-Even</span>
                <strong style="color:var(--navy);font-size:0.95rem;">~${opp.break_even_months} Months</strong>
              </div>
              <div style="background:var(--off-white);padding:8px 12px;border-radius:6px;border:var(--border);">
                <span style="color:var(--gray-600);display:block;">Capital Range</span>
                <strong style="color:var(--navy);font-size:0.95rem;">₹${(opp.min_investment/100000).toFixed(1)}L–${(opp.max_investment/100000).toFixed(1)}L</strong>
              </div>
              <div style="background:var(--off-white);padding:8px 12px;border-radius:6px;border:var(--border);">
                <span style="color:var(--gray-600);display:block;">Sector Growth</span>
                <strong style="color:var(--orange);font-size:0.95rem;">${opp.national_cagr_pct}% CAGR</strong>
              </div>
            </div>

            <!-- Demand Drivers Preview -->
            <ul style="font-size:0.82rem;color:var(--gray-600);line-height:1.6;margin-bottom:16px;">
              ${driversHtml}
            </ul>

            <!-- Action Buttons -->
            <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;border-top:var(--border);padding-top:14px;">
              <button type="button" class="btn btn-outline btn-sm btn-why-rank" data-idx="${idx}">
                📊 Why This Ranking? (Factor Waterfall)
              </button>
              <div style="display:flex;gap:8px;">
                <button type="button" class="btn btn-outline btn-sm btn-save-opp" data-idx="${idx}">
                  🔖 Save Opportunity
                </button>
                <button type="button" class="btn btn-primary btn-sm btn-gen-plan" data-idx="${idx}">
                  📋 Generate 14-Section Business Plan →
                </button>
              </div>
            </div>
          </div>
        `;
      }).join('');

      // Wire Opportunity Card Action Buttons
      container.querySelectorAll('.btn-why-rank').forEach(btn => {
        btn.addEventListener('click', () => {
          const idx = parseInt(btn.dataset.idx);
          showWhyRankingModal(opps[idx]);
        });
      });

      container.querySelectorAll('.btn-gen-plan').forEach(btn => {
        btn.addEventListener('click', () => {
          const idx = parseInt(btn.dataset.idx);
          triggerPlanGeneration(opps[idx], loc.name);
        });
      });

      container.querySelectorAll('.btn-save-opp').forEach(btn => {
        btn.addEventListener('click', async () => {
          const idx = parseInt(btn.dataset.idx);
          await saveOpportunityBookmark(opps[idx], loc.name);
        });
      });
    }

    // Priority 1 opportunity reference (used for comparative table & scenario sliders)
    const p1 = opps[0] || null;

    // Render Priority 1 "Why Not The Other Options?" Comparative Table
    const compContainer = document.getElementById('comparative-table-container');
    if (compContainer && p1 && p1.comparative_analysis) {
      compContainer.innerHTML = `
        <div style="overflow-x:auto;">
          <table style="width:100%;border-collapse:collapse;font-size:0.85rem;">
            <thead>
              <tr style="background:var(--gray-100);border-bottom:2px solid var(--gray-200);text-align:left;">
                <th style="padding:10px 14px;">Alternative Candidate</th>
                <th style="padding:10px 14px;">Score Differential</th>
                <th style="padding:10px 14px;">Priority 1 Lead Advantage (${p1.category_name})</th>
                <th style="padding:10px 14px;">Tradeoff Analysis</th>
              </tr>
            </thead>
            <tbody>
              ${p1.comparative_analysis.map(row => `
                <tr style="border-bottom:1px solid var(--gray-200);">
                  <td style="padding:10px 14px;font-weight:700;color:var(--navy);">
                    ${row.compared_icon} Priority ${row.compared_to_priority}: ${row.compared_category_name}
                  </td>
                  <td style="padding:10px 14px;color:var(--orange);font-weight:800;">
                    +${row.score_differential} pts
                  </td>
                  <td style="padding:10px 14px;color:var(--green);font-weight:600;">
                    ✓ ${row.p1_advantage}
                  </td>
                  <td style="padding:10px 14px;color:var(--gray-600);">
                    ${row.tradeoff_note}
                  </td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      `;
    }

    // Market Gap Quadrants
    document.getElementById('quadrant-q1-list').innerHTML = (matrix.high_demand_low_comp || []).map(c => `• ${c}`).join('<br>') || 'None currently';
    document.getElementById('quadrant-q2-list').innerHTML = (matrix.high_demand_high_comp || []).map(c => `• ${c}`).join('<br>') || 'None currently';
    document.getElementById('quadrant-q3-list').innerHTML = (matrix.low_demand_low_comp || []).map(c => `• ${c}`).join('<br>') || 'None currently';
    document.getElementById('quadrant-q4-list').innerHTML = (matrix.low_demand_high_comp || []).map(c => `• ${c}`).join('<br>') || 'None currently';

    // Hook up Scenario Stress Test for Priority 1
    if (p1) initScenarioSliders(p1, loc);
  }

  // 5. Leaflet Map Renderer
  function renderLeafletMap(lat, lng, radiusKm, competitors, locName) {
    if (!window.L) {
      console.warn('Leaflet not loaded');
      return;
    }

    if (!window.oppMap) {
      window.oppMap = L.map('opp-leaflet-map').setView([lat, lng], 13);
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
      }).addTo(window.oppMap);
    } else {
      window.oppMap.setView([lat, lng], 13);
    }

    // Center Marker & Radius Circle
    if (window.oppCenterMarker) window.oppMap.removeLayer(window.oppCenterMarker);
    if (window.oppRadiusCircle) window.oppMap.removeLayer(window.oppRadiusCircle);

    window.oppCenterMarker = L.marker([lat, lng]).addTo(window.oppMap)
      .bindPopup(`📍 <strong>${locName}</strong><br>Center of ${radiusKm} km analysis catchment.`)
      .openPopup();

    window.oppRadiusCircle = L.circle([lat, lng], {
      color: '#f05b22',
      fillColor: '#f05b22',
      fillOpacity: 0.12,
      radius: radiusKm * 1000
    }).addTo(window.oppMap);

    // Clear and re-render competitor markers
    if (window.oppCompMarkers) {
      window.oppCompMarkers.forEach(m => window.oppMap.removeLayer(m));
    }
    window.oppCompMarkers = [];

    competitors.forEach(c => {
      const compMarker = L.circleMarker([c.latitude, c.longitude], {
        radius: 7,
        color: c.threat_level === 'High' ? '#dc3545' : '#2563eb',
        fillColor: c.threat_level === 'High' ? '#dc3545' : '#2563eb',
        fillOpacity: 0.75
      }).addTo(window.oppMap);

      compMarker.bindPopup(`
        <strong>${c.icon} ${c.name}</strong><br>
        <span style="font-size:0.75rem;color:gray;">Category: ${c.category_name}</span><br>
        Distance: <strong>${c.distance_km} km</strong> · Threat: <strong style="color:${c.threat_level==='High'?'#dc3545':'#2563eb'}">${c.threat_level}</strong>
      `);
      window.oppCompMarkers.push(compMarker);
    });

    setTimeout(() => { window.oppMap.invalidateSize(); }, 300);
  }

  // 6. Why This Ranking Modal Trigger
  function showWhyRankingModal(opp) {
    document.getElementById('why-modal-icon').textContent = opp.icon;
    document.getElementById('why-modal-title').textContent = `${opp.category_name}`;
    document.getElementById('why-modal-priority').textContent = `Priority ${opp.priority}`;
    document.getElementById('why-modal-total-score').textContent = opp.opportunity_score;
    document.getElementById('why-modal-explanation').textContent = opp.ranking_explanation;
    document.getElementById('why-modal-lead-reason').textContent = opp.ranked_above_next_reason || '';

    const container = document.getElementById('waterfall-bars-container');
    if (container) {
      const factors = opp.factor_scores;
      const fKeys = ['demand', 'competition', 'growth', 'spending', 'supply_gap', 'location'];

      container.innerHTML = fKeys.map(k => {
        const f = factors[k];
        return `
          <div class="waterfall-bar-row">
            <div class="waterfall-label">
              ${f.label} (${f.weight_pct}%)
              <span style="font-size:0.72rem;display:block;color:var(--gray-600);font-weight:400;">${f.interpretation}</span>
            </div>
            <div class="waterfall-track">
              <div class="waterfall-fill" style="width:${Math.min(100, f.score)}%;"></div>
            </div>
            <div class="waterfall-val">
              ${f.score}/100
              <span style="font-size:0.72rem;display:block;color:var(--orange);">+${f.contribution} pts</span>
            </div>
          </div>
        `;
      }).join('');
    }

    openModal('modal-why-ranking');
  }

  // 7. 14-Section Business Plan Generator Trigger
  async function triggerPlanGeneration(opp, locationName) {
    const titleEl = document.getElementById('plan-modal-title');
    if (titleEl) titleEl.textContent = `Generating Blueprint for ${opp.category_name}...`;
    openModal('modal-business-plan');

    try {
      const res = await apiCall('/api/plan/generate', {
        method: 'POST',
        body: JSON.stringify({
          category_key: opp.category_key,
          location_name: locationName,
          investment: opp.min_investment,
          area_type: areaTypeSelect ? areaTypeSelect.value : 'semi_urban'
        })
      });

      // API wraps plan under res.business_plan or directly as res
      const plan = (res && res.business_plan) ? res.business_plan : res;
      if (plan && plan.sections && plan.sections.length > 0) {
        renderBusinessPlanModal(plan);
      } else {
        const titleEl2 = document.getElementById('plan-modal-title');
        if (titleEl2) titleEl2.textContent = 'Business Plan Ready (check console for details)';
      }
    } catch (err) {
      alert('Error generating plan: ' + err.message);
      closeModal('modal-business-plan');
    }
  }

  function renderBusinessPlanModal(plan) {
    document.getElementById('plan-modal-title').textContent = plan.title;
    document.getElementById('plan-modal-sub').textContent = `Grounded in ${plan.location_name} Micro-Market Intelligence`;

    const fin = plan.financial_summary || {};
    document.getElementById('plan-fin-sales').textContent = formatINR(fin.monthly_sales);
    document.getElementById('plan-fin-profit').textContent = formatINR(fin.monthly_profit);
    document.getElementById('plan-fin-margin').textContent = `${fin.margin_pct}%`;
    document.getElementById('plan-fin-be').textContent = `${fin.break_even_months} Months`;

    // 14 Sections
    const secContainer = document.getElementById('plan-sections-container');
    if (secContainer) {
      secContainer.innerHTML = plan.sections.map(s => `
        <div style="background:var(--off-white);padding:14px 18px;border-radius:var(--radius-sm);border:var(--border);">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
            <h4 style="font-size:0.95rem;font-weight:700;color:var(--navy);">${s.section_number}. ${s.title}</h4>
            <span style="font-size:0.72rem;font-weight:700;padding:2px 8px;border-radius:4px;background:rgba(240,91,34,0.12);color:var(--orange);">${s.tag}</span>
          </div>
          <p style="font-size:0.85rem;color:var(--gray-800);line-height:1.6;white-space:pre-line;">${s.content}</p>
        </div>
      `).join('');
    }

    // 10-step roadmap
    const roadContainer = document.getElementById('plan-roadmap-container');
    if (roadContainer) {
      roadContainer.innerHTML = (plan.roadmap || []).map(r => `
        <div style="display:flex;gap:12px;align-items:flex-start;background:var(--white);padding:10px 14px;border-radius:6px;border:var(--border);">
          <div style="width:28px;height:28px;border-radius:50%;background:var(--navy);color:#fff;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:0.8rem;flex-shrink:0;">${r.step}</div>
          <div>
            <div style="font-size:0.85rem;font-weight:700;color:var(--navy);">${r.title} <span style="font-size:0.75rem;color:var(--orange);font-weight:600;">(${r.phase})</span></div>
            <p style="font-size:0.8rem;color:var(--gray-600);margin-top:2px;">${r.action}</p>
          </div>
        </div>
      `).join('');
    }

    // Wire Save to Dashboard button
    const saveBtn = document.getElementById('btn-save-plan-to-db');
    if (saveBtn) {
      saveBtn.onclick = async () => {
        saveBtn.disabled = true;
        saveBtn.textContent = 'Saving...';
        try {
          await apiCall('/api/plan/generate', {
            method: 'POST',
            body: JSON.stringify({
              category_key: plan.category_key,
              location_name: plan.location_name,
              investment: plan.investment,
              save: true
            })
          });
          showToast('Blueprint saved to your Workspace Dashboard!');
          saveBtn.textContent = '✓ Saved';
        } catch (e) {
          showToast('Please sign in to save plans to your dashboard.', 'error');
          saveBtn.disabled = false;
          saveBtn.textContent = '💾 Save to Dashboard';
        }
      };
    }

    // Wire Copy Plan button
    const copyBtn = document.getElementById('btn-copy-plan');
    if (copyBtn) {
      copyBtn.onclick = () => {
        let text = `${plan.title}\nLocation: ${plan.location_name}\n\n`;
        text += `FINANCIAL METRICS:\n`;
        text += `- Monthly Sales: ${formatINR(fin.monthly_sales)}\n`;
        text += `- Monthly Net Profit: ${formatINR(fin.monthly_profit)}\n`;
        text += `- Gross Margin: ${fin.margin_pct}%\n`;
        text += `- Break-Even: ${fin.break_even_months} Months\n\n`;
        text += `14-SECTION BUSINESS PLAN:\n\n`;
        (plan.sections || []).forEach(s => {
          text += `### ${s.section_number}. ${s.title} [${s.tag}]\n${s.content}\n\n`;
        });
        text += `10-STEP EXECUTION ROADMAP:\n\n`;
        (plan.roadmap || []).forEach(r => {
          text += `Step ${r.step} (${r.phase}): ${r.title}\n${r.action}\n\n`;
        });
        navigator.clipboard.writeText(text).then(() => {
          showToast('Full 14-section blueprint copied to clipboard!');
        }).catch(() => {
          showToast('Blueprint ready (please copy manually).');
        });
      };
    }
  }

  // 8. Save Opportunity Bookmark
  async function saveOpportunityBookmark(opp, locationName) {
    try {
      await apiCall('/api/user/saved_opportunities', {
        method: 'POST',
        body: JSON.stringify({
          category_key: opp.category_key,
          category_name: opp.category_name,
          priority: opp.priority,
          opportunity_score: opp.opportunity_score,
          confidence_score: opp.confidence_score,
          location_name: locationName,
          reasons: opp.why_selected_reasons,
          factors: opp.factor_scores
        })
      });
      showToast(`Saved Priority ${opp.priority} (${opp.category_name}) to your Dashboard!`);
    } catch (err) {
      showToast('Please sign in to save opportunities to your dashboard.', 'error');
    }
  }

  // 9. Bookmark Location Button
  const saveLocBtn = document.getElementById('btn-save-loc-bookmark');
  if (saveLocBtn) {
    saveLocBtn.addEventListener('click', async () => {
      const q = searchInput.value.trim();
      try {
        await apiCall('/api/user/saved_locations', {
          method: 'POST',
          body: JSON.stringify({
            name: q,
            formatted_address: q,
            latitude: activeGeocoded ? activeGeocoded.latitude : 20.2961,
            longitude: activeGeocoded ? activeGeocoded.longitude : 85.8245,
            radius_km: currentRadiusKm
          })
        });
        showToast(`Bookmarked '${q}' to your workspace!`);
      } catch (_) {
        showToast('Please sign in to bookmark locations.', 'error');
      }
    });
  }

  // 10. Scenario Sliders Setup
  function initScenarioSliders(opp, loc) {
    const sRent = document.getElementById('slider-rent');
    const sDem = document.getElementById('slider-demand');
    const sComp = document.getElementById('slider-comp');
    const lblRent = document.getElementById('label-rent-val');
    const lblDem = document.getElementById('label-dem-val');
    const lblComp = document.getElementById('label-comp-val');
    const resetBtn = document.getElementById('btn-reset-scenario');

    if (!sRent || !sDem || !sComp) return;

    let scenTimer = null;
    const triggerScenario = () => {
      const rVal = parseFloat(sRent.value);
      const dVal = parseFloat(sDem.value);
      const cVal = parseInt(sComp.value);

      if (lblRent) lblRent.textContent = `${rVal > 0 ? '+' : ''}${rVal}%`;
      if (lblDem) lblDem.textContent = `${dVal > 0 ? '+' : ''}${dVal}%`;
      if (lblComp) lblComp.textContent = `+${cVal} stores`;

      clearTimeout(scenTimer);
      scenTimer = setTimeout(async () => {
        try {
          const res = await apiCall('/api/scenario/simulate', {
            method: 'POST',
            body: JSON.stringify({
              category_key: opp.category_key,
              state: loc.state,
              district: loc.district,
              area_type: loc.area_type,
              radius_km: loc.radius_km,
              investment: opp.min_investment,
              rent_delta_pct: rVal,
              demand_delta_pct: dVal,
              competitor_influx: cVal
            })
          });

          if (res) {
            const scoreLabel = document.getElementById('scen-score-label');
            const impactLabel = document.getElementById('scen-impact-label');
            const diffSign = res.score_difference >= 0 ? '+' : '';
            if (scoreLabel) scoreLabel.innerHTML = `Simulated Score: <strong>${res.scenario_score}/100</strong> <span style="font-size:0.88rem;color:${res.score_difference<0?'#dc3545':'#059669'};">(${diffSign}${res.score_difference} pts)</span>`;
            if (impactLabel) impactLabel.textContent = res.impact_summary;
          }
        } catch (_) {}
      }, 250);
    };

    sRent.oninput = triggerScenario;
    sDem.oninput = triggerScenario;
    sComp.oninput = triggerScenario;

    if (resetBtn) {
      resetBtn.onclick = () => {
        sRent.value = 0;
        sDem.value = 0;
        sComp.value = 0;
        triggerScenario();
      };
    }
  }

  // Run initial discovery automatically on page load so user sees instant value!
  setTimeout(() => {
    runDiscovery();
  }, 100);
}


// ─────────────────────────────────────────────────────
//  DYNAMIC DASHBOARD HYDRATION
// ─────────────────────────────────────────────────────

window.switchDashTab = function(tab) {
  const tabs = ['analyses', 'opps', 'plans', 'locations'];
  tabs.forEach(t => {
    const btn = document.getElementById(`tab-btn-${t}`);
    const panel = document.getElementById(`dash-panel-${t}`);
    if (btn) btn.classList.toggle('active', t === tab);
    if (panel) panel.style.display = t === tab ? 'block' : 'none';
  });
};

async function hydrateDashboard() {
  const welcomeName = document.getElementById('dash-welcome-name');
  const welcomeSub = document.getElementById('dash-welcome-sub');
  const authAction = document.getElementById('btn-auth-action');

  try {
    const res = await apiCall('/api/user/dashboard_data');
    if (!res) return;

    // 1. User Header
    if (res.authenticated && res.user) {
      if (welcomeName) welcomeName.textContent = `Welcome back, ${res.user.name} 👋`;
      if (welcomeSub) welcomeSub.textContent = `${res.user.email} · Enterprise Role: ${res.user.role.toUpperCase()} · Status: Certified Active`;
      if (authAction) {
        authAction.textContent = 'Logout';
        authAction.href = '#';
        authAction.onclick = async (e) => {
          e.preventDefault();
          await apiCall('/api/logout', { method: 'POST' }).catch(() => {});
          window.location.href = 'login.html';
        };
      }
    } else {
      if (welcomeName) welcomeName.textContent = `Welcome to Your Demo Workspace 👋`;
      if (welcomeSub) welcomeSub.textContent = `Sign in with Google or create an account to auto-sync your analyses and business blueprints across devices.`;
      if (authAction) {
        authAction.textContent = 'Sign In';
        authAction.href = 'login.html';
      }
    }

    // 2. KPIs
    const kpis = res.kpis || {};
    document.getElementById('stat-analyses-count').textContent = kpis.saved_analyses_count || 0;
    document.getElementById('stat-opps-count').textContent = kpis.saved_opportunities_count || 0;
    document.getElementById('stat-plans-count').textContent = kpis.business_plans_count || 0;
    document.getElementById('stat-locations-count').textContent = kpis.saved_locations_count || 0;

    document.getElementById('badge-count-analyses').textContent = kpis.saved_analyses_count || 0;
    document.getElementById('badge-count-opps').textContent = kpis.saved_opportunities_count || 0;
    document.getElementById('badge-count-plans').textContent = kpis.business_plans_count || 0;
    document.getElementById('badge-count-locations').textContent = kpis.saved_locations_count || 0;

    // 3. Tab 1: Saved Analyses List
    const aContainer = document.getElementById('analyses-list-container');
    if (aContainer) {
      if (res.recent_analyses && res.recent_analyses.length > 0) {
        aContainer.innerHTML = res.recent_analyses.map(a => `
          <div class="saved-card">
            <div class="saved-card-header">
              <div>
                <h3 style="font-size:1.1rem;font-weight:700;color:var(--navy);">${a.business_name}</h3>
                <span style="font-size:0.8rem;color:var(--gray-600);">📍 ${a.district}, ${a.state} · ${a.business_type}</span>
              </div>
              <div style="display:flex;gap:8px;align-items:center;">
                <span class="stat-pill ${a.feasibility_score >= 70 ? 'green' : 'orange'}">
                  Feasibility: ${a.feasibility_score}/100
                </span>
                <span class="stat-pill">${a.viability_status}</span>
              </div>
            </div>
            <div class="saved-card-body" style="font-size:0.88rem;color:var(--gray-600);">
              Capital: <strong>${formatINR(a.total_investment)}</strong> · Certificate: <strong style="color:var(--orange);">${a.certificate_no}</strong>
            </div>
            <div class="saved-card-footer">
              <span style="font-size:0.75rem;color:var(--gray-600);">Created: ${new Date(a.created_at).toLocaleDateString()}</span>
              <div style="display:flex;gap:8px;">
                <a href="results-overview.html?id=${a.id}" class="btn btn-primary btn-sm">View Certified Report →</a>
                <button type="button" class="btn btn-outline btn-sm btn-del-analysis" data-id="${a.id}">Delete</button>
              </div>
            </div>
          </div>
        `).join('');

        aContainer.querySelectorAll('.btn-del-analysis').forEach(btn => {
          btn.addEventListener('click', async () => {
            if (confirm('Delete this certified analysis?')) {
              await apiCall(`/api/analysis/${btn.dataset.id}`, { method: 'DELETE' });
              showToast('Analysis deleted.');
              hydrateDashboard();
            }
          });
        });
      } else {
        aContainer.innerHTML = `
          <div class="empty-state-box">
            <div style="font-size:3rem;margin-bottom:10px;">📊</div>
            <h3 style="color:var(--navy);font-weight:700;margin-bottom:6px;">No Analyses Run Yet</h3>
            <p style="color:var(--gray-600);font-size:0.9rem;margin-bottom:18px;">Research a location or evaluate a business concept to generate your first certified report.</p>
            <a href="analyze.html" class="btn btn-primary btn-sm">+ Start Location Research</a>
          </div>
        `;
      }
    }

    // 4. Tab 2: Saved Opportunities
    const oContainer = document.getElementById('opps-list-container');
    if (oContainer) {
      if (res.saved_opportunities && res.saved_opportunities.length > 0) {
        oContainer.innerHTML = res.saved_opportunities.map(o => `
          <div class="saved-card">
            <div class="saved-card-header">
              <div>
                <span class="priority-badge priority-${o.priority}">Priority ${o.priority}</span>
                <h3 style="font-size:1.15rem;font-weight:800;color:var(--navy);margin-top:4px;">${o.category_name}</h3>
                <span style="font-size:0.82rem;color:var(--gray-600);">📍 ${o.location_name}</span>
              </div>
              <div class="stat-pill green">Score: ${o.opportunity_score}/100</div>
            </div>
            <div class="saved-card-body" style="font-size:0.85rem;color:var(--gray-600);">
              ${(o.reasons || []).slice(0, 2).map(r => `<div>• ${r}</div>`).join('')}
            </div>
            <div class="saved-card-footer">
              <span style="font-size:0.75rem;color:var(--gray-600);">Saved on ${new Date(o.created_at).toLocaleDateString()}</span>
              <div style="display:flex;gap:8px;">
                <a href="analyze.html?q=${encodeURIComponent(o.location_name)}" class="btn btn-primary btn-sm">Research Area Again →</a>
                <button type="button" class="btn btn-outline btn-sm btn-del-opp" data-id="${o.id}">Remove</button>
              </div>
            </div>
          </div>
        `).join('');

        oContainer.querySelectorAll('.btn-del-opp').forEach(btn => {
          btn.addEventListener('click', async () => {
            await apiCall(`/api/user/saved_opportunities/${btn.dataset.id}`, { method: 'DELETE' });
            showToast('Opportunity removed from dashboard.');
            hydrateDashboard();
          });
        });
      } else {
        oContainer.innerHTML = `
          <div class="empty-state-box">
            <div style="font-size:3rem;margin-bottom:10px;">🏆</div>
            <h3 style="color:var(--navy);font-weight:700;margin-bottom:6px;">No Saved Opportunities</h3>
            <p style="color:var(--gray-600);font-size:0.9rem;margin-bottom:18px;">Bookmark high-potential Priority 1–5 opportunities directly from your location analysis runs.</p>
            <a href="analyze.html" class="btn btn-primary btn-sm">Explore Opportunities →</a>
          </div>
        `;
      }
    }

    // 5. Tab 3: Business Plans
    const pContainer = document.getElementById('plans-list-container');
    if (pContainer) {
      if (res.business_plans && res.business_plans.length > 0) {
        pContainer.innerHTML = res.business_plans.map(p => `
          <div class="saved-card">
            <div class="saved-card-header">
              <div>
                <h3 style="font-size:1.15rem;font-weight:800;color:var(--navy);">${p.title}</h3>
                <span style="font-size:0.82rem;color:var(--gray-600);">📍 ${p.location_name} · Investment: ${formatINR(p.investment)}</span>
              </div>
              <span class="stat-pill orange">14-Section Blueprint</span>
            </div>
            <div class="saved-card-body" style="font-size:0.85rem;color:var(--gray-600);line-height:1.6;">
              ${p.executive_summary || 'Actionable operational and financial roadmap.'}
            </div>
            <div class="saved-card-footer">
              <span style="font-size:0.75rem;color:var(--gray-600);">Updated: ${new Date(p.updated_at || p.created_at).toLocaleDateString()}</span>
              <div style="display:flex;gap:8px;">
                <button type="button" class="btn btn-primary btn-sm btn-view-plan" data-id="${p.id}">View Blueprint →</button>
                <button type="button" class="btn btn-outline btn-sm btn-del-plan" data-id="${p.id}">Delete</button>
              </div>
            </div>
          </div>
        `).join('');

        pContainer.querySelectorAll('.btn-view-plan').forEach(btn => {
          btn.addEventListener('click', async () => {
            btn.disabled = true;
            btn.textContent = 'Loading...';
            try {
              const res = await apiCall(`/api/user/business_plans/${btn.dataset.id}`);
              const plan = (res && res.plan) ? res.plan : res;
              const fullPlan = (plan.plan_data && plan.plan_data.sections) ? plan.plan_data : plan;
              if (!fullPlan.title) fullPlan.title = plan.title;
              if (!fullPlan.location_name) fullPlan.location_name = plan.location_name;
              if (!fullPlan.roadmap && plan.roadmap) fullPlan.roadmap = plan.roadmap;
              renderBusinessPlanModal(fullPlan);
              openModal('modal-business-plan');
            } catch (err) {
              alert('Could not open blueprint: ' + err.message);
            } finally {
              btn.disabled = false;
              btn.textContent = 'View Blueprint →';
            }
          });
        });

        pContainer.querySelectorAll('.btn-del-plan').forEach(btn => {
          btn.addEventListener('click', async () => {
            if (confirm('Delete this business blueprint?')) {
              await apiCall(`/api/plan/${btn.dataset.id}`, { method: 'DELETE' });
              showToast('Business plan deleted.');
              hydrateDashboard();
            }
          });
        });
      } else {
        pContainer.innerHTML = `
          <div class="empty-state-box">
            <div style="font-size:3rem;margin-bottom:10px;">📋</div>
            <h3 style="color:var(--navy);font-weight:700;margin-bottom:6px;">No Saved Business Plans</h3>
            <p style="color:var(--gray-600);font-size:0.9rem;margin-bottom:18px;">Click "Generate 14-Section Business Plan" on any opportunity card to save a complete blueprint here.</p>
            <a href="analyze.html" class="btn btn-primary btn-sm">Start Planning →</a>
          </div>
        `;
      }
    }

    // 6. Tab 4: Saved Locations
    const lContainer = document.getElementById('locations-list-container');
    if (lContainer) {
      if (res.saved_locations && res.saved_locations.length > 0) {
        lContainer.innerHTML = res.saved_locations.map(l => `
          <div class="saved-card">
            <div class="saved-card-header">
              <div>
                <h3 style="font-size:1.15rem;font-weight:800;color:var(--navy);">📍 ${l.name}</h3>
                <span style="font-size:0.82rem;color:var(--gray-600);">${l.formatted_address || l.name} · Radius: ${l.radius_km || 3.0} km</span>
              </div>
            </div>
            <div class="saved-card-footer">
              <span style="font-size:0.75rem;color:var(--gray-600);">Bookmarked on ${new Date(l.created_at).toLocaleDateString()}</span>
              <div style="display:flex;gap:8px;">
                <a href="analyze.html?q=${encodeURIComponent(l.name)}&r=${l.radius_km || 3.0}" class="btn btn-primary btn-sm">Research This Area →</a>
                <button type="button" class="btn btn-outline btn-sm btn-del-loc" data-id="${l.id}">Remove</button>
              </div>
            </div>
          </div>
        `).join('');

        lContainer.querySelectorAll('.btn-del-loc').forEach(btn => {
          btn.addEventListener('click', async () => {
            await apiCall(`/api/user/saved_locations/${btn.dataset.id}`, { method: 'DELETE' });
            showToast('Location bookmark removed.');
            hydrateDashboard();
          });
        });
      } else {
        lContainer.innerHTML = `
          <div class="empty-state-box">
            <div style="font-size:3rem;margin-bottom:10px;">📍</div>
            <h3 style="color:var(--navy);font-weight:700;margin-bottom:6px;">No Bookmarked Locations</h3>
            <p style="color:var(--gray-600);font-size:0.9rem;margin-bottom:18px;">Bookmark your key market areas in the Location Opportunity Explorer to easily revisit them.</p>
            <a href="analyze.html" class="btn btn-primary btn-sm">Bookmark a Location →</a>
          </div>
        `;
      }
    }

  } catch (err) {
    console.warn('[Dashboard] Error hydrating workspace:', err);
  }
}


