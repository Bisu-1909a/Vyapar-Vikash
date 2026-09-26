"""
geo_data.py – Comprehensive Pan-India Geographic & Micro-Economic Database
Contains all 36 States & Union Territories of India, all 780+ Districts,
and rich sub-district / block / taluk / village area intelligence with economic indicators.
"""

# All 28 States + 8 Union Territories
ALL_INDIA_STATES = [
    {"name": "Andhra Pradesh", "code": "AP", "zone": "South", "capital": "Amaravati", "gdp_growth": 11.4, "primary_industry": "Agriculture, Aquaculture, IT, Pharma"},
    {"name": "Arunachal Pradesh", "code": "AR", "zone": "Northeast", "capital": "Itanagar", "gdp_growth": 9.2, "primary_industry": "Horticulture, Handloom, Tourism, Hydro"},
    {"name": "Assam", "code": "AS", "zone": "Northeast", "capital": "Dispur", "gdp_growth": 10.1, "primary_industry": "Tea, Petroleum, Handloom, Food Processing"},
    {"name": "Bihar", "code": "BR", "zone": "East", "capital": "Patna", "gdp_growth": 10.6, "primary_industry": "Agriculture, FMCG, Dairy, Food Processing"},
    {"name": "Chhattisgarh", "code": "CG", "zone": "Central", "capital": "Raipur", "gdp_growth": 11.2, "primary_industry": "Minerals, Steel, Forest Produce, Agri"},
    {"name": "Goa", "code": "GA", "zone": "West", "capital": "Panaji", "gdp_growth": 9.8, "primary_industry": "Tourism, Hospitality, Fisheries, Pharma"},
    {"name": "Gujarat", "code": "GJ", "zone": "West", "capital": "Gandhinagar", "gdp_growth": 13.1, "primary_industry": "Chemicals, Textiles, Engineering, Dairy"},
    {"name": "Haryana", "code": "HR", "zone": "North", "capital": "Chandigarh", "gdp_growth": 11.8, "primary_industry": "Automobiles, IT, Dairy, Agro-processing"},
    {"name": "Himachal Pradesh", "code": "HP", "zone": "North", "capital": "Shimla", "gdp_growth": 8.7, "primary_industry": "Horticulture, Tourism, Hydro, Pharma"},
    {"name": "Jharkhand", "code": "JH", "zone": "East", "capital": "Ranchi", "gdp_growth": 9.5, "primary_industry": "Mining, Heavy Engineering, Steel, Forest"},
    {"name": "Karnataka", "code": "KA", "zone": "South", "capital": "Bengaluru", "gdp_growth": 12.5, "primary_industry": "IT/Software, Silk, Coffee, Engineering"},
    {"name": "Kerala", "code": "KL", "zone": "South", "capital": "Thiruvananthapuram", "gdp_growth": 9.6, "primary_industry": "Spices, Tourism, Marine Exports, Healthcare"},
    {"name": "Madhya Pradesh", "code": "MP", "zone": "Central", "capital": "Bhopal", "gdp_growth": 12.8, "primary_industry": "Agriculture, Soyabean, Textiles, Mining"},
    {"name": "Maharashtra", "code": "MH", "zone": "West", "capital": "Mumbai", "gdp_growth": 12.1, "primary_industry": "Finance, Manufacturing, Automobiles, Sugar"},
    {"name": "Manipur", "code": "MN", "zone": "Northeast", "capital": "Imphal", "gdp_growth": 7.8, "primary_industry": "Handlooms, Bamboo Crafts, Horticulture"},
    {"name": "Meghalaya", "code": "ML", "zone": "Northeast", "capital": "Shillong", "gdp_growth": 8.3, "primary_industry": "Tourism, Spices (Lakadong Turmeric), Agro"},
    {"name": "Mizoram", "code": "MZ", "zone": "Northeast", "capital": "Aizawl", "gdp_growth": 8.9, "primary_industry": "Bamboo, Spices, Floriculture, Handlooms"},
    {"name": "Nagaland", "code": "NL", "zone": "Northeast", "capital": "Kohima", "gdp_growth": 7.6, "primary_industry": "Handicrafts, Horticulture, Organic Honey"},
    {"name": "Odisha", "code": "OD", "zone": "East", "capital": "Bhubaneswar", "gdp_growth": 11.5, "primary_industry": "Steel, Mining, Seafood, Handlooms, IT"},
    {"name": "Punjab", "code": "PB", "zone": "North", "capital": "Chandigarh", "gdp_growth": 9.4, "primary_industry": "Agriculture, Agro-machinery, Textiles, Sports Goods"},
    {"name": "Rajasthan", "code": "RJ", "zone": "North", "capital": "Jaipur", "gdp_growth": 11.0, "primary_industry": "Tourism, Solar, Handicrafts, Minerals, Dairy"},
    {"name": "Sikkim", "code": "SK", "zone": "Northeast", "capital": "Gangtok", "gdp_growth": 8.5, "primary_industry": "Organic Farming, Tourism, Cardamom, Pharma"},
    {"name": "Tamil Nadu", "code": "TN", "zone": "South", "capital": "Chennai", "gdp_growth": 12.0, "primary_industry": "Automobiles, Textiles, Leather, Hardware, IT"},
    {"name": "Telangana", "code": "TS", "zone": "South", "capital": "Hyderabad", "gdp_growth": 13.0, "primary_industry": "IT, Biotechnology, Pharma, Cotton, Poultry"},
    {"name": "Tripura", "code": "TR", "zone": "Northeast", "capital": "Agartala", "gdp_growth": 8.8, "primary_industry": "Rubber, Tea, Bamboo Handicrafts, Natural Gas"},
    {"name": "Uttar Pradesh", "code": "UP", "zone": "North", "capital": "Lucknow", "gdp_growth": 12.2, "primary_industry": "Agro-processing, Leather, Handicrafts (ODOP), Sugar"},
    {"name": "Uttarakhand", "code": "UK", "zone": "North", "capital": "Dehradun", "gdp_growth": 9.8, "primary_industry": "Tourism, Herbs, Food Processing, Auto Ancillary"},
    {"name": "West Bengal", "code": "WB", "zone": "East", "capital": "Kolkata", "gdp_growth": 10.3, "primary_industry": "Jute, Tea, Leather, Textiles, Agriculture"},
    # Union Territories
    {"name": "Andaman and Nicobar Islands", "code": "AN", "zone": "UT", "capital": "Port Blair", "gdp_growth": 8.0, "primary_industry": "Fisheries, Tourism, Coconut/Arecanut"},
    {"name": "Chandigarh", "code": "CH", "zone": "UT", "capital": "Chandigarh", "gdp_growth": 9.5, "primary_industry": "Trade, Services, IT, Banking"},
    {"name": "Dadra and Nagar Haveli and Daman and Diu", "code": "DH", "zone": "UT", "capital": "Daman", "gdp_growth": 10.2, "primary_industry": "Manufacturing, Textiles, Plastics, Tourism"},
    {"name": "Delhi", "code": "DL", "zone": "UT", "capital": "New Delhi", "gdp_growth": 11.8, "primary_industry": "Services, Wholesale Trade, Retail, IT, Tourism"},
    {"name": "Jammu and Kashmir", "code": "JK", "zone": "UT", "capital": "Srinagar/Jammu", "gdp_growth": 8.9, "primary_industry": "Horticulture (Apples/Walnuts), Handicrafts, Tourism"},
    {"name": "Ladakh", "code": "LA", "zone": "UT", "capital": "Leh", "gdp_growth": 7.5, "primary_industry": "Tourism, Pashmina Wool, Apricots, Seabuckthorn"},
    {"name": "Lakshadweep", "code": "LD", "zone": "UT", "capital": "Kavaratti", "gdp_growth": 7.0, "primary_industry": "Coconut, Fisheries (Tuna), Coir, Tourism"},
    {"name": "Puducherry", "code": "PY", "zone": "UT", "capital": "Puducherry", "gdp_growth": 9.1, "primary_industry": "Tourism, Textiles, Fisheries, Light Engineering"},
]

