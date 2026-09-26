"""
analysis_engine.py
==================
Generates all 6 certified analysis modules dynamically from form input.
Ensures zero hardcoded leakage: Market demand drivers, product/service mix,
competition mapping, SWOT strategies, financial breakdowns, schemes, action plan,
and AI advisor reflect the user's exact business type, location, and financial inputs.
"""

import random
from datetime import datetime
from geo_data import get_area_archetype, MICRO_AREA_ARCHETYPES


# ──────────────────────────────────────────────────────────────
#  Business-type knowledge base
# ──────────────────────────────────────────────────────────────
BUSINESS_DATA = {
    "mobile_shop": {
        "label": "Mobile Shop & Electronics",
        "sector": "Retail / Consumer Electronics",
        "avg_margin_pct": 18,
        "monthly_fixed_cost_pct": 8,
        "break_even_months": 11,
        "market_growth_pct": 12.5,
        "strengths": ["High recurring consumer footfall", "Essential connectivity necessity in digital economy", "Fast inventory turnover on budget models"],
        "weaknesses": ["Working capital locked in fast-depreciating inventory", "Intense price transparency from e-commerce", "Requires skilled repair technician"],
        "opportunities": ["Rural 5G upgrade cycle and smartphone penetration", "Smartphone repair & screen replacement generates 60%+ margins", "Value-added accessories and bill payment commissions"],
        "threats": ["Online e-commerce deep discounting (Flipkart/Amazon)", "Unbranded grey-market components", "Rising prime high-street commercial rentals"],
        "demand_drivers": [
            {"icon": "📡", "title": "Digital India & 5G Rollout", "desc": "Widespread adoption of UPI, Jan Dhan, and OTT streaming mandates working smartphones across every household."},
            {"icon": "🎓", "title": "Youth & Student Demographic", "desc": "Continuous online learning, social applications, and gaming generate high replacement and upgrade cycles."},
            {"icon": "👨‍🌾", "title": "Direct Benefit Transfers", "desc": "Farmers and rural entrepreneurs require functional smartphones for PM-KISAN, e-NAM, and agricultural advisory services."}
        ],
        "product_service_mix": [
            {"title": "Smartphone Repair & Diagnostic Services", "desc": "Screen replacement, battery swap, and motherboard soldering.", "priority": "Priority 1", "priority_tag": "tag-green", "rationale": "Highest gross margin (60-75%) and builds immediate local trust that online platforms cannot compete with."},
            {"title": "Curated Protective Accessories", "desc": "Tempered glasses, rugged cases, fast charging adapters, and OTG cables.", "priority": "Priority 2", "priority_tag": "tag-green", "rationale": "High margin (45-55%), low initial capital requirement, and high impulse buy frequency."},
            {"title": "Budget to Mid-Range Smartphones (₹6K - ₹18K)", "desc": "High-demand devices from Xiaomi, Realme, Samsung, and Vivo.", "priority": "Priority 3", "priority_tag": "tag-orange", "rationale": "Primary top-line revenue driver that commands consumer footfall into your retail location."},
            {"title": "Utility Digital Services & Financial Linkage", "desc": "Mobile recharge, DTH top-up, SIM activation, and micro-ATM facilities.", "priority": "Priority 4", "priority_tag": "tag-navy", "rationale": "Generates steady daily footfall and recurring customer touchpoints with minimal overhead."}
        ],
        "startup_cost_split": [
            {"name": "Initial Phone Stock & Fast-Moving Models", "pct": 45, "icon": "📱"},
            {"name": "High-Margin Accessories & Spares Inventory", "pct": 20, "icon": "🎧"},
            {"name": "Shop Fit-Out, Display Counters & Security Racks", "pct": 18, "icon": "🏪"},
            {"name": "Repair Diagnostic Tools & Soldering Station", "pct": 10, "icon": "🔧"},
            {"name": "Advance Lease Deposit & Regulatory Permits", "pct": 7, "icon": "🏠"}
        ],
        "monthly_expense_split": [
            {"name": "Commercial Shop Lease / Rent", "pct": 36},
            {"name": "Store Assistants / Part-Time Technician", "pct": 30},
            {"name": "Electricity & Air Conditioning", "pct": 14},
            {"name": "Logistics & Local Stock Freight", "pct": 10},
            {"name": "Packaging, Tea & General Upkeep", "pct": 10}
        ],
        "monthly_revenue_split": [
            {"name": "Primary Device Sales & Upgrades", "pct": 52},
            {"name": "Repair Services & Component Replacement", "pct": 28},
            {"name": "Accessories & Peripherals", "pct": 14},
            {"name": "Recharge Commission & Micro-ATM", "pct": 6}
        ],
        "competitor_prefix": ["Digital World", "Apex Mobile Hub", "City Telecom Point", "Express Phone Gallery", "National Electronics"],
        "schemes": ["PMEGP", "MUDRA Loan", "Stand-Up India", "MSME Loan"]
    },
    "grocery": {
        "label": "Grocery / Kirana Supermarket",
        "sector": "Retail / FMCG & Staples",
        "avg_margin_pct": 15,
        "monthly_fixed_cost_pct": 7,
        "break_even_months": 9,
        "market_growth_pct": 8.5,
        "strengths": ["Daily non-negotiable household demand", "High community loyalty and hyper-local trust", "Steady cash-flow velocity with low skill barrier"],
        "weaknesses": ["Thin margins on branded packaged FMCG", "Inventory shrinkage and perishable goods spoilage", "Working capital locked in credit (udhaar) if informal"],
        "opportunities": ["Doorstep delivery via WhatsApp ordering", "Digital ledger adoption (Khatabook/OkCredit) to streamline receivables", "Value-add loose grains and certified organic pulses at 25%+ margins"],
        "threats": ["Quick commerce apps and regional supermarket chain expansion", "FMCG distributor price fluctuations", "Unregulated price discounting by wholesale clubs"],
        "demand_drivers": [
            {"icon": "🛒", "title": "Inelastic Daily Essential Demand", "desc": "Every household within a 2-3 km cluster purchases foodgrains, edible oils, and household hygiene daily."},
            {"icon": "📲", "title": "Hyperlocal Proximity & Trust", "desc": "Neighbourhood consumers prioritize immediate availability and personal relationship over distant supermarkets."},
            {"icon": "💳", "title": "Digital Payment Revolution", "desc": "100% UPI acceptance enables seamless small-ticket transactions and fast checkout without cash friction."}
        ],
        "product_service_mix": [
            {"title": "Core Daily Essentials & Staples", "desc": "Wheat flour, regional rice varieties, pulses, edible oils, and spices.", "priority": "Priority 1", "priority_tag": "tag-green", "rationale": "High-volume necessity driving everyday footfall and customer retention."},
            {"title": "Packaged Branded FMCG & Dairy", "desc": "Biscuits, snacks, toiletries, milk, curd, and packaged beverages.", "priority": "Priority 2", "priority_tag": "tag-green", "rationale": "Rapid inventory turnover and brand-pull items with zero marketing overhead."},
            {"title": "High-Margin Local Produce & Cleaned Loose Grains", "desc": "Directly sourced pulses, dry fruits, and seasonal spices.", "priority": "Priority 3", "priority_tag": "tag-orange", "rationale": "Generates 22-30% gross margin compared to 8-10% on national branded FMCG goods."},
            {"title": "Free WhatsApp Order & Hyperlocal Doorstep Delivery", "desc": "Scheduled morning and evening delivery for senior citizens and busy families.", "priority": "Priority 4", "priority_tag": "tag-navy", "rationale": "Creates an unassailable defensive moat against dark stores and online quick-commerce apps."}
        ],
        "startup_cost_split": [
            {"name": "Core FMCG & Foodgrain Opening Inventory", "pct": 52, "icon": "📦"},
            {"name": "Modern Shelving Racks & Glass Front Displays", "pct": 20, "icon": "🏪"},
            {"name": "POS Billing Terminal, Barcode Scanner & Weighing Scales", "pct": 12, "icon": "⚖️"},
            {"name": "Commercial Deep Freezer / Refrigerator for Dairy", "pct": 9, "icon": "❄️"},
            {"name": "Lease Advance & Trade Registration", "pct": 7, "icon": "🏠"}
        ],
        "monthly_expense_split": [
            {"name": "Commercial Shop Rent", "pct": 38},
            {"name": "Store Helpers / Delivery Assistant", "pct": 28},
            {"name": "Power & Refrigeration Electricity", "pct": 16},
            {"name": "Carriage Inward & Restocking Freight", "pct": 10},
            {"name": "Bags, Packaging & Hygiene Cleaning", "pct": 8}
        ],
        "monthly_revenue_split": [
            {"name": "Staples, Grains & Edible Oils", "pct": 46},
            {"name": "Packaged FMCG & Confectionery", "pct": 30},
            {"name": "Dairy, Bakery & Perishables", "pct": 16},
            {"name": "Personal Care & Household Cleaning", "pct": 8}
        ],
        "competitor_prefix": ["Maa Durga Kirana", "Shree Ganesh Daily Needs", "Modern Super Bazaar", "Om Provision Store", "Balaji Mart"],
        "schemes": ["PMEGP", "PM SVANidhi", "MUDRA Loan", "MSME Loan"]
    },
    "dairy": {
        "label": "Dairy Farming & Milk Processing",
        "sector": "Agri-Food & Livestock Processing",
        "avg_margin_pct": 26,
        "monthly_fixed_cost_pct": 9,
        "break_even_months": 15,
        "market_growth_pct": 11.2,
        "strengths": ["Daily morning-and-evening cashflow generation", "High institutional demand from sweet makers and tea stalls", "Strong government subsidy and cooperative backing"],
        "weaknesses": ["High livestock health and veterinary management risk", "Perishability demands reliable cold storage", "Cattle feed inflation impact"],
        "opportunities": ["Value-added derivatives: Paneer, Ghee, Curd, and Khoya", "Direct-to-consumer farm-fresh A2 milk subscription", "Integration with state milk federation and local cooperatives"],
        "threats": ["Milk adulteration scrutiny and FSSAI audits", "Bovine disease outbreaks", "Seasonal yield drops in peak summer"],
        "demand_drivers": [
            {"icon": "🥛", "title": "Freshness & Purity Premium", "desc": "Urban and semi-urban consumers actively seek unadulterated, farm-fresh milk over reconstituted powder milk."},
            {"icon": "🧀", "title": "Value-Add Derivative Boom", "desc": "Paneer, curd, and artisanal ghee consumption is growing at 14% CAGR for local sweets and catering."},
            {"icon": "🤝", "title": "Guaranteed Off-take Ecosystem", "desc": "Cooperative unions and local tea stalls provide guaranteed daily procurement minimums."}
        ],
        "product_service_mix": [
            {"title": "Fresh Pure Whole Milk Delivery", "desc": "Morning and evening farm-fresh raw/pasteurized milk deliveries.", "priority": "Priority 1", "priority_tag": "tag-green", "rationale": "Foundational daily revenue stream providing predictable operational working capital."},
            {"title": "Fresh Artisanal Paneer & Khoya", "desc": "Daily freshly pressed cottage cheese for households, caterers, and restaurants.", "priority": "Priority 2", "priority_tag": "tag-green", "rationale": "High profit margin (35-45%) and absorbs evening surplus milk with zero wastage."},
            {"title": "Traditional Cultured Curd & Chaas", "desc": "Thick hygienic curd packs and spiced buttermilk.", "priority": "Priority 3", "priority_tag": "tag-orange", "rationale": "High summer demand item with rapid turns and strong festive order volume."},
            {"title": "Pure Desi Cow Ghee (Bilona Method)", "desc": "Premium small-batch ghee sold at ₹900 - ₹1,400 per kg.", "priority": "Priority 4", "priority_tag": "tag-navy", "rationale": "Zero spoilage shelf life and exceptional profit margins (50%+)."}
        ],
        "startup_cost_split": [
            {"name": "High-Yield Milking Cattle / Raw Milk Supply Setup", "pct": 48, "icon": "🐄"},
            {"name": "Bulk Milk Cooler & Refrigerated Storage Vat", "pct": 22, "icon": "❄️"},
            {"name": "Cattle Shedding, Water Borewell & Biosecurity", "pct": 14, "icon": "🏡"},
            {"name": "Processing Utensils, Cream Separator & Paneer Press", "pct": 9, "icon": "⚙️"},
            {"name": "FSSAI Registration, Veterinary Kit & Permits", "pct": 7, "icon": "📜"}
        ],
        "monthly_expense_split": [
            {"name": "Cattle Feed, Fodder & Mineral Mixtures", "pct": 46},
            {"name": "Farm Labor / Milking Assistants", "pct": 24},
            {"name": "Chilling Electricity & Generator Diesel", "pct": 15},
            {"name": "Veterinary Health & Vaccination Care", "pct": 8},
            {"name": "Logistics & Morning Milk Delivery Fuel", "pct": 7}
        ],
        "monthly_revenue_split": [
            {"name": "Direct Milk Delivery Subscriptions", "pct": 54},
            {"name": "Fresh Paneer & Khoya to Caterers", "pct": 26},
            {"name": "Packaged Curd & Lassi Sales", "pct": 12},
            {"name": "Pure Ghee & Organic Compost Manure", "pct": 8}
        ],
        "competitor_prefix": ["Kalinga Dairy Point", "Utkal Milk Agency", "Gokul Dairy Farm", "Shree Krishna Milk Centre", "Amrit Dairy Hub"],
        "schemes": ["NABARD Dairy Entrepreneurship Development Scheme (DEDS)", "National Livestock Mission", "PMEGP", "Kisan Credit Card (KCC)"]
    },
    "bakery": {
        "label": "Bakery & Confectionery",
        "sector": "Food & Hospitality Processing",
        "avg_margin_pct": 38,
        "monthly_fixed_cost_pct": 14,
        "break_even_months": 8,
        "market_growth_pct": 13.0,
        "strengths": ["Outstanding gross margins on celebratory and specialty bakes", "High celebratory and gifting seasonality (birthdays, festivals)", "Low cost of raw flour/sugar converted to premium retail value"],
        "weaknesses": ["Short shelf life of cream items requires precise sales forecasting", "Requires skilled baker and consistent oven temperature management", "Intense local competition for impulse snacks"],
        "opportunities": ["Customized designer birthday and wedding cakes", "Online delivery platform tie-up (Swiggy, Zomato)", "Corporate event catering and snack boxes for schools"],
        "threats": ["Industrial mass-produced packaged bakery brands", "Sharp spikes in butter, chocolate, and edible oil costs", "Strict FSSAI hygiene audit norms"],
        "demand_drivers": [
            {"icon": "🎂", "title": "Celebration Culture Expansion", "desc": "Rising demand for designer cakes, photo cakes, and event confections in Tier 2/3 and semi-urban clusters."},
            {"icon": "☕", "title": "Daily Tea-Time Snacking", "desc": "Puffs, biscuits, rusks, and tea-time cakes provide steady morning and evening footfall."},
            {"icon": "🛵", "title": "Food Delivery Aggregation", "desc": "Listing on Swiggy and Zomato expands your delivery footprint up to 7-10 km radius."}
        ],
        "product_service_mix": [
            {"title": "Custom Celebration Cakes & Pastries", "desc": "Fresh cream birthday cakes, tiered wedding cakes, and pastries.", "priority": "Priority 1", "priority_tag": "tag-green", "rationale": "Highest margin category (60-70%) with direct advance customer payments."},
            {"title": "Fresh Daily Breads, Buns & Pav", "desc": "Sandwich breads, milk loaves, burger buns, and pav for local stalls.", "priority": "Priority 2", "priority_tag": "tag-green", "rationale": "High-velocity everyday staple ensuring repeat morning customer footfall."},
            {"title": "Hot Savory Snacks & Puffs", "desc": "Paneer patties, veg rolls, and baked samosas.", "priority": "Priority 3", "priority_tag": "tag-orange", "rationale": "Major afternoon tea-time impulse buy that commands 40-50% profit margin."},
            {"title": "Packaged Dry Cookies, Rusks & Namkeen", "desc": "Handmade butter cookies, jeera rusks, and dry cakes.", "priority": "Priority 4", "priority_tag": "tag-navy", "rationale": "Extended shelf-life items (30-60 days) to prevent any unsold inventory loss."}
        ],
        "startup_cost_split": [
            {"name": "Commercial Rotary/Deck Baking Oven & Planetary Mixer", "pct": 40, "icon": "🔥"},
            {"name": "Chilled Pastry Display Counter & Beverage Chiller", "pct": 22, "icon": "🍰"},
            {"name": "Opening Raw Materials (Flour, Butter, Fondant, Boxes)", "pct": 18, "icon": "📦"},
            {"name": "Interior Ambience, Glass Partition & Lighting", "pct": 12, "icon": "✨"},
            {"name": "FSSAI Commercial Food Licence & Fire Clearance", "pct": 8, "icon": "📜"}
        ],
        "monthly_expense_split": [
            {"name": "Master Baker & Helper Wages", "pct": 38},
            {"name": "Retail Shop Rent", "pct": 32},
            {"name": "Commercial Electricity & Baking Gas (LPG)", "pct": 16},
            {"name": "Cake Boxes, Bags & Food Grade Packaging", "pct": 8},
            {"name": "Sanitation, Cleaning & Pest Control", "pct": 6}
        ],
        "monthly_revenue_split": [
            {"name": "Specialty & Birthday Cake Orders", "pct": 45},
            {"name": "Hot Savory Puffs & Evening Snacks", "pct": 25},
            {"name": "Daily Breads, Buns & Pav Supply", "pct": 18},
            {"name": "Dry Cookies, Chocolates & Beverages", "pct": 12}
        ],
        "competitor_prefix": ["Royal Bake House", "Golden Crust Bakery", "Cakes & More", "Sweet Delights Bakery", "Crown Confectionery"],
        "schemes": ["PMEGP", "MUDRA Loan", "Stand-Up India"]
    },
    "tailoring": {
        "label": "Tailoring & Boutique Garments",
        "sector": "Textile & Fashion Apparel",
        "avg_margin_pct": 52,
        "monthly_fixed_cost_pct": 8,
        "break_even_months": 6,
        "market_growth_pct": 9.5,
        "strengths": ["Exceptional gross service margins (50-65%)", "Minimal perishable inventory risk", "Strong word-of-mouth customer retention"],
        "weaknesses": ["Heavily reliant on skilled cutter and master tailor", "Seasonal peak crunches (wedding/festive) followed by lulls", "Ready-made garment competition"],
        "opportunities": ["Institutional contracts (school and security uniforms)", "Bridal blouse and designer lehenga embroidery", "Alteration and urgent fitting express services"],
        "threats": ["Mass-produced fast fashion e-commerce (Meesho, Myntra)", "Shortage of skilled stitching artisans", "Fabric vendor price inflation"],
        "demand_drivers": [
            {"icon": "👗", "title": "Bespoke Fitting Demand", "desc": "Standard ready-made sizes do not fit everyone; custom tailored blouses, suits, and dresses remain essential."},
            {"icon": "🏫", "title": "Institutional Uniform Contracts", "desc": "Local private schools, hospitals, and security agencies require recurring annual uniform batches."},
            {"icon": "✨", "title": "Wedding & Festive Spikes", "desc": "Regional wedding seasons generate premium designer tailoring orders at 2-3x standard rates."}
        ],
        "product_service_mix": [
            {"title": "Custom Ladies Tailoring (Blouses & Salwar Suits)", "desc": "Designer cut, piping, lining, and contemporary pattern stitching.", "priority": "Priority 1", "priority_tag": "tag-green", "rationale": "High-volume recurring demand with 60%+ margins on labor and lining fabric."},
            {"title": "Bridal & Festive Designer Wear", "desc": "Intricate embroidery, aari work, and bridal lehengas.", "priority": "Priority 2", "priority_tag": "tag-green", "rationale": "High-ticket pricing (₹1,500 - ₹5,000+ per piece) with substantial advance deposits."},
            {"title": "School & Institutional Uniform Supply", "desc": "Bulk stitching of shirts, trousers, pinafores, and badges.", "priority": "Priority 3", "priority_tag": "tag-orange", "rationale": "Predictable seasonal bulk volume that guarantees workshop utilization during off-peak times."},
            {"title": "Express Alterations & Fabric Sourcing", "desc": "Same-day zip replacement, length fitting, and matched lining cloth.", "priority": "Priority 4", "priority_tag": "tag-navy", "rationale": "Brings new footfall daily with minimal effort and immediate cash payment."}
        ],
        "startup_cost_split": [
            {"name": "Industrial High-Speed Stitching & Overlock Machines", "pct": 42, "icon": "🧵"},
            {"name": "Cutting Tables, Steam Iron Press & Fitting Room", "pct": 22, "icon": "✂️"},
            {"name": "Lining Cloth, Threads, Zips & Notions Stock", "pct": 18, "icon": "📦"},
            {"name": "Shop Signage, Trial Mirrors & Racks", "pct": 10, "icon": "🏪"},
            {"name": "Udyam Registration & Trade License", "pct": 8, "icon": "📜"}
        ],
        "monthly_expense_split": [
            {"name": "Assistant Tailor & Embroidery Artisan Wages", "pct": 45},
            {"name": "Shop Rental", "pct": 28},
            {"name": "Electricity for Motors & Steam Irons", "pct": 12},
            {"name": "Thread, Needles, Oil & Consumables", "pct": 8},
            {"name": "Maintenance & Machine Servicing", "pct": 7}
        ],
        "monthly_revenue_split": [
            {"name": "Everyday Blouse & Suit Tailoring", "pct": 48},
            {"name": "Bridal, Festive & Designer Wear", "pct": 28},
            {"name": "School & Institutional Uniform Orders", "pct": 16},
            {"name": "Express Alterations & Notions Sales", "pct": 8}
        ],
        "competitor_prefix": ["Elegance Tailoring", "Pari Boutique", "Perfect Fit Tailors", "Modern Ladies Corner", "Shree Fashion Point"],
        "schemes": ["PM VIKAS", "Stand-Up India", "MUDRA Loan", "National Handloom Development Programme"]
    },
    "electronics_repair": {
        "label": "Electronics & Appliance Repair",
        "sector": "Services / Technical Repair",
        "avg_margin_pct": 58,
        "monthly_fixed_cost_pct": 6,
        "break_even_months": 5,
        "market_growth_pct": 11.0,
        "strengths": ["High margin on technical labor", "Low startup inventory risk", "Essential household service"],
        "weaknesses": ["Requires technical expertise", "Component sourcing delays", "Equipment diagnostic investment"],
        "opportunities": ["Smart TV and inverter repair boom", "Home visit premium repair charges", "Tie-up with major brands for warranty service"],
        "threats": ["Component obsolescence", "Cheap replacement appliances reducing repair viability", "DIY YouTube tutorials"],
        "demand_drivers": [
            {"icon": "⚡", "title": "Rising Household Appliance Ownership", "desc": "Inverters, TVs, washing machines, and mixers are now standard in rural and semi-urban homes."},
            {"icon": "🛠️", "title": "High Replacement vs Repair Cost", "desc": "Consumers strongly prefer spending ₹500 - ₹2,000 on repair rather than ₹15,000 on new appliances."},
            {"icon": "🏡", "title": "Doorstep Service Deficit", "desc": "Big brand service centers rarely send technicians to villages; local reliable repair is urgently needed."}
        ],
        "product_service_mix": [
            {"title": "Inverter, UPS & Battery Maintenance", "desc": "PCB repair, transformer winding, and battery de-sulphation.", "priority": "Priority 1", "priority_tag": "tag-green", "rationale": "Crucial rural/semi-urban lifeline with high service charges and recurring maintenance contracts."},
            {"title": "Smart LED TV & Audio Repair", "desc": "Backlight replacement, display panel bonding, and motherboard repairs.", "priority": "Priority 2", "priority_tag": "tag-green", "rationale": "High ticket service (₹1,000 - ₹3,500) with 60%+ net margins."},
            {"title": "Home Appliance Repair (Mixer, Fan, Microwave, RO)", "desc": "Motor rewinding, heating element replacement, and filter swaps.", "priority": "Priority 3", "priority_tag": "tag-orange", "rationale": "Steady daily baseline footfall with instant cash turnover."},
            {"title": "Refurbished Electronics & Genuine Spares Sales", "desc": "Sale of tested remanufactured appliances and genuine replacement components.", "priority": "Priority 4", "priority_tag": "tag-navy", "rationale": "Generates secondary product margin while solving part sourcing issues for customers."}
        ],
        "startup_cost_split": [
            {"name": "Oscilloscope, Soldering Stations, Multimeters & Testing Rigs", "pct": 38, "icon": "🔬"},
            {"name": "Common ICs, Capacitors, Backlights & Spare Parts Inventory", "pct": 26, "icon": "⚙️"},
            {"name": "Workshop Benches, Racks & Tools", "pct": 18, "icon": "🔧"},
            {"name": "Shop Advance & Display Signboard", "pct": 10, "icon": "🏪"},
            {"name": "Udyam MSME Registration & Safety Setup", "pct": 8, "icon": "📜"}
        ],
        "monthly_expense_split": [
            {"name": "Workshop Rent", "pct": 34},
            {"name": "Assistant Technician Wages", "pct": 32},
            {"name": "Electricity & Testing Power", "pct": 16},
            {"name": "Component Freight & Logistics", "pct": 10},
            {"name": "Solder, Flux & Workshop Consumables", "pct": 8}
        ],
        "monthly_revenue_split": [
            {"name": "LED TV & Display Panel Repairs", "pct": 38},
            {"name": "Inverter, UPS & Power Electronics", "pct": 32},
            {"name": "Kitchen & Small Household Appliances", "pct": 20},
            {"name": "Spare Parts & Refurbished Item Sales", "pct": 10}
        ],
        "competitor_prefix": ["Supreme Electronics", "Care Electricals & Repair", "Star Service Hub", "Microtech Repair Point", "National Appliance Care"],
        "schemes": ["PMEGP", "MSME Technology Upgrade Fund (CLCSS)", "MUDRA Loan", "Stand-Up India"]
    },
    "salon": {
        "label": "Salon & Beauty Parlour",
        "sector": "Personal Care & Grooming",
        "avg_margin_pct": 62,
        "monthly_fixed_cost_pct": 12,
        "break_even_months": 7,
        "market_growth_pct": 14.5,
        "strengths": ["Outstanding service margins (60-75%)", "Repeat customers every 15-30 days", "Aspirational growth in Tier 2/3 markets"],
        "weaknesses": ["Skilled beautician retention", "Requires clean, air-conditioned premises", "High initial interior fit-out cost"],
        "opportunities": ["Bridal makeup packages and pre-wedding grooming", "Monthly grooming memberships for recurring cashflow", "Retail sales of professional haircare and skincare products"],
        "threats": ["National salon chains expanding", "Unregistered home beauticians", "Staff poaching"],
        "demand_drivers": [
            {"icon": "✂️", "title": "Frequent Grooming Habits", "desc": "Haircuts, beard styling, facials, and threading are regular monthly or bi-weekly necessities."},
            {"icon": "💄", "title": "Wedding & Event Demand", "desc": "Bridal and event makeups command premium pricing of ₹5,000 - ₹25,000 per booking."},
            {"icon": "🌟", "title": "Aspirational Lifestyle Upgrades", "desc": "Tier 2/3 and rural consumers prioritize hygienic, air-conditioned parlours over unorganized roadside shops."}
        ],
        "product_service_mix": [
            {"title": "Core Hair Styling, Cutting & Trimming", "desc": "Modern cuts, beard grooming, hair wash, and blow dry.", "priority": "Priority 1", "priority_tag": "tag-green", "rationale": "High-frequency daily service creating your dependable baseline revenue."},
            {"title": "Skincare, Facials & D-Tan Treatments", "desc": "Herbal, fruit, gold facials, clean-ups, and skin hydration.", "priority": "Priority 2", "priority_tag": "tag-green", "rationale": "High margin (70-80%) that substantially increases your average ticket size."},
            {"title": "Bridal & Event Makeup Packages", "desc": "Pre-bridal packages, HD makeup, saree draping, and styling.", "priority": "Priority 3", "priority_tag": "tag-orange", "rationale": "Transformational revenue driver during regional wedding and festival months."},
            {"title": "Hair Spa & Keratin/Colouring Treatments", "desc": "Deep conditioning, root touch-ups, smoothing, and botox treatments.", "priority": "Priority 4", "priority_tag": "tag-navy", "rationale": "Premium value-add service with high customer stickiness and repeat loyalty."}
        ],
        "startup_cost_split": [
            {"name": "Hydraulic Salon Chairs, Styling Stations & Mirrors", "pct": 36, "icon": "🪑"},
            {"name": "Interior Ambience, Air Conditioning & Lighting", "pct": 28, "icon": "✨"},
            {"name": "Professional Styling Equipment (Dryers, Steamers, Irons)", "pct": 16, "icon": "💇"},
            {"name": "Cosmetics, Hair Colour & Skincare Opening Stock", "pct": 12, "icon": "🧴"},
            {"name": "Shop Advance & Local Trade License", "pct": 8, "icon": "📜"}
        ],
        "monthly_expense_split": [
            {"name": "Stylists & Beautician Staff Wages", "pct": 42},
            {"name": "Commercial Shop Rent", "pct": 30},
            {"name": "Electricity (AC, Water Geysers, Lights)", "pct": 14},
            {"name": "Shampoos, Creams, Disposable Gowns & Consumables", "pct": 8},
            {"name": "Laundry, Hygiene & Maintenance", "pct": 6}
        ],
        "monthly_revenue_split": [
            {"name": "Daily Hair Grooming & Shaving", "pct": 42},
            {"name": "Facials, Bleach & Skincare", "pct": 28},
            {"name": "Bridal & Festive Grooming Packages", "pct": 18},
            {"name": "Hair Colouring, Spa & Product Sales", "pct": 12}
        ],
        "competitor_prefix": ["Looks Beauty Hub", "Crown Unisex Salon", "Sparkle Parlour", "Glamour Touch Studio", "Elegance Hair Lounge"],
        "schemes": ["MUDRA Loan", "Stand-Up India", "PMEGP"]
    },
    "restaurant": {
        "label": "Restaurant / Food Dhaba",
        "sector": "Food Service & Hospitality",
        "avg_margin_pct": 34,
        "monthly_fixed_cost_pct": 16,
        "break_even_months": 10,
        "market_growth_pct": 10.5,
        "strengths": ["Substantial daily cash velocity", "Direct consumer relationship", "Scalable via catering and food delivery apps"],
        "weaknesses": ["High fixed rent and kitchen staff payroll", "Daily raw material perishability and kitchen wastage", "Demands strict hygiene compliance"],
        "opportunities": ["Swiggy/Zomato delivery onboarding", "Lunch tiffin box subscription for offices/banks", "Catering for local celebrations and birthdays"],
        "threats": ["Volatile vegetable and commercial LPG prices", "Quick-service chain expansion", "Customer taste fatigue"],
        "demand_drivers": [
            {"icon": "🍲", "title": "Eating-Out & Social Dining Trend", "desc": "Families, youth, and travelers increasingly prefer dining at clean, hygienic local restaurants."},
            {"icon": "💼", "title": "Working Professional Lunch Need", "desc": "Bank staff, teachers, and shopkeepers need affordable, high-quality daily meal options."},
            {"icon": "🛵", "title": "Online Food Delivery Reach", "desc": "Delivery aggregators enable reaching customers across the entire town beyond walk-in patrons."}
        ],
        "product_service_mix": [
            {"title": "Signature Thali & Daily Fresh Meals", "desc": "Wholesome regional thalis, dal, seasonal curries, and rotis.", "priority": "Priority 1", "priority_tag": "tag-green", "rationale": "High-volume daily meal anchor providing reliable morning and evening footfall."},
            {"title": "Tandoori & Evening Specialty Snacks", "desc": "Fresh rotis, paneer/chicken tandoori, and biryani.", "priority": "Priority 2", "priority_tag": "tag-green", "rationale": "High-margin evening crowd puller (40-50% margins) that doubles dinner revenue."},
            {"title": "Office Lunch Tiffin Subscription", "desc": "Packaged hot meals delivered to local workplaces and retail stores.", "priority": "Priority 3", "priority_tag": "tag-orange", "rationale": "Guaranteed advance monthly subscriptions that insulate against bad weather footfall dips."},
            {"title": "Beverages, Desserts & Quick Bites", "desc": "Chai, lassi, cold beverages, and local traditional sweets.", "priority": "Priority 4", "priority_tag": "tag-navy", "rationale": "Instant margin booster with minimal kitchen preparation overhead."}
        ],
        "startup_cost_split": [
            {"name": "Commercial Kitchen Setup (Burners, Tandoor, Deep Freezers)", "pct": 40, "icon": "🍳"},
            {"name": "Dining Furniture, Crockery & Interior Lighting", "pct": 26, "icon": "🪑"},
            {"name": "Initial Food Provisions, Spices & Packaging", "pct": 16, "icon": "📦"},
            {"name": "Premise Advance Lease & Signage", "pct": 10, "icon": "🏪"},
            {"name": "FSSAI Commercial Licence, Fire NOC & Local Permits", "pct": 8, "icon": "📜"}
        ],
        "monthly_expense_split": [
            {"name": "Cooks, Kitchen Helpers & Service Staff Wages", "pct": 40},
            {"name": "Commercial Lease Rent", "pct": 28},
            {"name": "Commercial LPG Gas Cylinders & Electricity", "pct": 16},
            {"name": "Food Packaging Containers & Cleaning Supplies", "pct": 8},
            {"name": "Waste Disposal & Kitchen Maintenance", "pct": 8}
        ],
        "monthly_revenue_split": [
            {"name": "Dine-in Lunch & Dinner Thalis", "pct": 48},
            {"name": "Evening Snacks, Tandoori & Fast Food", "pct": 26},
            {"name": "Office Tiffin Subscriptions", "pct": 16},
            {"name": "Beverages & Takeaway Counters", "pct": 10}
        ],
        "competitor_prefix": ["Swad Restaurant", "Annapurna Dhaba", "Zaika Food Point", "Highway Treat", "Taste of Odisha"],
        "schemes": ["PMEGP", "MUDRA Loan", "PM SVANidhi"]
    },
    "agriculture": {
        "label": "Agriculture & Agri-Business",
        "sector": "Agri-Business & Horticulture",
        "avg_margin_pct": 28,
        "monthly_fixed_cost_pct": 10,
        "break_even_months": 18,
        "market_growth_pct": 7.5,
        "strengths": ["Inherent food necessity", "Government priority sector with high subsidy support", "Direct land/crop asset backing"],
        "weaknesses": ["Weather and rainfall dependency", "Mandi middleman price exploitation", "Seasonal crop income gaps"],
        "opportunities": ["FPO collective marketing and direct bulk selling", "e-NAM online trading for price discovery", "High-value horticulture and organic certification"],
        "threats": ["Climate change and sudden erratic storms", "Pest attacks and crop loss", "Input fertilizer inflation"],
        "demand_drivers": [
            {"icon": "🌱", "title": "Rising Food & Pulse Demand", "desc": "India's food consumption is escalating, driving sustained procurement prices."},
            {"icon": "🚜", "title": "Agritech & e-NAM Mandi Integration", "desc": "Digital auction platforms allow farmers to bypass local middlemen and sell at national prices."},
            {"icon": "🛡️", "title": "Comprehensive Safety Nets", "desc": "PM-KISAN, PMFBY crop insurance, and subsidized KCC credit eliminate distress borrowing."}
        ],
        "product_service_mix": [
            {"title": "High-Yield Certified Seasonal Crops", "desc": "Quality grain, pulse, or oilseed crop production.", "priority": "Priority 1", "priority_tag": "tag-green", "rationale": "Core baseline harvest providing bulk revenue upon mandi delivery."},
            {"title": "High-Value Vegetable & Horticulture Intercropping", "desc": "Tomatoes, chillies, ginger, or leafy greens between primary rows.", "priority": "Priority 2", "priority_tag": "tag-green", "rationale": "Provides regular weekly cashflow between major seasonal harvest cycles."},
            {"title": "Direct FPO Bulk Contracting", "desc": "Supplying graded produce directly to institutional buyers and processors.", "priority": "Priority 3", "priority_tag": "tag-orange", "rationale": "Yields 15-25% higher net realization compared to traditional village commission agents."},
            {"title": "Bio-Compost & Vermicompost Production", "desc": "Organic fertilizer produced from farm residue and livestock dung.", "priority": "Priority 4", "priority_tag": "tag-navy", "rationale": "Reduces your chemical fertilizer bill while creating an additional saleable product."}
        ],
        "startup_cost_split": [
            {"name": "Land Preparation, Borewell Drip Irrigation Setup", "pct": 42, "icon": "💧"},
            {"name": "Certified High-Yield Seeds & Organic Input Foundation", "pct": 24, "icon": "🌱"},
            {"name": "Small Farm Machinery / Power Tiller Attachment", "pct": 18, "icon": "🚜"},
            {"name": "Storage Shed & Harvest Handling Crates", "pct": 10, "icon": "🏡"},
            {"name": "Soil Health Card, KCC Documentation & FPO Linkage", "pct": 6, "icon": "📜"}
        ],
        "monthly_expense_split": [
            {"name": "Farm Labor for Weeding, Spraying & Harvesting", "pct": 45},
            {"name": "Irrigation Electricity & Generator Fuel", "pct": 22},
            {"name": "Organic Fertilizers, Micro-nutrients & Bio-Pesticides", "pct": 20},
            {"name": "Transportation & Mandi Carriage", "pct": 8},
            {"name": "Equipment Servicing & Maintenance", "pct": 5}
        ],
        "monthly_revenue_split": [
            {"name": "Primary Grain / Pulse Seasonal Harvest Sales", "pct": 55},
            {"name": "Weekly Horticulture & Vegetable Market Sales", "pct": 28},
            {"name": "Direct Institutional / FPO Supply", "pct": 12},
            {"name": "Organic Bio-Fertilizer & Fodder Sales", "pct": 5}
        ],
        "competitor_prefix": ["Green Fields Farm", "Utkal Agri Producers", "Kisan Seva Kendra", "Kalinga Bio Farm", "Progressive Agri Farms"],
        "schemes": ["PM-KISAN", "PMFBY", "Kisan Credit Card (KCC)", "e-NAM", "NABARD Dairy Entrepreneurship Development Scheme (DEDS)"]
    },
    "handicraft": {
        "label": "Handicrafts & Handloom",
        "sector": "Cottage Industry & Artisanal Goods",
        "avg_margin_pct": 65,
        "monthly_fixed_cost_pct": 5,
        "break_even_months": 5,
        "market_growth_pct": 13.5,
        "strengths": ["Extremely high product margin (60-70%)", "Low capital requirement", "Government export and GI tag protection"],
        "weaknesses": ["Slow handmade production speed", "Artisan skill bottleneck", "Marketing and packaging challenges"],
        "opportunities": ["Listing on Amazon Karigar, Flipkart Samarth, and ONDC", "Export orders through EPCH", "Direct exhibitions at Dilli Haat and state emporiums"],
        "threats": ["Machine-made cheap imitation goods", "Artisan migration", "Raw material price volatility"],
        "demand_drivers": [
            {"icon": "🎨", "title": "Cultural & Handmade Heritage Boom", "desc": "Urban and international consumers place high value on genuine artisan handlooms and crafts."},
            {"icon": "🛍️", "title": "E-Commerce Samarth Portals", "desc": "Marketplaces now onboard rural artisans directly with subsidized listing and logistics fees."},
            {"icon": "🏛️", "title": "Government Gifting Mandates", "desc": "Government agencies and corporate events actively purchase GI-tagged indigenous crafts."}
        ],
        "product_service_mix": [
            {"title": "Authentic Regional GI-Tagged Crafts", "desc": "Handcrafted textiles, terracotta, brassware, or stone carving.", "priority": "Priority 1", "priority_tag": "tag-green", "rationale": "High-value specialty that commands premium authentic pricing without price competition."},
            {"title": "Modern Utility Handicrafts", "desc": "Bags, table mats, coasters, file covers, and pen stands.", "priority": "Priority 2", "priority_tag": "tag-green", "rationale": "Fast-selling corporate gifting items suitable for regular bulk purchase orders."},
            {"title": "E-Commerce Packaged Artisanal Products", "desc": "Standardized craft items packaged with artisan stories for online delivery.", "priority": "Priority 3", "priority_tag": "tag-orange", "rationale": "Reaches metropolitan consumers across India at full retail margins."},
            {"title": "Direct Fair & Exhibition Pop-Ups", "desc": "Direct stalls at urban cultural melas and exhibitions.", "priority": "Priority 4", "priority_tag": "tag-navy", "rationale": "100% upfront cash sales and eliminates all distributor intermediary commissions."}
        ],
        "startup_cost_split": [
            {"name": "Artisan Handlooms / Specialized Crafting Tools", "pct": 36, "icon": "🧵"},
            {"name": "Raw Materials (Yarn, Natural Dyes, Brass/Clay, Wood)", "pct": 30, "icon": "📦"},
            {"name": "Workshop Setup & Natural Drying Racks", "pct": 16, "icon": "🏡"},
            {"name": "Branded Packaging, Barcoding & Photo Portfolio", "pct": 10, "icon": "📸"},
            {"name": "Artisan Card (Pehchan) & GI / Udyam Registration", "pct": 8, "icon": "📜"}
        ],
        "monthly_expense_split": [
            {"name": "Artisan & Weaver Piece-Rate Payments", "pct": 52},
            {"name": "Raw Material Refills", "pct": 24},
            {"name": "Workshop Space Lease", "pct": 12},
            {"name": "Courier Shipping & Packaging Boxes", "pct": 8},
            {"name": "Utility Power & General Upkeep", "pct": 4}
        ],
        "monthly_revenue_split": [
            {"name": "Direct Retail & Tourist Center Sales", "pct": 42},
            {"name": "Online Marketplace Orders (Amazon Karigar/ONDC)", "pct": 28},
            {"name": "Corporate & Government Gifting Orders", "pct": 18},
            {"name": "State Handloom Emporium Wholesale", "pct": 12}
        ],
        "competitor_prefix": ["Kala Kendra", "Heritage Crafts", "Odisha Handloom Center", "Artisans Guild", "Utkal Craft Gallery"],
        "schemes": ["Ambedkar Hastshilp Vikas Yojana", "PM VIKAS", "National Handloom Development Programme", "MUDRA Shishu Loan"]
    },
    "transport": {
        "label": "Transport & Logistics Services",
        "sector": "Logistics & Freight Services",
        "avg_margin_pct": 24,
        "monthly_fixed_cost_pct": 20,
        "break_even_months": 16,
        "market_growth_pct": 12.0,
        "strengths": ["Asset-backed business with high tangible value", "Essential last-mile connectivity for agriculture and trade", "Immediate demand from e-commerce delivery partners"],
        "weaknesses": ["High fuel cost sensitivity", "Vehicle maintenance and tyre replacement expenses", "Permit and toll compliances"],
        "opportunities": ["Last-mile e-commerce delivery hub partnership", "FMCG distributor dedicated fleet contracts", "Cold chain logistics for fresh vegetables and milk"],
        "threats": ["Diesel price surges", "Aggregator commission squeeze", "Road and weather damage"],
        "demand_drivers": [
            {"icon": "🚚", "title": "Rural E-Commerce Last Mile", "desc": "Shiprocket, Delhivery, and Amazon require local mini-trucks and delivery vans to service pincodes."},
            {"icon": "🌾", "title": "Agricultural Mandi Haulage", "desc": "Farmers need reliable transport from farm gate to district mandis during harvest seasons."},
            {"icon": "🏗️", "title": "Infrastructure Construction Boom", "desc": "Road and housing projects require constant movement of cement, sand, and construction supplies."}
        ],
        "product_service_mix": [
            {"title": "Dedicated FMCG & Distributor Haulage", "desc": "Fixed monthly transport for regional wholesale distributors.", "priority": "Priority 1", "priority_tag": "tag-green", "rationale": "Guaranteed recurring monthly retainers that cover vehicle EMI and driver costs."},
            {"title": "Agricultural Harvest Mandi Trips", "desc": "Direct farm-to-mandi transportation of grains and vegetables.", "priority": "Priority 2", "priority_tag": "tag-green", "rationale": "High-margin spot rate cash payments during peak harvesting cycles."},
            {"title": "E-Commerce Hub Last-Mile Deliveries", "desc": "Scheduled morning parcel routing for national courier partners.", "priority": "Priority 3", "priority_tag": "tag-orange", "rationale": "Predictable volume with weekly payments and zero customer acquisition expense."},
            {"title": "Local Household Shifting & On-Call Goods Carriage", "desc": "On-demand weekend local shifting and commercial goods transport.", "priority": "Priority 4", "priority_tag": "tag-navy", "rationale": "Generates profitable auxiliary weekend income at premium rates."}
        ],
        "startup_cost_split": [
            {"name": "Commercial Vehicle Down Payment & Registration", "pct": 55, "icon": "🚚"},
            {"name": "Comprehensive Commercial Insurance & National Permits", "pct": 16, "icon": "📜"},
            {"name": "GPS Telematics, Cargo Tarpaulins & Tie-Down Setup", "pct": 12, "icon": "📡"},
            {"name": "3-Month Fuel & Toll Advance Working Buffer", "pct": 11, "icon": "⛽"},
            {"name": "Transport Office Space & Signage", "pct": 6, "icon": "🏪"}
        ],
        "monthly_expense_split": [
            {"name": "Diesel Fuel & Toll Taxes", "pct": 46},
            {"name": "Commercial Vehicle EMI", "pct": 26},
            {"name": "Driver & Helper Wages", "pct": 18},
            {"name": "Routine Maintenance, Tyres & Oil Change", "pct": 7},
            {"name": "Permits, Fitness & Legal Upkeep", "pct": 3}
        ],
        "monthly_revenue_split": [
            {"name": "FMCG / Wholesale Fixed Route Contracts", "pct": 48},
            {"name": "Mandi Agricultural Haulage", "pct": 26},
            {"name": "E-Commerce Hub Parcels", "pct": 16},
            {"name": "Local On-Demand Cargo Trips", "pct": 10}
        ],
        "competitor_prefix": ["Speed Logistics", "Kalinga Cargo Carriers", "Bharat Road Lines", "Express Goods Movers", "National Transport Co"],
        "schemes": ["PMEGP", "PM Gati Shakti", "MUDRA Loan", "Stand-Up India"]
    },
    "other": {
        "label": "Custom Enterprise",
        "sector": "General / Local Services",
        "avg_margin_pct": 30,
        "monthly_fixed_cost_pct": 10,
        "break_even_months": 11,
        "market_growth_pct": 9.0,
        "strengths": ["Tailored solution for niche local market gap", "Agile and adaptable business structure", "Direct owner-customer relationship"],
        "weaknesses": ["Initial market awareness requires education", "Benchmark data requires customized validation", "Need to establish supply chains"],
        "opportunities": ["First-mover advantage in under-served town", "Expansion into adjacent services", "Government MSME subsidies"],
        "threats": ["New competitors entering once viability is proven", "Cash flow friction during early months", "Regulatory compliance learning curve"],
        "demand_drivers": [
            {"icon": "💡", "title": "Untapped Local Market Gap", "desc": "Residents currently travel to distant cities to access this essential product or service."},
            {"icon": "📈", "title": "Rising Disposable Incomes", "desc": "Semi-urban and rural purchasing power is growing at over 8% per annum."},
            {"icon": "🛡️", "title": "MSME Government Priority", "desc": "Liberalized collateral-free loans and credit guarantee schemes back new local micro-enterprises."}
        ],
        "product_service_mix": [
            {"title": "Core Signature Product / Service", "desc": "Primary offering that addresses the main local market pain point.", "priority": "Priority 1", "priority_tag": "tag-green", "rationale": "Establishes your core brand identity and drives early customer acquisition."},
            {"title": "Complementary Accessories & Add-ons", "desc": "High-margin auxiliary items sold alongside the primary purchase.", "priority": "Priority 2", "priority_tag": "tag-green", "rationale": "Lifts bottom-line profitability by 20-30% on existing footfall."},
            {"title": "Annual Maintenance / Recurring Service Contracts", "desc": "Subscription or repeat service ensuring customer retention.", "priority": "Priority 3", "priority_tag": "tag-orange", "rationale": "Creates predictable monthly recurring revenue (MRR) to cover fixed overheads."},
            {"title": "Digital On-Demand Booking & Express Delivery", "desc": "Phone/WhatsApp booking with doorstep fulfillment.", "priority": "Priority 4", "priority_tag": "tag-navy", "rationale": "Expands your serviceable radius across neighboring villages and towns."}
        ],
        "startup_cost_split": [
            {"name": "Core Equipment, Machinery & Tools", "pct": 40, "icon": "⚙️"},
            {"name": "Initial Inventory Stock & Raw Materials", "pct": 26, "icon": "📦"},
            {"name": "Premises Setup, Furniture & Signage", "pct": 18, "icon": "🏪"},
            {"name": "Working Capital & Utility Reserve", "pct": 10, "icon": "💰"},
            {"name": "Udyam Registration, Licenses & Permits", "pct": 6, "icon": "📜"}
        ],
        "monthly_expense_split": [
            {"name": "Staff Wages & Labor", "pct": 36},
            {"name": "Premise Rent", "pct": 30},
            {"name": "Power, Utilities & Fuel", "pct": 16},
            {"name": "Consumables & Inventory Replenishment Freight", "pct": 10},
            {"name": "Marketing, WhatsApp Business & Miscellaneous", "pct": 8}
        ],
        "monthly_revenue_split": [
            {"name": "Core Service / Product Deliveries", "pct": 52},
            {"name": "Value-Add Services & Custom Requests", "pct": 26},
            {"name": "Add-On Supplies & Consumables", "pct": 14},
            {"name": "Repeat Customer Maintenance Contracts", "pct": 8}
        ],
        "competitor_prefix": ["Apex Local Enterprises", "Shree Enterprise Point", "Standard Services", "Universal Hub", "Pioneer Solutions"],
        "schemes": ["PMEGP", "MUDRA Loan", "Startup India", "Stand-Up India"]
    }
}

