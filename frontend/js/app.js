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

  // 1. Analyse Form Page
  if (path.includes('analyse.html') || path.includes('analyze.html')) {
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
  const districtInput = document.getElementById('district');
  const districtList = document.getElementById('district-list');
  const blockInput = document.getElementById('block');
  const blockList = document.getElementById('block-list');
  const villageInput = document.getElementById('village');
  const villageList = document.getElementById('village-list');
  const areaTypeSelect = document.getElementById('area_type');
  const microHint = document.getElementById('micro-area-hint');

  if (!stateSelect || !districtInput) return;

  // 1. State Change -> Fetch Districts
  stateSelect.addEventListener('change', async () => {
    const state = stateSelect.value;
    if (!state) return;

    if (districtList) districtList.innerHTML = '';
    districtInput.value = '';
    if (blockInput) blockInput.value = '';
    if (villageInput) villageInput.value = '';

    try {
      const res = await apiCall(`/api/geo/districts?state=${encodeURIComponent(state)}`);
      if (res && res.districts && districtList) {
        districtList.innerHTML = res.districts.map(d => `<option value="${d.name}">`).join('');
        districtInput.placeholder = `Select or type district (${res.count} in ${state})`;
      }
    } catch (err) {
      console.warn('[Geo] Failed to load districts:', err);
    }
  });

  // 2. District Change -> Fetch Sub-Areas & Preset Blocks/Villages
  const handleDistrictChange = async () => {
    const state = stateSelect.value;
    const district = districtInput.value.trim();
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

      // Fetch micro-intelligence
      updateMicroIntelligence();
    } catch (err) {
      console.warn('[Geo] Sub-area load note:', err);
    }
  };

  districtInput.addEventListener('change', handleDistrictChange);
  districtInput.addEventListener('input', () => {
    if (districtInput.value.length > 2) handleDistrictChange();
  });

  // 3. Auto-detect Archetype & Update Micro Hint
  const updateMicroIntelligence = async () => {
    const state = stateSelect.value || '';
    const district = districtInput.value.trim() || '';
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

// ── 10. Hydrate Dashboard Page ───────────────────────
async function hydrateDashboard() {
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