# Comprehensive Pan-India Districts mapping (All 780+ districts categorized by State/UT)
ALL_INDIA_DISTRICTS = {
    "Andhra Pradesh": [
        "Alluri Sitharama Raju", "Anakapalli", "Ananthapuramu", "Annamayya", "Bapatla", "Chittoor",
        "Dr. B.R. Ambedkar Konaseema", "East Godavari", "Eluru", "Guntur", "Kakinada", "Krishna",
        "Kurnool", "Nandyal", "NTR", "Palnadu", "Parvathipuram Manyam", "Prakasam", "Sri Potti Sriramulu Nellore",
        "Sri Sathya Sai", "Srikakulam", "Tirupati", "Visakhapatnam", "Vizianagaram", "West Godavari", "YSR Kadapa"
    ],
    "Arunachal Pradesh": [
        "Anjaw", "Changlang", "Dibang Valley", "East Kameng", "East Siang", "Kamle", "Kra Daadi",
        "Kurung Kumey", "Leparada", "Lohit", "Longding", "Lower Dibang Valley", "Lower Siang",
        "Lower Subansiri", "Namsai", "Pakke Kessang", "Papum Pare", "Shi Yomi", "Siang", "Tawang",
        "Tirap", "Upper Siang", "Upper Subansiri", "West Kameng", "West Siang"
    ],
    "Assam": [
        "Baksa", "Barpeta", "Biswanath", "Bongaigaon", "Cachar", "Charaideo", "Chirang", "Darrang",
        "Dhemaji", "Dhubri", "Dibrugarh", "Dima Hasao", "Goalpara", "Golaghat", "Hailakandi", "Hojai",
        "Jorhat", "Kamrup", "Kamrup Metropolitan", "Karbi Anglong", "Karimganj", "Kokrajhar", "Lakhimpur",
        "Majuli", "Morigaon", "Nagaon", "Nalbari", "Sivasagar", "Sonitpur", "South Salmara-Mankachar",
        "Tinsukia", "Udalguri", "West Karbi Anglong"
    ],
    "Bihar": [
        "Araria", "Arwal", "Aurangabad", "Banka", "Begusarai", "Bhagalpur", "Bhojpur", "Buxar",
        "Darbhanga", "East Champaran (Motihari)", "Gaya", "Gopalganj", "Jamui", "Jehanabad", "Kaimur (Bhabua)",
        "Katihar", "Khagaria", "Kishanganj", "Lakhisarai", "Madhepura", "Madhubani", "Munger", "Muzaffarpur",
        "Nalanda", "Nawada", "Patna", "Purnia", "Rohtas (Sasaram)", "Saharsa", "Samastipur", "Saran (Chhapra)",
        "Sheikhpura", "Sheohar", "Sitamarhi", "Siwan", "Supaul", "Vaishali (Hajipur)", "West Champaran (Bettiah)"
    ],
    "Chhattisgarh": [
        "Balod", "Baloda Bazar", "Balrampur", "Bastar", "Bemetara", "Bijapur", "Bilaspur", "Dantewada",
        "Dhamtari", "Durg", "Gariaband", "Gaurela-Pendra-Marwahi", "Janjgir-Champa", "Jashpur", "Kabirdham (Kawardha)",
        "Kanker", "Khairagarh-Chhuikhadan-Gandai", "Kondagaon", "Korba", "Koriya", "Mahasamund", "Manendragarh-Chirmiri-Bharatpur",
        "Mohla-Manpur-Ambagarh Chowki", "Mungeli", "Narayanpur", "Raigarh", "Raipur", "Rajnandgaon", "Sarangarh-Bilaigarh",
        "Sakti", "Sukma", "Surajpur", "Surguja"
    ],
    "Goa": [
        "North Goa", "South Goa"
    ],
    "Gujarat": [
        "Ahmedabad", "Amreli", "Anand", "Aravalli", "Banaskantha", "Bharuch", "Bhavnagar", "Botad",
        "Chhota Udaipur", "Dahod", "Dang", "Devbhoomi Dwarka", "Gandhinagar", "Gir Somnath", "Jamnagar",
        "Junagadh", "Kheda", "Kutch", "Mahisagar", "Mehsana", "Morbi", "Narmada", "Navsari",
        "Panchmahal", "Patan", "Porbandar", "Rajkot", "Sabarkantha", "Surat", "Surendranagar", "Tapi",
        "Vadodara", "Valsad"
    ],
    "Haryana": [
        "Ambala", "Bhiwani", "Charkhi Dadri", "Faridabad", "Fatehabad", "Gurugram", "Hisar", "Jhajjar",
        "Jind", "Kaithal", "Karnal", "Kurukshetra", "Mahendragarh", "Nuh", "Palwal", "Panchkula",
        "Panipat", "Rewari", "Rohtak", "Sirsa", "Sonipat", "Yamunanagar"
    ],
    "Himachal Pradesh": [
        "Bilaspur", "Chamba", "Hamirpur", "Kangra", "Kinnaur", "Kullu", "Lahaul and Spiti", "Mandi",
        "Shimla", "Sirmaur", "Solan", "Una"
    ],
    "Jharkhand": [
        "Bokaro", "Chatra", "Deoghar", "Dhanbad", "Dumka", "East Singhbhum (Jamshedpur)", "Garhwa", "Giridih",
        "Godda", "Gumla", "Hazaribagh", "Jamtara", "Khunti", "Koderma", "Latehar", "Lohardaga",
        "Pakur", "Palamu", "Ramgarh", "Ranchi", "Sahibganj", "Seraikela Kharsawan", "Simdega", "West Singhbhum (Chaibasa)"
    ],
    "Karnataka": [
        "Bagalkot", "Ballari", "Belagavi", "Bengaluru Rural", "Bengaluru Urban", "Bidar", "Chamarajanagar",
        "Chikkaballapura", "Chikkamagaluru", "Chitradurga", "Dakshina Kannada (Mangaluru)", "Davanagere", "Dharwad", "Gadag",
        "Hassan", "Haveri", "Kalaburagi", "Kodagu", "Kolar", "Koppal", "Mandya", "Mysuru",
        "Raichur", "Ramanagara", "Shivamogga", "Tumakuru", "Udupi", "Uttara Kannada", "Vijayanagara", "Vijayapura", "Yadgir"
    ],
    "Kerala": [
        "Alappuzha", "Ernakulam (Kochi)", "Idukki", "Kannur", "Kasaragod", "Kollam", "Kottayam", "Kozhikode",
        "Malappuram", "Palakkad", "Pathanamthitta", "Thiruvananthapuram", "Thrissur", "Wayanad"
    ],
    "Madhya Pradesh": [
        "Agar Malwa", "Alirajpur", "Anuppur", "Ashoknagar", "Balaghat", "Barwani", "Betul", "Bhind",
        "Bhopal", "Burhanpur", "Chhatarpur", "Chhindwara", "Damoh", "Datia", "Dewas", "Dhar",
        "Dindori", "Guna", "Gwalior", "Harda", "Narmadapuram (Hoshangabad)", "Indore", "Jabalpur", "Jhabua",
        "Katni", "Khandwa", "Khargone", "Maihar", "Mandla", "Mandsaur", "Morena", "Mauganj",
        "Narsinghpur", "Neemuch", "Niwari", "Panna", "Pandhurna", "Raisen", "Rajgarh", "Ratlam",
        "Rewa", "Sagar", "Satna", "Sehore", "Seoni", "Shahdol", "Shajapur", "Sheopur",
        "Shivpuri", "Sidhi", "Singrauli", "Tikamgarh", "Ujjain", "Umaria", "Vidisha"
    ],
    "Maharashtra": [
        "Ahmednagar (Ahilyanagar)", "Akola", "Amravati", "Chhatrapati Sambhaji Nagar (Aurangabad)", "Beed", "Bhandara", "Buldhana", "Chandrapur",
        "Dhule", "Gadchiroli", "Gondia", "Hingoli", "Jalgaon", "Jalna", "Kolhapur", "Latur",
        "Mumbai City", "Mumbai Suburban", "Nagpur", "Nanded", "Nandurbar", "Nashik", "Dharashiv (Osmanabad)", "Palghar",
        "Parbhani", "Pune", "Raigad", "Ratnagiri", "Sangli", "Satara", "Sindhudurg", "Solapur",
        "Thane", "Wardha", "Washim", "Yavatmal"
    ],
    "Manipur": [
        "Bishnupur", "Chandel", "Churachandpur", "Imphal East", "Imphal West", "Jiribam", "Kakching",
        "Kamjong", "Kangpokpi", "Noney", "Pherzawl", "Senapati", "Tamenglong", "Tengnoupal", "Thoubal", "Ukhrul"
    ],
    "Meghalaya": [
        "East Garo Hills", "East Jaintia Hills", "East Khasi Hills (Shillong)", "Eastern West Khasi Hills",
        "North Garo Hills", "Ri-Bhoi", "South Garo Hills", "South West Garo Hills", "South West Khasi Hills",
        "West Garo Hills (Tura)", "West Jaintia Hills", "West Khasi Hills"
    ],
    "Mizoram": [
        "Aizawl", "Champhai", "Hnahthial", "Khawzawl", "Kolasib", "Lawngtlai", "Lunglei", "Mamit",
        "Saitual", "Serchhip", "Siaha"
    ],
    "Nagaland": [
        "Chumoukedima", "Dimapur", "Kiphire", "Kohima", "Longleng", "Mokokchung", "Mon", "Niuland",
        "Noklak", "Peren", "Phek", "Shamator", "Tseminyu", "Tuensang", "Wokha", "Zunheboto"
    ],
    "Odisha": [
        "Angul", "Balangir", "Balasore (Baleswar)", "Bargarh", "Bhadrak", "Boudh", "Cuttack", "Deogarh",
        "Dhenkanal", "Gajapati", "Ganjam", "Jagatsinghpur", "Jajpur", "Jharsuguda", "Kalahandi", "Kandhamal",
        "Kendrapara", "Kendujhar (Keonjhar)", "Khordha (Bhubaneswar)", "Koraput", "Malkangiri", "Mayurbhanj",
        "Nabarangpur", "Nayagarh", "Nuapada", "Puri", "Rayagada", "Sambalpur", "Subarnapur (Sonepur)", "Sundargarh"
    ],
    "Punjab": [
        "Amritsar", "Barnala", "Bathinda", "Faridkot", "Fatehgarh Sahib", "Fazilka", "Ferozepur", "Gurdaspur",
        "Hoshiarpur", "Jalandhar", "Kapurthala", "Ludhiana", "Malerkotla", "Mansa", "Moga", "Muktsar",
        "Pathankot", "Patiala", "Rupnagar", "Sahibzada Ajit Singh Nagar (Mohali)", "Sangrur", "Shahid Bhagat Singh Nagar (Nawanshahr)", "Tarn Taran"
    ],
    "Rajasthan": [
        "Ajmer", "Alwar", "Anupgarh", "Balotra", "Banswara", "Baran", "Barmer", "Beawar",
        "Bharatpur", "Bhilwara", "Bikaner", "Bundi", "Chittorgarh", "Churu", "Dausa", "Deeg",
        "Dholpur", "Didwana-Kuchaman", "Dudu", "Dungarpur", "Ganganagar", "Gangapur City", "Hanumangarh",
        "Jaipur", "Jaipur Rural", "Jaisalmer", "Jalore", "Jhalawar", "Jhunjhunu", "Jodhpur", "Jodhpur Rural",
        "Karauli", "Kekri", "Khairthal-Tijara", "Kota", "Kotputli-Behror", "Nagaur", "Neem Ka Thana",
        "Pali", "Phalodi", "Pratapgarh", "Rajsamand", "Salumbar", "Sanchore", "Sawai Madhopur", "Shahpura",
        "Sikar", "Sirohi", "Tonk", "Udaipur"
    ],
    "Sikkim": [
        "Gangtok", "Gyalshing", "Mangan", "Namchi", "Pakyong", "Soreng"
    ],
    "Tamil Nadu": [
        "Ariyalur", "Chengalpattu", "Chennai", "Coimbatore", "Cuddalore", "Dharmapuri", "Dindigul", "Erode",
        "Kallakurichi", "Kanchipuram", "Kanyakumari", "Karur", "Krishnagiri", "Madurai", "Mayiladuthurai", "Nagapattinam",
        "Namakkal", "Nilgiris", "Perambalur", "Pudukkottai", "Ramanathapuram", "Ranipet", "Salem", "Sivaganga",
        "Tenkasi", "Thanjavur", "Theni", "Thoothukudi", "Tiruchirappalli", "Tirunelveli", "Tirupathur", "Tiruppur",
        "Tiruvallur", "Tiruvannamalai", "Tiruvarur", "Vellore", "Viluppuram", "Virudhunagar"
    ],
    "Telangana": [
        "Adilabad", "Bhadradri Kothagudem", "Hanumakonda", "Hyderabad", "Jagtial", "Jangaon", "Jayashankar Bhupalpally",
        "Jogulamba Gadwal", "Kamareddy", "Karimnagar", "Khammam", "Kumuram Bheem Asifabad", "Mahabubabad", "Mahabubnagar",
        "Mancherial", "Medak", "Medchal-Malkajgiri", "Mulugu", "Nagarkurnool", "Nalgonda", "Narayanpet", "Nirmal",
        "Nizamabad", "Peddapalli", "Rajanna Sircilla", "Rangareddy", "Sangareddy", "Siddipet", "Suryapet", "Vikarabad",
        "Wanaparthy", "Warangal", "Yadadri Bhuvanagiri"
    ],
    "Tripura": [
        "Dhalai", "Gomati", "Khowai", "North Tripura", "Sepahijala", "South Tripura", "Unakoti", "West Tripura"
    ],
    "Uttar Pradesh": [
        "Agra", "Aligarh", "Ambedkar Nagar", "Amethi", "Amroha", "Auraiya", "Ayodhya (Faizabad)", "Azamgarh",
        "Baghpat", "Bahraich", "Ballia", "Balrampur", "Banda", "Barabanki", "Bareilly", "Basti",
        "Bhadohi", "Bijnor", "Budaun", "Bulandshahr", "Chandauli", "Chitrakoot", "Deoria", "Etah",
        "Etawah", "Farrukhabad", "Fatehpur", "Firozabad", "Gautam Buddha Nagar (Noida)", "Ghaziabad", "Ghazipur", "Gonda",
        "Gorakhpur", "Hamirpur", "Hapur", "Hardoi", "Hathras", "Jalaun", "Jaunpur", "Jhansi",
        "Kannauj", "Kanpur Dehat", "Kanpur Nagar", "Kasganj", "Kaushambi", "Kheri (Lakhimpur)", "Kushinagar", "Lalitpur",
        "Lucknow", "Maharajganj", "Mahoba", "Mainpuri", "Mathura", "Mau", "Meerut", "Mirzapur",
        "Moradabad", "Muzaffarnagar", "Pilibhit", "Pratapgarh", "Prayagraj (Allahabad)", "Raebareli", "Rampur", "Saharanpur",
        "Sambhal", "Sant Kabir Nagar", "Shahjahanpur", "Shamli", "Shravasti", "Siddharthnagar", "Sitapur", "Sonbhadra",
        "Sultanpur", "Unnao", "Varanasi"
    ],
    "Uttarakhand": [
        "Almora", "Bageshwar", "Chamoli", "Champawat", "Dehradun", "Haridwar", "Nainital", "Pauri Garhwal",
        "Pithoragarh", "Rudraprayag", "Tehri Garhwal", "Udham Singh Nagar", "Uttarkashi"
    ],
    "West Bengal": [
        "Alipurduar", "Bankura", "Birbhum", "Cooch Behar", "Dakshin Dinajpur", "Darjeeling", "Hooghly", "Howrah",
        "Jalpaiguri", "Jhargram", "Kalimpong", "Kolkata", "Malda", "Murshidabad", "Nadia", "North 24 Parganas",
        "Paschim Bardhaman", "Paschim Medinipur", "Purba Bardhaman", "Purba Medinipur", "Purulia", "South 24 Parganas", "Uttar Dinajpur"
    ],
    # Union Territories Districts
    "Andaman and Nicobar Islands": [
        "Nicobar", "North and Middle Andaman", "South Andaman"
    ],
    "Chandigarh": [
        "Chandigarh"
    ],
    "Dadra and Nagar Haveli and Daman and Diu": [
        "Dadra and Nagar Haveli", "Daman", "Diu"
    ],
    "Delhi": [
        "Central Delhi", "East Delhi", "New Delhi", "North Delhi", "North East Delhi", "North West Delhi",
        "Shahdara", "South Delhi", "South East Delhi", "South West Delhi", "West Delhi"
    ],
    "Jammu and Kashmir": [
        "Anantnag", "Bandipora", "Baramulla", "Budgam", "Doda", "Ganderbal", "Jammu", "Kathua",
        "Kishtwar", "Kulgam", "Kupwara", "Poonch", "Pulwama", "Rajouri", "Ramban", "Reasi",
        "Samba", "Shopian", "Srinagar", "Udhampur"
    ],
    "Ladakh": [
        "Kargil", "Leh"
    ],
    "Lakshadweep": [
        "Lakshadweep"
    ],
    "Puducherry": [
        "Karaikal", "Mahe", "Puducherry", "Yanam"
    ]
}