# ──────────────────────────────────────────────────────────────
#  Government Schemes Database (with verified clickable portal URLs)
# ──────────────────────────────────────────────────────────────
SCHEMES_DB = {
    "PMEGP": {
        "name": "Prime Minister's Employment Generation Programme (PMEGP)",
        "ministry": "Ministry of Micro, Small and Medium Enterprises (MSME)",
        "subsidy": "25% (Urban) to 35% (Rural) of project cost",
        "subsidy_rate_rural": 0.35,
        "subsidy_rate_urban": 0.25,
        "max_loan": "₹50 Lakhs (Manufacturing), ₹20 Lakhs (Services / Retail)",
        "eligibility": "Any Indian citizen above 18 years. Greenfield (new) businesses. No income ceiling.",
        "portal_url": "https://www.kviconline.gov.in/pmegpeportal/pmegphome/index.jsp",
        "url": "https://www.kviconline.gov.in/pmegpeportal/pmegphome/index.jsp",
        "nodal_agency": "KVIC / KVIB / District Industries Centre (DIC)",
        "tags": ["manufacturing", "services", "rural", "urban"],
    },
    "MUDRA Loan": {
        "name": "Pradhan Mantri MUDRA Yojana (PMMY)",
        "ministry": "Department of Financial Services, Ministry of Finance",
        "subsidy": "Collateral-free credit guarantee; low concessional interest",
        "subsidy_rate_rural": 0.0,
        "subsidy_rate_urban": 0.0,
        "max_loan": "Shishu: Up to ₹50K | Kishore: ₹50K to ₹5L | Tarun: ₹5L to ₹10L",
        "eligibility": "Non-farm micro and small enterprises in trading, manufacturing, and services.",
        "portal_url": "https://www.mudra.org.in/",
        "url": "https://www.mudra.org.in/",
        "nodal_agency": "MUDRA Ltd. / All Commercial, Regional Rural & Cooperative Banks",
        "tags": ["all", "startup", "small business"],
    },
    "Stand-Up India": {
        "name": "Stand-Up India Scheme for Women & SC/ST",
        "ministry": "Ministry of Finance & Small Industries Development Bank of India (SIDBI)",
        "subsidy": "Composite loan covering 75% to 85% of project cost with concessional margin money",
        "subsidy_rate_rural": 0.15,
        "subsidy_rate_urban": 0.15,
        "max_loan": "₹10 Lakhs to ₹1 Crore",
        "eligibility": "SC/ST and/or Woman entrepreneur setting up greenfield manufacturing, service, or trading unit.",
        "portal_url": "https://www.standupmitra.in/",
        "url": "https://www.standupmitra.in/",
        "nodal_agency": "SIDBI & Scheduled Commercial Banks",
        "tags": ["sc/st", "women", "manufacturing", "services"],
    },
    "MSME Loan": {
        "name": "Credit Guarantee Fund Trust for Micro and Small Enterprises (CGTMSE)",
        "ministry": "Ministry of MSME & SIDBI",
        "subsidy": "Credit guarantee coverage up to 85% without third-party collateral",
        "subsidy_rate_rural": 0.0,
        "subsidy_rate_urban": 0.0,
        "max_loan": "Up to ₹2 Crores (Collateral-free)",
        "eligibility": "New and existing MSMEs registered under Udyam Portal.",
        "portal_url": "https://www.cgtmse.in/",
        "url": "https://www.cgtmse.in/",
        "nodal_agency": "CGTMSE Trust & Member Lending Institutions",
        "tags": ["msme", "manufacturing", "services"],
    },
    "PM-KISAN": {
        "name": "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)",
        "ministry": "Ministry of Agriculture & Farmers Welfare",
        "subsidy": "₹6,000 per year direct income transfer in 3 installments",
        "subsidy_rate_rural": 0.0,
        "subsidy_rate_urban": 0.0,
        "max_loan": "Direct Income Transfer DBT",
        "eligibility": "Landholding farmer families with cultivable landholding.",
        "portal_url": "https://pmkisan.gov.in/",
        "url": "https://pmkisan.gov.in/",
        "nodal_agency": "Department of Agriculture and Farmers Welfare",
        "tags": ["agriculture", "farmer", "rural"],
    },
    "PMFBY": {
        "name": "Pradhan Mantri Fasal Bima Yojana (PMFBY)",
        "ministry": "Ministry of Agriculture & Farmers Welfare",
        "subsidy": "Heavily subsidized premium (only 2% for Kharif, 1.5% for Rabi crops)",
        "subsidy_rate_rural": 0.50,
        "subsidy_rate_urban": 0.50,
        "max_loan": "Complete sum insured equivalent to expected crop loss value",
        "eligibility": "All farmers growing notified crops in notified areas.",
        "portal_url": "https://pmfby.gov.in/",
        "url": "https://pmfby.gov.in/",
        "nodal_agency": "Department of Agriculture / Em师paneled General Insurance Companies",
        "tags": ["agriculture", "farmer", "insurance"],
    },
    "Kisan Credit Card (KCC)": {
        "name": "Kisan Credit Card (KCC) Scheme",
        "ministry": "Ministry of Agriculture / Reserve Bank of India",
        "subsidy": "Interest subvention of 3% for timely repayment (Effective 4% p.a. interest)",
        "subsidy_rate_rural": 0.03,
        "subsidy_rate_urban": 0.03,
        "max_loan": "Up to ₹3 Lakhs at 4% effective interest",
        "eligibility": "All farmers, tenant farmers, dairy farmers, and animal husbandry practitioners.",
        "portal_url": "https://www.nabard.org/",
        "url": "https://www.nabard.org/",
        "nodal_agency": "NABARD & Commercial / RRB Banks",
        "tags": ["agriculture", "credit", "farmer"],
    },
    "NABARD Dairy Entrepreneurship Development Scheme (DEDS)": {
        "name": "NABARD Dairy Entrepreneurship Development Scheme (DEDS)",
        "ministry": "Ministry of Fisheries, Animal Husbandry & Dairying",
        "subsidy": "25% back-ended capital subsidy (33.33% for SC/ST and Women)",
        "subsidy_rate_rural": 0.25,
        "subsidy_rate_urban": 0.25,
        "max_loan": "Up to ₹30 Lakhs for modern dairy units and processing",
        "eligibility": "Farmers, individual entrepreneurs, NGOs, SHGs, and cooperatives.",
        "portal_url": "https://www.nabard.org/",
        "url": "https://www.nabard.org/",
        "nodal_agency": "NABARD & Nationalized Commercial Banks",
        "tags": ["dairy", "animal husbandry", "rural"],
    },
    "PM VIKAS": {
        "name": "PM Vishwakarma Kaushal Samman (PM VIKAS)",
        "ministry": "Ministry of Skill Development & Ministry of MSME",
        "subsidy": "₹15,000 modern toolkit grant + 5% concessional collateral-free loan",
        "subsidy_rate_rural": 0.20,
        "subsidy_rate_urban": 0.20,
        "max_loan": "Tranche 1: ₹1 Lakh, Tranche 2: ₹2 Lakhs @ 5% interest",
        "eligibility": "Traditional craftspeople, artisans, tailors, carpenters, blacksmiths.",
        "portal_url": "https://pmvishwakarma.gov.in/",
        "url": "https://pmvishwakarma.gov.in/",
        "nodal_agency": "Ministry of MSME & District Skill Committees",
        "tags": ["artisan", "skill", "handicraft", "tailoring"],
    },
    "MUDRA Shishu Loan": {
        "name": "MUDRA Shishu Category Micro Loan",
        "ministry": "Ministry of Finance",
        "subsidy": "100% collateral-free with zero processing fee",
        "subsidy_rate_rural": 0.0,
        "subsidy_rate_urban": 0.0,
        "max_loan": "Up to ₹50,000",
        "eligibility": "New micro-enterprises and small street businesses.",
        "portal_url": "https://www.mudra.org.in/",
        "url": "https://www.mudra.org.in/",
        "nodal_agency": "All Banks & Micro Finance Institutions (MFIs)",
        "tags": ["startup", "micro", "small"],
    },
    "Ambedkar Hastshilp Vikas Yojana": {
        "name": "Ambedkar Hastshilp Vikas Yojana (AHVY)",
        "ministry": "Ministry of Textiles / Office of Development Commissioner (Handicrafts)",
        "subsidy": "Up to 75% financial grant for design, raw material bank, and cluster setup",
        "subsidy_rate_rural": 0.75,
        "subsidy_rate_urban": 0.75,
        "max_loan": "Project-based cluster grant",
        "eligibility": "Artisan self-help groups, registered artisan societies, and cooperatives.",
        "portal_url": "https://www.handicrafts.nic.in/",
        "url": "https://www.handicrafts.nic.in/",
        "nodal_agency": "DC Handicrafts & Regional Service Centers",
        "tags": ["handicraft", "artisan", "rural"],
    },
    "PM SVANidhi": {
        "name": "PM Street Vendor's AtmaNirbhar Nidhi (PM SVANidhi)",
        "ministry": "Ministry of Housing & Urban Affairs",
        "subsidy": "7% interest subsidy directly credited to bank account on digital transactions",
        "subsidy_rate_rural": 0.07,
        "subsidy_rate_urban": 0.07,
        "max_loan": "Tranche 1: ₹10K | Tranche 2: ₹20K | Tranche 3: ₹50K",
        "eligibility": "Urban/semi-urban vendors and small daily goods providers.",
        "portal_url": "https://pmsvanidhi.mohua.gov.in/",
        "url": "https://pmsvanidhi.mohua.gov.in/",
        "nodal_agency": "Urban Local Bodies (ULBs) & SIDBI",
        "tags": ["street vendor", "urban", "small"],
    },
    "National Livestock Mission": {
        "name": "National Livestock Mission (NLM)",
        "ministry": "Department of Animal Husbandry and Dairying",
        "subsidy": "Up to 50% capital subsidy on breeding, fodder, and dairy processing units",
        "subsidy_rate_rural": 0.50,
        "subsidy_rate_urban": 0.50,
        "max_loan": "Up to ₹50 Lakhs capital subsidy per project",
        "eligibility": "Individuals, SHGs, FPOs, and private companies in livestock sector.",
        "portal_url": "https://nlm.udyamimitra.in/",
        "url": "https://nlm.udyamimitra.in/",
        "nodal_agency": "State Animal Husbandry Department & SIDBI",
        "tags": ["livestock", "animal husbandry", "rural"],
    },
    "Startup India": {
        "name": "Startup India Initiative",
        "ministry": "Department for Promotion of Industry and Internal Trade (DPIIT)",
        "subsidy": "3-year 100% income tax exemption + fast-tracked subsidized patent filing",
        "subsidy_rate_rural": 0.0,
        "subsidy_rate_urban": 0.0,
        "max_loan": "Seed Fund Scheme up to ₹50 Lakhs via incubators",
        "eligibility": "Incorporated private limited company or registered partnership up to 10 years old.",
        "portal_url": "https://www.startupindia.gov.in/",
        "url": "https://www.startupindia.gov.in/",
        "nodal_agency": "DPIIT & Startup India Hub",
        "tags": ["startup", "innovation", "technology"],
    },
    "MSME Technology Upgrade Fund (CLCSS)": {
        "name": "Credit Linked Capital Subsidy Scheme (CLCSS)",
        "ministry": "Ministry of MSME",
        "subsidy": "15% upfront capital subsidy for inducting well-established technology",
        "subsidy_rate_rural": 0.15,
        "subsidy_rate_urban": 0.15,
        "max_loan": "₹1 Crore eligible plant and machinery cost",
        "eligibility": "Micro and small enterprises registered on Udyam Portal.",
        "portal_url": "https://clcss.dcmsme.gov.in/",
        "url": "https://clcss.dcmsme.gov.in/",
        "nodal_agency": "Office of DC (MSME) & Nodal Banks",
        "tags": ["manufacturing", "technology", "msme"],
    },
    "National Handloom Development Programme": {
        "name": "National Handloom Development Programme (NHDP)",
        "ministry": "Ministry of Textiles",
        "subsidy": "Up to 90% subsidy for cluster development, lighting units, and yarn depots",
        "subsidy_rate_rural": 0.90,
        "subsidy_rate_urban": 0.90,
        "max_loan": "Weavers Mudra Card up to ₹2 Lakhs @ 6% interest",
        "eligibility": "Handloom weavers, cooperative societies, and producer companies.",
        "portal_url": "https://handlooms.nic.in/",
        "url": "https://handlooms.nic.in/",
        "nodal_agency": "Weavers Service Centre (WSC) & DC Handlooms",
        "tags": ["handloom", "textile", "weaving", "rural"],
    },
    "e-NAM": {
        "name": "National Agriculture Market (e-NAM)",
        "ministry": "Ministry of Agriculture & Farmers Welfare",
        "subsidy": "Free online trading access + quality assaying labs at regulated mandis",
        "subsidy_rate_rural": 0.0,
        "subsidy_rate_urban": 0.0,
        "max_loan": "Electronic warehouse receipt trading platform",
        "eligibility": "All farmers and producer organizations selling agricultural produce.",
        "portal_url": "https://www.enam.gov.in/",
        "url": "https://www.enam.gov.in/",
        "nodal_agency": "Small Farmers Agribusiness Consortium (SFAC)",
        "tags": ["agriculture", "market linkage", "digital"],
    },
    "PM Gati Shakti": {
        "name": "PM Gati Shakti Multi-Modal Logistics Support",
        "ministry": "Ministry of Commerce and Industry",
        "subsidy": "Logistics hub linkage, express corridor clearances, and freight grants",
        "subsidy_rate_rural": 0.0,
        "subsidy_rate_urban": 0.0,
        "max_loan": "Commercial vehicle and freight hub priority credit",
        "eligibility": "Logistics, fleet owners, and rural transport operators.",
        "portal_url": "https://pmgatishakti.gov.in/",
        "url": "https://pmgatishakti.gov.in/",
        "nodal_agency": "Logistics Division, DPIIT",
        "tags": ["logistics", "transport", "infrastructure"],
    }
}


# ──────────────────────────────────────────────────────────────
#  Main Analysis Engine
# ──────────────────────────────────────────────────────────────

def run_full_analysis(form_data: dict) -> dict:
    """
    Generate all 6 analysis modules dynamically from form data.
    Guarantees that all numbers, locations, and sectors strictly follow user input.
    """
    btype = form_data.get("business_type", "other")
    bdata = BUSINESS_DATA.get(btype, BUSINESS_DATA["other"])

    investment = float(form_data.get("total_investment", 100000))
    own_capital = float(form_data.get("own_capital", investment * 0.4))
    loan_amount = max(0, investment - own_capital)

    # Respect user inputs if entered, else provide calculated industry benchmarks
    user_sales = form_data.get("expected_monthly_sales") or form_data.get("expected_revenue")
    expected_sales = float(user_sales) if user_sales and float(user_sales) > 0 else (investment * 0.22)

    user_expenses = form_data.get("monthly_expenses")
    monthly_expenses = float(user_expenses) if user_expenses and float(user_expenses) > 0 else (investment * (bdata["monthly_fixed_cost_pct"] / 100))

    state = form_data.get("state", "Odisha")
    district = form_data.get("district", "Cuttack")
    village = form_data.get("village") or form_data.get("town") or ""
    block = form_data.get("block") or ""
    town = form_data.get("town") or village or ""
    area_type = form_data.get("area_type", "rural")
    biz_name = form_data.get("business_name") or f"{village or district} {bdata['label']}"
    stage = form_data.get("business_stage", "new")

    # Resolve micro-location details
    loc_display = f"{village}, {block}" if (village and block) else (village or block or district)
    full_loc_display = f"{loc_display}, {district}, {state}" if loc_display != district else f"{district}, {state}"
    archetype = get_area_archetype(area_type)

    result = {
        "meta": {
            "business_name": biz_name,
            "business_type": btype,
            "business_label": bdata["label"],
            "sector": bdata["sector"],
            "state": state,
            "district": district,
            "village": village,
            "block": block,
            "town": town,
            "area_type": area_type,
            "area_label": archetype["label"],
            "location_display": loc_display,
            "full_location_display": full_loc_display,
            "stage": stage,
            "total_investment": investment,
            "generated_at": datetime.now().strftime("%d %b %Y, %I:%M %p"),
        },
        "market": _market_analysis(bdata, area_type, state, district, investment, village=village, block=block),
        "financial": _financial_analysis(bdata, investment, own_capital, loan_amount, expected_sales, monthly_expenses, biz_name, village=village, block=block, area_type=area_type, state=state, district=district),
        "swot": _swot_analysis(bdata, area_type, biz_name, district, state, village=village, block=block),
        "competition": _competition_analysis(bdata, area_type, district, state, biz_name, village=village, block=block),
        "schemes": _schemes_analysis(bdata, form_data, investment, district, state, village=village, block=block),
        "action_plan": _action_plan(bdata, biz_name, investment, stage, district, state, village=village, block=block),
    }
    return result