# Micro-area profiles & Sub-district intelligence database
# Provides hyper-local archetype calibration for rental rates, wages, floating footfall, and business advantages
MICRO_AREA_ARCHETYPES = {
    "rural_gram_panchayat": {
        "label": "Rural Village Cluster / Gram Panchayat",
        "area_type": "rural",
        "radius_km": 3.5,
        "catchment_pop_range": "3,000 – 12,000 residents",
        "avg_sqft_rent": 12.0,  # ₹12/sqft
        "daily_wage_rate": 350.0,
        "footfall_index": 5.8,
        "power_reliability_hrs": 18,
        "advantages": ["Zero high-street broker fees", "High community word-of-mouth trust", "Low overhead and operating costs", "Highest PMEGP 35% margin subsidy"],
        "consumer_behavior": "Value-conscious, relies heavily on trusted personal relationship, daily cash & UPI mix, visits weekly haats/bazaars.",
        "logistics_note": "Direct access via PMGSY all-weather rural roads; last-mile transport via mini-trucks and auto-rickshaws."
    },
    "semi_urban_block_hub": {
        "label": "Semi-Urban Block / Taluk Market Center",
        "area_type": "semi_urban",
        "radius_km": 6.0,
        "catchment_pop_range": "25,000 – 80,000 residents",
        "avg_sqft_rent": 28.0,
        "daily_wage_rate": 450.0,
        "footfall_index": 7.8,
        "power_reliability_hrs": 21,
        "advantages": ["Central feeder point for 15-20 surrounding villages", "High daily commercial trade velocity", "Presence of multiple bank branches and ATMs", "Eligible for 25-35% PMEGP subsidies"],
        "consumer_behavior": "Aspirational, values brand reliability and warranties, 80%+ smartphone/UPI penetration, steady weekday and booming weekend sales.",
        "logistics_note": "State highway connectivity with daily bus terminals and direct wholesale delivery routes."
    },
    "highway_junction_bazaar": {
        "label": "Highway Junction & Transit Corridor",
        "area_type": "semi_urban",
        "radius_km": 8.0,
        "catchment_pop_range": "15,000 resident + 10,000+ daily floating transit traffic",
        "avg_sqft_rent": 38.0,
        "daily_wage_rate": 500.0,
        "footfall_index": 8.6,
        "power_reliability_hrs": 22,
        "advantages": ["24/7 constant vehicle and traveler footfall", "High impulse purchase volume", "Excellent logistics and direct container/truck access"],
        "consumer_behavior": "Fast-service oriented, prefers ready-to-go products, high-ticket takeaway orders, 90%+ digital transactions.",
        "logistics_note": "National/State Highway direct frontage with parking convenience."
    },
    "urban_outskirts_hub": {
        "label": "Urban Outskirts & Suburban Growth Corridor",
        "area_type": "urban_outskirts",
        "radius_km": 5.0,
        "catchment_pop_range": "50,000 – 1,50,000 residents",
        "avg_sqft_rent": 48.0,
        "daily_wage_rate": 550.0,
        "footfall_index": 8.2,
        "power_reliability_hrs": 23,
        "advantages": ["Rapidly growing residential population", "30-40% cheaper commercial rentals than central city", "High young workforce and student density"],
        "consumer_behavior": "Digitally savvy, uses WhatsApp/phone deliveries, seeks modern retail aesthetics and branded quality.",
        "logistics_note": "City bypass roads with same-day e-commerce and wholesale distributor replenishment."
    },
    "urban_city_ward": {
        "label": "Urban City Center / Municipal Ward",
        "area_type": "urban",
        "radius_km": 3.0,
        "catchment_pop_range": "75,000 – 2,50,000 residents",
        "avg_sqft_rent": 85.0,
        "daily_wage_rate": 650.0,
        "footfall_index": 9.2,
        "power_reliability_hrs": 24,
        "advantages": ["Very high daily transaction density", "Higher average basket spending value", "Fastest inventory turnover and supplier proximity"],
        "consumer_behavior": "Time-sensitive, quality and convenience focused, 100% digital payment adoption, high repeat ordering.",
        "logistics_note": "Intense urban traffic; micro-warehousing and bike delivery recommended."
    },
    "agro_cluster_mandi": {
        "label": "Agricultural Cluster & APMC Mandi Hub",
        "area_type": "rural",
        "radius_km": 7.0,
        "catchment_pop_range": "20,000 farmers & agro-traders",
        "avg_sqft_rent": 18.0,
        "daily_wage_rate": 380.0,
        "footfall_index": 8.4,
        "power_reliability_hrs": 19,
        "advantages": ["Direct farm-gate raw material sourcing at wholesale prices", "Massive seasonal liquidity surges during harvest cycles", "High eligibility for PMFME & Agri-Infra Fund subsidies"],
        "consumer_behavior": "Bulk buying during harvest months (Rabi/Kharif), values durability and robust machinery, strong community ties.",
        "logistics_note": "Heavy tractor and commercial vehicle connectivity directly linked to state agricultural mandis."
    }
}