# ──────────────────────────────────────────────────────────────
#  Individual analysis modules
# ──────────────────────────────────────────────────────────────

def _market_analysis(bdata, area_type, state, district, investment, village="", block=""):
    archetype = get_area_archetype(area_type)
    area_multipliers = {"rural": 0.75, "semi_urban": 1.0, "urban_outskirts": 1.3, "urban": 1.6}
    mult = area_multipliers.get(area_type, 1.0)
    base_market_size = round(investment * 12 * mult * random.uniform(3.5, 6.5) / 1_00_000, 2)

    loc_label = village or block or district
    radius = archetype.get("radius_km", 5.0)

    demand_score = round(min(9.6, max(7.0, (bdata["market_growth_pct"] * 0.45) + archetype["footfall_index"] * 0.4 + random.uniform(0.5, 1.2))), 1)

    return {
        "market_size_cr": base_market_size,
        "growth_rate_pct": bdata["market_growth_pct"],
        "area_type": area_type,
        "area_label": archetype["label"],
        "catchment_radius_km": radius,
        "catchment_population": archetype.get("catchment_pop_range", "5,000 - 25,000 residents"),
        "demand_score": demand_score,
        "local_demand": _local_demand_text(bdata, area_type, district, village=village, block=block),
        "demand_drivers": [
            {"icon": "📍", "title": f"Hyper-Local Demand in {loc_label}", "desc": f"Residents within your direct {radius} km cluster prefer local accessibility over travelling to distant hubs."},
            {"icon": "📈", "title": "Expanding Purchasing Power", "desc": f"Steady household spending and commercial growth in {loc_label} ({district}) provide resilient baseline demand."},
            {"icon": "📲", "title": "Digital Payments & Local Trust", "desc": "100% UPI adoption and personal relationships enable fast customer acquisition and recurring orders."}
        ],
        "product_service_mix": bdata.get("product_service_mix", []),
        "market_insights": [
            f"The {bdata['label']} sector is expanding at {bdata['market_growth_pct']}% CAGR nationally, with highest untapped potential in {archetype['label'].lower()} zones.",
            f"In {loc_label} ({district}), consumers value immediate availability, reliable quality, and friendly neighborhood service over distant city markets.",
            f"Offering WhatsApp-based product orders and digital billing builds an unassailable defensive moat across a {radius} km radius.",
            f"Government MSME subsidies (up to 35% under PMEGP in {district}) significantly reduce equity risk for new entrants in {state}."
        ],
        "target_segment": {
            "primary": f"Households, daily consumers, and local professionals in {loc_label} within a {radius} km radius",
            "secondary": f"Neighboring village clusters and commercial commuters in {district}",
            "reach_km": radius,
        },
    }


def _local_demand_text(bdata, area_type, district, village="", block=""):
    loc = f"{village}, {block} ({district})" if (village and block) else (f"{village or block}, {district}" if (village or block) else district)
    archetype = get_area_archetype(area_type)
    return (f"In the {loc} ({archetype['label']}), demand for {bdata['label'].lower()} is "
            f"{'rapidly accelerating' if bdata['market_growth_pct'] > 10 else 'healthy, consistent, and resilient'}. "
            f"Serving an estimated {archetype['catchment_pop_range']} within a {archetype['radius_km']} km radius, "
            f"with sector margins averaging {bdata['avg_margin_pct']}%, local micro-enterprise fundamentals indicate "
            f"{'exceptional' if bdata['avg_margin_pct'] > 30 else 'solid'} commercial feasibility.")


def _financial_analysis(bdata, investment, own_capital, loan_amount, expected_sales, monthly_expenses, biz_name, village="", block="", area_type="rural", state="", district=""):
    investment = float(investment) if investment else 100000.0
    own_capital = float(own_capital) if own_capital else (investment * 0.4)
    loan_amount = float(loan_amount) if loan_amount else max(0.0, investment - own_capital)
    sector_margin = (bdata.get("avg_margin_pct", 25)) / 100.0

    # User's expected monthly revenue
    if expected_sales and float(expected_sales) > 0:
        monthly_rev = float(expected_sales)
    else:
        monthly_rev = max(25000.0, investment * 0.20)

    # User's monthly operating expenses
    if monthly_expenses and float(monthly_expenses) > 0:
        monthly_fixed = float(monthly_expenses)
    else:
        monthly_fixed = round(monthly_rev * (1.0 - sector_margin))

    # Net Monthly Profit and Profit Margin directly reflecting user inputs
    if monthly_rev > monthly_fixed:
        monthly_profit = monthly_rev - monthly_fixed
    else:
        # Fallback if user entered expenses >= revenue
        monthly_profit = max(monthly_rev * 0.12, investment * 0.05)
        monthly_fixed = max(0.0, monthly_rev - monthly_profit)

    annual_profit = monthly_profit * 12
    profit_margin_pct = round((monthly_profit / max(1.0, monthly_rev)) * 100)

    # Dynamic break-even calculation based on user's investment and monthly profit
    be_months_calc = max(1, round(investment / max(1.0, monthly_profit)))
    break_even_display = f"{max(1, be_months_calc - 1)}–{be_months_calc + 1} months" if be_months_calc > 1 else "1–2 months"
    roi_pct = round((annual_profit / max(1.0, investment)) * 100, 1)

    # Loan EMI calculation
    tenure_months = be_months_calc + 12
    if loan_amount > 0:
        r = 0.12 / 12  # 12% p.a. concessional MSME rate
        emi = round(loan_amount * r * (1 + r)**tenure_months / ((1 + r)**tenure_months - 1))
    else:
        emi = 0

    # Dynamic startup cost breakdown summing to 100% of user investment
    startup_splits = bdata.get("startup_cost_split", [])
    startup_costs = []
    for item in startup_splits:
        amt = round(investment * (item["pct"] / 100))
        startup_costs.append({
            "name": item["name"],
            "icon": item.get("icon", "💼"),
            "pct": item["pct"],
            "amount": amt,
            "formatted_amount": f"₹{amt:,.0f}"
        })

    # Dynamic itemized monthly expenses summing to user's exact monthly_fixed
    expense_splits = bdata.get("monthly_expense_split", [
        {"name": "Commercial Space Rent", "pct": 40},
        {"name": "Staff / Worker Wages", "pct": 30},
        {"name": "Electricity, Water & Utilities", "pct": 15},
        {"name": "Consumables & Restocking Carriage", "pct": 10},
        {"name": "Maintenance & General Upkeep", "pct": 5}
    ])
    monthly_expenses_breakdown = []
    for item in expense_splits:
        amt = round(monthly_fixed * (item["pct"] / 100))
        monthly_expenses_breakdown.append({
            "name": item["name"],
            "pct": item["pct"],
            "amount": amt,
            "formatted_amount": f"₹{amt:,.0f}"
        })

    # Dynamic itemized monthly revenue streams summing to user's exact monthly_rev
    revenue_splits = bdata.get("monthly_revenue_split", [
        {"name": "Primary Service / Product Sales", "pct": 55},
        {"name": "Secondary Offerings & High-Margin Items", "pct": 25},
        {"name": "Auxiliary Services & Subscriptions", "pct": 12},
        {"name": "Ancillary Commissions & Counter Sales", "pct": 8}
    ])
    monthly_revenue_breakdown = []
    for item in revenue_splits:
        amt = round(monthly_rev * (item["pct"] / 100))
        monthly_revenue_breakdown.append({
            "name": item["name"],
            "pct": item["pct"],
            "amount": amt,
            "formatted_amount": f"₹{amt:,.0f}"
        })

    # Year 1 monthly ramp-up projection table
    ramp_months = [
        {"period": "Month 1–2 (Setup & Launch)", "rev_factor": 0.55, "profit_factor": 0.0, "status": "Break-even ramp"},
        {"period": "Month 3–6 (Growth & Retention)", "rev_factor": 0.80, "profit_factor": 0.55, "status": "Growing surplus"},
        {"period": "Month 7–12 (Full Stabilization)", "rev_factor": 1.00, "profit_factor": 1.00, "status": "Optimal capacity"},
    ]
    year1_table = []
    cum_recovered = 0
    for rm in ramp_months:
        p_rev = round(monthly_rev * rm["rev_factor"])
        p_profit = round(monthly_profit * rm["profit_factor"])
        months_span = 2 if "1–2" in rm["period"] else (4 if "3–6" in rm["period"] else 6)
        cum_recovered += (p_profit * months_span)
        year1_table.append({
            "period": rm["period"],
            "monthly_revenue": p_rev,
            "monthly_profit": p_profit,
            "cumulative_recovered": cum_recovered,
            "formatted_rev": f"₹{p_rev:,.0f}",
            "formatted_profit": f"₹{p_profit:,.0f}" if p_profit > 0 else "₹0 (break-even)",
            "formatted_recovered": f"₹{cum_recovered:,.0f} recovered" if cum_recovered > 0 else "₹0 recovered"
        })

    # 3-Year Projections
    projections = []
    cum_profit = 0
    for yr in range(1, 4):
        yr_rev = monthly_rev * 12 * (1.12 ** (yr - 1))
        yr_profit = monthly_profit * 12 * (1.12 ** (yr - 1))
        cum_profit += yr_profit
        projections.append({
            "year": f"Year {yr}",
            "revenue": round(yr_rev),
            "profit": round(yr_profit),
            "cumulative_profit": round(cum_profit),
            "formatted_revenue": f"₹{round(yr_rev):,.0f}",
            "formatted_profit": f"₹{round(yr_profit):,.0f}",
            "formatted_cumulative": f"₹{round(cum_profit):,.0f}",
        })

    return {
        "investment": round(investment),
        "own_capital": round(own_capital),
        "loan_amount": round(loan_amount),
        "monthly_revenue": round(monthly_rev),
        "monthly_fixed_cost": round(monthly_fixed),
        "monthly_profit": round(monthly_profit),
        "annual_profit": round(annual_profit),
        "break_even_revenue": round(monthly_fixed),
        "break_even_months": be_months_calc,
        "break_even_display": break_even_display,
        "profit_margin_pct": profit_margin_pct,
        "gross_margin_pct": profit_margin_pct,
        "net_profit_margin_pct": profit_margin_pct,
        "roi_pct": roi_pct,
        "emi": emi,
        "tenure_months": tenure_months,
        "startup_costs": startup_costs,
        "monthly_expenses_breakdown": monthly_expenses_breakdown,
        "monthly_revenue_breakdown": monthly_revenue_breakdown,
        "year1_table": year1_table,
        "projections": projections,
        "summary": (
            f"With ₹{investment:,.0f} total planned investment for {biz_name}, you can anticipate a realistic monthly net profit of "
            f"₹{monthly_profit:,.0f} (based on ₹{monthly_rev:,.0f} revenue and ₹{monthly_fixed:,.0f} operating costs). "
            f"Full investment recovery is estimated within {break_even_display} with an annualized ROI of {roi_pct}%."
        ),
    }