# Sub-area presets for major districts to provide instant, authentic suggestions
SAMPLE_BLOCKS_AND_VILLAGES = {
    "Odisha": {
        "Cuttack": [
            {"block": "Athagarh", "villages": ["Gopalpur", "Chagharia", "Khurda", "Radhakishorepur", "Samsarpur"], "type": "rural_gram_panchayat"},
            {"block": "Banki", "villages": ["Banki Town", "Charchika", "Kalapathar", "Baideswar"], "type": "semi_urban_block_hub"},
            {"block": "Salepur", "villages": ["Salepur Bazaar", "Bahugram", "Machhagaon", "Kusunpur"], "type": "semi_urban_block_hub"},
            {"block": "Choudwar", "villages": ["Choudwar Industrial Area", "Charbatia", "Gandhi Chowk", "Naya Bazaar"], "type": "highway_junction_bazaar"},
            {"block": "Barabati Cuttack", "villages": ["Badambadi", "Buxi Bazaar", "Chandi Mandir Road", "Link Road", "College Square"], "type": "urban_city_ward"}
        ],
        "Khordha (Bhubaneswar)": [
            {"block": "Bhubaneswar Urban", "villages": ["Patia", "Nayapalli", "Saheed Nagar", "Jatani", "Khandagiri", "Chandrasekharpur"], "type": "urban_city_ward"},
            {"block": "Balianta", "villages": ["Balianta Market", "Hanspal", "Bhingarpur", "Phulnakhara"], "type": "urban_outskirts_hub"},
            {"block": "Banapur", "villages": ["Banapur Main", "Bhagabatpur", "Chilika Border", "Nachuni"], "type": "rural_gram_panchayat"},
            {"block": "Begunia", "villages": ["Begunia Chowk", "Bagedia", "Kantabada", "Siko"], "type": "rural_gram_panchayat"}
        ],
        "Ganjam": [
            {"block": "Berhampur Urban", "villages": ["Giri Road", "Bada Bazaar", "Gosani Nuagaon", "Kamapalli", "Ankuli"], "type": "urban_city_ward"},
            {"block": "Chhatrapur", "villages": ["Chhatrapur Court", "Aryapalli", "Ganjam Port Road"], "type": "semi_urban_block_hub"},
            {"block": "Aska", "villages": ["Aska Sugar Mill Road", "Babanpur", "Pakalapalli"], "type": "agro_cluster_mandi"},
            {"block": "Bhanjanagar", "villages": ["Bhanjanagar Town", "Lalsingi", "Baunsalundi"], "type": "semi_urban_block_hub"}
        ],
        "Puri": [
            {"block": "Puri Sadar", "villages": ["Grand Road", "Chakratirtha Road", "Atharanala", "Samgara"], "type": "urban_city_ward"},
            {"block": "Pipili", "villages": ["Pipili Applique Market", "Dandamukundapur", "Teisipur", "Satsankha"], "type": "highway_junction_bazaar"},
            {"block": "Nimapada", "villages": ["Nimapada Town", "Dhanua", "Rench", "Sagada"], "type": "agro_cluster_mandi"},
            {"block": "Konark", "villages": ["Sun Temple Road", "Chandrabhaga Beach Road", "Gop"], "type": "highway_junction_bazaar"}
        ],
        "Sambalpur": [
            {"block": "Sambalpur City", "villages": ["Budharaja", "Dhanupali", "Khetrajpur", "Ainthapali", "Bareipali"], "type": "urban_city_ward"},
            {"block": "Rengali", "villages": ["Rengali Station", "Lapanga", "Nishana"], "type": "highway_junction_bazaar"},
            {"block": "Kuchinda", "villages": ["Kuchinda Market", "Kuntara", "Bhojpur"], "type": "semi_urban_block_hub"}
        ]
    }
}


def get_area_archetype(area_type_or_name: str) -> dict:
    """Returns matching micro-area archetype details."""
    key = str(area_type_or_name).lower().replace(" ", "_").replace("-", "_")
    if "panchayat" in key or "village" in key or key == "rural":
        return MICRO_AREA_ARCHETYPES["rural_gram_panchayat"]
    elif "mandi" in key or "agro" in key or "krishi" in key:
        return MICRO_AREA_ARCHETYPES["agro_cluster_mandi"]
    elif "highway" in key or "junction" in key or "corridor" in key:
        return MICRO_AREA_ARCHETYPES["highway_junction_bazaar"]
    elif "outskirt" in key or "suburban" in key:
        return MICRO_AREA_ARCHETYPES["urban_outskirts_hub"]
    elif "semi_urban" in key:
        return MICRO_AREA_ARCHETYPES["semi_urban_block_hub"]
    elif "ward" in key or "urban" in key or "city" in key:
        return MICRO_AREA_ARCHETYPES["urban_city_ward"]
    else:
        return MICRO_AREA_ARCHETYPES["semi_urban_block_hub"]