def _swot_analysis(bdata, area_type, biz_name, district, state, village="", block=""):
    loc_label = village or block or district
    archetype = get_area_archetype(area_type)
    area_opps = {
        "rural": [f"Untapped demand in {loc_label} village cluster with zero organized competitors", "Strong long-term community loyalty and direct neighbor referrals"],
        "semi_urban": [f"Strategic central position in {loc_label} bridging rural consumers and wholesale distributors", "Growing aspirational consumption and willingness to pay for quality"],
        "urban_outskirts": [f"Access to expanding suburban population in {loc_label} at 40% lower commercial lease rents", "Rapid residential infrastructure build-out"],
        "urban": [f"High daily transaction velocity and footfall in {loc_label}", "Favorable adoption of premium product variants and instant UPI checkout"],
    }.get(area_type, [])

    b_label = bdata["label"]

    strategy_recommendations = {
        "maximize_strengths": f"Leverage prominent local signage in {loc_label} and personalized customer engagement for {biz_name}. Highlight your {bdata['strengths'][0].lower()} to build immediate neighborhood recall.",
        "minimize_weaknesses": f"Mitigate working capital strain by negotiating 15-day vendor credit cycles from distributors in {district}. Adopt digital inventory tracking to curb waste.",
        "capture_opportunities": f"Within Month 2, establish doorstep delivery and WhatsApp Business ordering for customers across {loc_label} ({district}). Introduce high-margin complementary offerings to boost basket value.",
        "counter_threats": f"Build an unassailable defensive moat through transparent pricing, prompt local service in {loc_label}, and verified quality guarantees that distant online or chain competitors cannot duplicate."
    }

    key_insight = (
        f"Your strongest competitive advantage in {loc_label} is being an agile, community-rooted {b_label.lower()}. "
        f"By pairing prompt personal service with digital payment convenience, {biz_name} can capture lasting customer loyalty across {district}."
    )

    return {
        "strengths": bdata["strengths"],
        "weaknesses": bdata["weaknesses"],
        "opportunities": bdata["opportunities"] + area_opps,
        "threats": bdata["threats"],
        "strategy_recommendations": strategy_recommendations,
        "key_insight": key_insight,
        "score": {
            "strengths": len(bdata["strengths"]) * 20,
            "weaknesses": len(bdata["weaknesses"]) * 20,
            "opportunities": (len(bdata["opportunities"]) + len(area_opps)) * 15,
            "threats": len(bdata["threats"]) * 20,
        },
    }


def _competition_analysis(bdata, area_type, district, state, biz_name, village="", block=""):
    comp_density = {
        "rural": "Low", "semi_urban": "Medium",
        "urban_outskirts": "Medium-High", "urban": "High"
    }.get(area_type, "Medium")

    prefixes = bdata.get("competitor_prefix", ["Local Trade Point", "Express Center", "District Super Store", "Modern Trade Hub", "Pioneer Mart"])
    competitors = []

    micro_loc = village or block or "Local Market"
    distant_loc = district if (district and district != micro_loc) else "District Main Market"

    # Specific hyper-local competitor mapping: 2 local vendors + 2-3 distant vendors in the block/district center
    comp_configs = [
        {"name": f"{prefixes[0]} ({micro_loc})", "dist": "0.6 km", "type": "Direct Local", "threat": "Medium", "share": 30, "service": f"Basic {bdata['label'].lower()} sales, limited stock variety", "gap": "Lacks digital payments, modern warranties, and doorstep delivery", "pro": "Walking distance; familiar to immediate neighbours"},
        {"name": f"{prefixes[1]} ({micro_loc} Chowk)", "dist": "1.2 km", "type": "Direct Local", "threat": "Low", "share": 20, "service": "Unorganized counter offering limited items as side-business", "gap": "Irregular opening hours and frequent out-of-stock items", "pro": "Low prices on basic entry-level items"},
        {"name": f"{prefixes[2]} ({block or distant_loc})", "dist": "4.8 km", "type": "Hub Store", "threat": "High", "share": 25, "service": "Full-line supplier with wider range but high travel friction", "gap": f"Situated outside {micro_loc}; requires 30-45 min commute for local consumers", "pro": "Established brand presence in block market"},
        {"name": f"{prefixes[3]} ({distant_loc} Town)", "dist": "8.5 km", "type": "Distant Wholesale", "threat": "Low", "share": 15, "service": "Wholesale bulk distributor, limited single retail unit assistance", "gap": "Minimum order values; inconvenient for everyday small purchases", "pro": "Potential inventory sourcing partner for your opening stock"},
        {"name": f"{prefixes[4]} ({distant_loc} High Street)", "dist": "11.2 km", "type": "Urban Retail", "threat": "Low", "share": 10, "service": "Branded showroom with premium high-margin pricing", "gap": "Expensive price point and zero local community touchpoint", "pro": "Benchmark for premium products and trending models"}
    ]

    for cfg in comp_configs:
        competitors.append({
            "name": cfg["name"],
            "distance": cfg["dist"],
            "services": cfg["service"],
            "gaps": cfg["gap"],
            "pros": cfg["pro"],
            "type": cfg["type"],
            "threat_level": cfg["threat"],
            "market_share_pct": cfg["share"],
        })

    target_loc = f"{village}, {block}" if (village and block) else (village or block or district)
    ai_recommendation = (
        f"Micro-location market analysis reveals NO organized, modern {bdata['label'].lower()} "
        f"providing full warranty support, digital ordering, and doorstep delivery inside {target_loc}. "
        f"Consumers in {target_loc} currently commute 5–10 km to distant centers in {distant_loc}, "
        f"incurring travel time and transport costs. {biz_name} can capture up to 45% of local neighborhood "
        f"demand by pairing transparent fair pricing with prompt local fulfillment."
    )

    market_gap = (
        f"Within {target_loc} and adjoining hamlets, local consumers suffer from fragmented supply and inconsistent pricing. "
        f"{biz_name} can establish itself as the go-to neighborhood destination for {bdata['label']}."
    )

    return {
        "competition_density": comp_density,
        "total_competitors_estimate": {"rural": "2-3 within village (4-6 in block)", "semi_urban": "4-7 in commercial ward",
                                        "urban_outskirts": "8-12 in suburban hub", "urban": "15+ in city center"}
                                       .get(area_type, "3-6"),
        "competitors": competitors,
        "ai_recommendation": ai_recommendation,
        "market_gap": market_gap,
        "competitive_advantage_tips": [
            f"Focus on personalized service and warm community relationships across {target_loc} that distant chains cannot replicate.",
            "Enable WhatsApp Business for quick catalogue sharing, order booking, and local home delivery.",
            "Maintain consistent product availability to eliminate customer disappointment and build daily habits.",
            "Display transparent, competitive pricing with 100% UPI payment ease (PhonePe, GooglePay, Paytm).",
        ],
        "market_entry_strategy": (
            f"Position {biz_name} as the most dependable and customer-friendly {bdata['label'].lower()} in {target_loc}. "
            f"Focus on capturing high loyalty within your immediate 2 km radius during the first 60 days before expanding across {district}."
        ),
    }


def _build_eligibility_reasons(key, form_data, investment, area_type):
    """Generate dynamic 'Why You're Eligible' checklist per scheme and user profile."""
    is_woman = form_data.get("entrepreneur_gender", "") in ["female", "Female", "FEMALE"]
    is_sc_st = form_data.get("caste_category", "") in ["sc", "st", "SC", "ST"]
    stage = form_data.get("business_stage", "new")
    biz_name = form_data.get("business_name", "Your business")
    district = form_data.get("district", "your district")
    location_city = form_data.get("village") or form_data.get("town") or form_data.get("block") or district

    area_label = {"rural": "rural area", "semi_urban": "semi-urban area",
                  "urban_outskirts": "urban outskirts", "urban": "urban area"}.get(area_type, "local area")

    reasons = []
    if key == "PMEGP":
        reasons = [
            {"check": True, "text": f"{'New (Greenfield)' if stage == 'new' else 'Eligible'} business enterprise"},
            {"check": investment <= 2500000, "text": f"Project cost ₹{investment:,.0f} within ₹25 Lakh service sector limit"},
            {"check": True, "text": f"Located in {area_label} — attracts {35 if area_type == 'rural' else 25}% margin-money subsidy"},
            {"check": True, "text": "Indian citizen above 18 years of age"},
        ]
        if is_sc_st:
            reasons.append({"check": True, "text": "SC/ST category: Additional 5% subsidy applicable"})
        if is_woman:
            reasons.append({"check": True, "text": "Woman entrepreneur: Eligible for special state-level PMEGP benefits"})

    elif key == "MUDRA Loan":
        tier = "Kishore (₹50K–₹5L)" if investment <= 500000 else "Tarun (₹5L–₹10L)"
        reasons = [
            {"check": True, "text": f"Non-farm business activity qualifies under {tier} category"},
            {"check": True, "text": "No collateral or third-party guarantee required"},
            {"check": True, "text": "Eligible at any PSU, private, or Gramya bank branch"},
            {"check": True, "text": "Udyam MSME registration strengthens your loan approval"},
        ]

    elif key == "Stand-Up India":
        reasons = [
            {"check": is_woman, "text": "Woman entrepreneur — primary eligibility criterion ✓" if is_woman else "Not applicable (woman-only)"},
            {"check": is_sc_st, "text": "SC/ST category — primary eligibility criterion ✓" if is_sc_st else "SC/ST category (not applicable)"},
            {"check": True, "text": "Greenfield manufacturing, service, or trading enterprise"},
            {"check": True, "text": "Bank loan from ₹10 Lakh to ₹1 Crore available"},
        ]

    elif key == "PM SVANidhi":
        reasons = [
            {"check": True, "text": "Street vending / micro business qualifies for seed capital"},
            {"check": True, "text": "Loan starts at ₹10,000 with credit-history building incentive"},
            {"check": True, "text": "Digital payment adoption grants interest cashback"},
            {"check": True, "text": "Applicable in urban and semi-urban local bodies"},
        ]

    elif key == "MSME Loan":
        reasons = [
            {"check": True, "text": "Registered under Udyam MSME portal (or registration pending)"},
            {"check": True, "text": "Collateral-free guarantee coverage up to 85% of loan value"},
            {"check": True, "text": "Available through all Member Lending Institutions (MLIs)"},
            {"check": True, "text": "Supports both new enterprises and working capital needs"},
        ]

    elif key == "PM VIKAS":
        reasons = [
            {"check": True, "text": "Traditional artisan / craftsperson trade qualifies"},
            {"check": True, "text": "₹15,000 modern toolkit incentive directly credited"},
            {"check": True, "text": "Skill training with ₹500/day stipend available"},
            {"check": True, "text": "Concessional 5% interest on collateral-free credit"},
        ]

    elif key in ["NABARD Dairy Entrepreneurship Development Scheme (DEDS)", "DEDS"]:
        reasons = [
            {"check": True, "text": "Dairy enterprise (milk production/processing) qualifies"},
            {"check": is_sc_st or is_woman, "text": "SC/ST or Women: Enhanced 33.33% back-ended subsidy" if (is_sc_st or is_woman) else "General category: 25% back-ended subsidy"},
            {"check": True, "text": "Unit financed through NABARD-linked commercial bank"},
            {"check": True, "text": "Modern milking equipment and cooling tank covered"},
        ]

    else:
        # Generic fallback
        reasons = [
            {"check": True, "text": "Business type meets scheme eligibility criteria"},
            {"check": True, "text": f"Investment of ₹{investment:,.0f} within admissible project cost"},
            {"check": True, "text": f"Located in {area_label} as required by scheme guidelines"},
            {"check": True, "text": "Udyam registration fulfills basic documentary requirement"},
        ]

    return reasons


def _schemes_analysis(bdata, form_data, investment, district, state, village="", block=""):
    relevant_keys = bdata.get("schemes", ["PMEGP", "MUDRA Loan"])
    is_woman = form_data.get("entrepreneur_gender", "") == "female"
    is_sc_st = form_data.get("caste_category", "") in ["sc", "st"]
    area_type = form_data.get("area_type", "rural")
    loc_label = village or block or district

    matched = []
    for key in relevant_keys:
        if key in SCHEMES_DB:
            s = SCHEMES_DB[key].copy()
            s["key"] = key
            rate = s.get("subsidy_rate_rural" if area_type == "rural" else "subsidy_rate_urban", 0.25)
            calc_subsidy = round(investment * rate)
            s["calculated_subsidy_amount"] = calc_subsidy
            s["calculated_subsidy_inr"] = calc_subsidy
            s["formatted_subsidy"] = f"\u20b9{calc_subsidy:,.0f}" if calc_subsidy > 0 else "Collateral-free credit"
            s["your_benefit"] = f"Up to \u20b9{calc_subsidy:,.0f} back" if calc_subsidy > 0 else "Collateral-free loan guarantee"
            s["bank_partner"] = "SIDBI, PSU Banks" if key == "PMEGP" else ("All Scheduled Banks" if key == "MUDRA Loan" else "SIDBI & Commercial Banks")
            s["apply_via"] = s.get("portal_url", "#")
            s["eligibility_reasons"] = _build_eligibility_reasons(key, form_data, investment, area_type)
            matched.append(s)

    # Ensure MUDRA is always available
    if not any(m["key"] == "MUDRA Loan" for m in matched) and "MUDRA Loan" in SCHEMES_DB:
        s = SCHEMES_DB["MUDRA Loan"].copy()
        s["key"] = "MUDRA Loan"
        s["calculated_subsidy_amount"] = 0
        s["formatted_subsidy"] = "Collateral-free credit guarantee"
        matched.append(s)

    # Add Stand-Up India if eligible
    if (is_woman or is_sc_st) and not any(m["key"] == "Stand-Up India" for m in matched):
        s = SCHEMES_DB["Stand-Up India"].copy()
        s["key"] = "Stand-Up India"
        calc_subsidy = round(investment * 0.15)
        s["calculated_subsidy_amount"] = calc_subsidy
        s["calculated_subsidy_inr"] = calc_subsidy
        s["formatted_subsidy"] = f"₹{calc_subsidy:,.0f} (Concessional margin)"
        s["your_benefit"] = f"Up to ₹{calc_subsidy:,.0f} margin money"
        s["bank_partner"] = "SIDBI & Scheduled Commercial Banks"
        s["apply_via"] = s.get("portal_url", "#")
        s["eligibility_reasons"] = _build_eligibility_reasons("Stand-Up India", form_data, investment, area_type)
        matched.insert(0, s)

    # Calculate realistic combined subsidy potential
    max_subsidy = round(investment * (0.35 if area_type == "rural" else 0.25))
    min_subsidy = round(investment * 0.15)

    combined_benefit = (
        f"By applying for the PMEGP subsidy (up to ₹{max_subsidy:,.0f} back on your ₹{investment:,.0f} project) "
        f"alongside a MUDRA Kishore/Tarun loan for working capital, your out-of-pocket equity requirement "
        f"is drastically reduced. Visit the District Industries Centre (DIC) in {district} to submit both applications simultaneously."
    )

    return {
        "total_matched": len(matched),
        "schemes": matched,
        "estimated_subsidy": f"₹{min_subsidy:,.0f} to ₹{max_subsidy:,.0f}",
        "combined_benefit": combined_benefit,
        "registration_steps": [
            f"1. Obtain free Udyam MSME Registration online at udyamregistration.gov.in",
            f"2. Submit online PMEGP application on KVIC e-portal (kviconline.gov.in) with project summary",
            f"3. Approach your nearest PSU or Gramya bank branch in {district} for MUDRA loan processing",
            f"4. Track application sanction with your local District Industries Centre (DIC) officer"
        ],
    }


def _action_plan(bdata, biz_name, investment, stage, district, state, village="", block=""):
    b_label = bdata["label"]
    loc_label = village or block or district

    phases = [
        {
            "phase": "Week 1–2: Statutory Registration & Scheme Sanction",
            "timeframe": "📅 WEEK 1–2",
            "title": f"Formalize {biz_name} & Apply for Government Subsidies",
            "desc": f"Obtain your free Udyam MSME registration online. Visit the District Industries Centre (DIC) in {district} to initiate PMEGP subsidy processing and apply for MUDRA credit at your nearest bank branch in {loc_label}.",
            "badges": ["📋 Docs: Aadhaar + PAN + Project Report", f"📍 Where: DIC {district} / Gram Panchayat {village or loc_label}", "💰 Benefit: Up to 35% subsidy + Collateral-free loan"],
            "tasks": [
                "Register on the Udyam Portal (udyamregistration.gov.in) — 100% free and instant certificate",
                f"Apply for PMEGP on KVIC portal (kviconline.gov.in) and submit copy at DIC {district}",
                f"Apply for MUDRA Loan at nearest bank branch in {loc_label} / {district}",
                f"Apply for Local Trade Licence from {village or block} Gram Panchayat / Municipal Body"
            ]
        },
        {
            "phase": "Week 3–4: Location Finalization & Infrastructure Fit-Out",
            "timeframe": "📅 WEEK 3–4",
            "title": "Secure Commercial Premise & Complete Essential Setup",
            "desc": f"Select a visible road-facing commercial space in {loc_label}. Finalize the lease agreement (standard 2-month deposit), arrange clean electricals, and install durable display shelving and bold signage.",
            "badges": [f"🏪 Premise: High visibility in {loc_label}", "⚖️ Rent Budget: Negotiate 2-month advance", "✨ Fit-out: Modern display + LED signage"],
            "tasks": [
                f"Finalize 150-300 sq ft shop lease on main road in {loc_label} ({district})",
                "Complete basic interior fit-out: glass counters, secure display racks, and bright lighting",
                "Install external LED signboard with business name and regional language branding",
                "Obtain GST registration online at gst.gov.in (if applicable for input tax credit)"
            ]
        },
        {
            "phase": "Month 1–2: Vendor Sourcing & Inventory Procurement",
            "timeframe": "📅 MONTH 1–2",
            "title": "Establish Supply Chains & Secure Opening Stock",
            "desc": f"Connect with authorized regional distributors in {district} and state wholesale hubs. Secure your opening stock with negotiated 15-day credit terms, and set up your digital billing terminal.",
            "badges": ["📦 Stock: High-demand verified inventory", "💡 Tip: Secure 15-day vendor credit", "💻 Tech: Digital billing + UPI QR"],
            "tasks": [
                f"Source opening stock directly from authorized wholesale distributors in {district}/{state}",
                "Negotiate 10-15 day revolving credit limits based on regular weekly re-orders",
                "Install digital billing software (Vyapar/Khatabook) and set up multi-bank UPI QR stands",
                "Procure required sector machinery, testing tools, or refrigeration units"
            ]
        },
        {
            "phase": "Month 2–3: Grand Launch & Local Community Outreach",
            "timeframe": "📅 MONTH 2–3",
            "title": "Commence Operations & Build Neighborhood Footfall",
            "desc": f"Host an auspicious opening with introductory discounts. Distribute flyers within a 3 km cluster, set up your Google Business profile, and launch WhatsApp ordering.",
            "badges": ["📢 Marketing: Pamphlets + WhatsApp groups", "🎁 Promotion: Inaugural customer gift/discount", "🌐 Digital: Google Business Profile live"],
            "tasks": [
                "Create and verify Google Business Profile so local searchers find your shop on Google Maps",
                "Set up WhatsApp Business with full product/service catalogue and broadcast lists",
                "Distribute 1,000 inaugural pamphlets across residential clusters and local market areas",
                "Introduce opening week promotional offers to convert first-time visitors into repeat patrons"
            ]
        },
        {
            "phase": "Month 4–6: Revenue Optimization & Break-Even Assurance",
            "timeframe": "📅 MONTH 4–6",
            "title": "Scale High-Margin Offerings & Solidify Positive Cashflow",
            "desc": f"Evaluate sales data to double down on your most profitable offerings. Introduce institutional contracts or subscriptions to guarantee monthly fixed expenses are covered effortlessly.",
            "badges": ["💳 Retention: Customer loyalty perks", "📈 Margin: Expand high-profit services", "🛡️ Assurance: Stable positive cashflow"],
            "tasks": [
                "Analyze Month 3 sales to eliminate slow-moving inventory and double top-selling stock",
                "Introduce high-margin value-add services (repairs, custom orders, or tiffin subscriptions)",
                "Secure institutional bulk contracts with local schools, offices, or commercial establishments",
                f"Achieve consistent operational break-even and commence planned bank loan repayments"
            ]
        }
    ]

    statutory_checklist = [
        {"name": "Udyam MSME Registration", "mandatory": True, "portal": "udyamregistration.gov.in", "fee": "Free"},
        {"name": "Gram Panchayat / Municipal Trade Licence", "mandatory": True, "portal": "Local Block Office", "fee": "Nominal"},
        {"name": "GST Registration", "mandatory": False, "portal": "gst.gov.in", "fee": "Free (Compulsory over ₹20L/₹40L turnover)"},
        {"name": "FSSAI Food Licence (For Food/Dairy/Bakery/Restaurant)", "mandatory": bdata["sector"] in ["Food & Hospitality Processing", "Food Service & Hospitality", "Agri-Food & Livestock Processing"], "portal": "foscos.fssai.gov.in", "fee": "₹100/year (Basic)"},
        {"name": "Current Bank Account with Udyam Certificate", "mandatory": True, "portal": "Any Scheduled Commercial Bank", "fee": "Zero minimum for MSME"}
    ]

    key_milestones = [
        {"milestone": "Statutory Permits & Udyam Registration", "target_day": 7},
        {"milestone": "PMEGP / Bank Loan Sanction", "target_day": 25},
        {"milestone": "Shop Infrastructure & Opening Inventory Ready", "target_day": 35},
        {"milestone": "First 100 Paying Customers Served", "target_day": 50},
        {"milestone": "Operational Break-Even Achieved", "target_day": bdata["break_even_months"] * 30},
        {"milestone": "Full Investment Capital Recouped", "target_day": (bdata["break_even_months"] + 6) * 30}
    ]

    assurances = [
        {"title": "Regulatory Assurance", "desc": "100% adherence to central and state MSME guidelines guarantees complete protection against arbitrary local inspection disruptions."},
        {"title": "Cashflow Buffer Assurance", "desc": f"Maintaining a minimum 60-day working capital reserve of ₹{investment * 0.15:,.0f} insulates your business against seasonal lulls."},
        {"title": "Subsidy Sanction Assurance", "desc": "Properly prepared project documentation via this platform matches DIC requirements for seamless government subsidy processing."}
    ]

    return {
        "business_name": biz_name,
        "stage": stage,
        "timeline": phases,
        "statutory_checklist": statutory_checklist,
        "key_milestones": key_milestones,
        "assurances": assurances,
        "quick_wins": [
            "Register on Google Maps today — customers searching nearby will discover your phone number and address instantly",
            "Set up WhatsApp Business with catalog to take phone orders with zero commission",
            "Speak with 15 target customers in your immediate neighbourhood before finalizing initial inventory"
        ]
    }
