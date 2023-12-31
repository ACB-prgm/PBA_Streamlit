SECTION_RANGES = {
    'PRE-PRODUCTION | WRAP LABOR': range(0, 51),
    'SHOOTING LABOR': range(51, 101),
    'PRE-PRODUCTION | WRAP EXPENSES': range(101, 114),
    'LOCATION AND TRAVEL': range(114, 139),
    'MAKEUP, WARDROBE, AND ANIMALS': range(140, 151),
    'STUDIO | STAGE RENTAL / EXPENSES': range(151, 167),
    'ART DEPARTMENT LABOR': range(168, 181),
    'ART DEPARTMENT EXPENSES': range(181, 193),
    'EQUIPMENT COSTS': range(193, 210),
    'FILMSTOCK, DEVELOP AND PRINT': range(211, 217),
    'MISCELLANEOUS': range(217, 227),
    'DIRECTOR | CREATIVE FEES': range(227, 234),
    'TALENT LABOR': range(234, 271),
    'TALENT EXPENSES': range(271, 277),
    'POST PRODUCTION LABOR': range(277, 282),
    'EDITORIAL | FINISHING | POST PRODUCTION': range(282, 329)
}

HB_CS_COLS = ["SECTION", "drop", "BID TOTALS", "ACTUAL", "VARIANCE"]
CS_SUBSECTION_COLS = ["LINE", "SUB SECTION", "DAYS", "RATE", "ESTIMATE", "ACTUAL"]
PR_COLS = ['LINE', 'PAYEE', 'PO', 'F1', 'F2', 'DAYS', 'RATE', 'BASE', '1.5', '2', '3', 'TAXABLE', 'NON-TAX', 'TOTAL ST', 'TOTAL OT', 'ACTUAL', 'FRINGE 1', 'FRINGE 2', 'LINE DESCRIPTION']
PO_COLS = ["LINE", "PAYEE", "PO", "DATE", "PAYID", "ACTUAL", "LINE DESCRIPTION"]

HB_PDF_SECTION_LOCS = {
    'PRE-PRODUCTION | WRAP LABOR': (1, 0),
    'SHOOTING LABOR': (2, 0),
    'PRE-PRODUCTION | WRAP EXPENSES': (3, 0),
    'LOCATION AND TRAVEL': (3, 1),
    'MAKEUP, WARDROBE, AND ANIMALS': (3, 2),
    'STUDIO | STAGE RENTAL / EXPENSES': (4, 0),
    'ART DEPARTMENT LABOR': (4, 1),
    'ART DEPARTMENT EXPENSES': (4, 2),
    'EQUIPMENT COSTS': (5, 0),
    'FILMSTOCK, DEVELOP AND PRINT': (5, 1),
    'MISCELLANEOUS': (5, 2),
    'DIRECTOR | CREATIVE FEES': (5, 3),
    'TALENT LABOR': (6, 0),
    'TALENT EXPENSES': (6, 1),
    'POST PRODUCTION LABOR': (7, 0),
    'EDITORIAL | FINISHING | POST PRODUCTION': (7, 1),
}

FILE_PREFERENCE = [".xlsx", ".xlsb", ".pdf"]


restaurants = (
    'cava',
    'tocaya',
    'mcdonalds',
    'pick up stix',
    'popeyeys',
    'baja fresh',
    'subway',
    'taco bell',
    'chickfila',
    'dominos',
    'wendys',
    'kfc',
    'panera bread',
    'chipotle',
    'olive garden',
    'applebees',
    'outback',
    'red lobster',
    'cracker barrel',
    'innout',
    'in n out',
    'five guys',
    'texas roadhouse',
    'dennys',
    'panda express',
    'buffalo wild wings',
    'ihop',
    'tgi fridays',
    'ruths chris steak house',
    'pf changs',
    'golden corral',
    'carrabbas',
    'red robin',
    'hooters',
    'yard house',
    'chilis',
    'famous daves',
    'bonefish',
    'maggianos little italy',
    'maggianos',
    'mellow mushroom',
    'doordash',
    'postmates',
    'grubhub',
    'uber eats',
    'sbarro',
    'shake shack',
    'Mendocino Farms',
    'Medocino Farms'
)

restaurant_keywords = (
    "pizza",
    "restaurant",
    "resturaunt",
    "bakery",
    "chicken",
    "burger",
    "taco",
    "coffee",
    "grill",
    "barbecue",
    "diner",
    "sushi",
    "steakhouse",
    "pub",
    "bistro",
    "cafe",
    "deli",
    "noodle",
    "pasta",
    "seafood",
    "vegetarian",
    "ramen",
    "buffet",
    "food truck",
    "fast food",
    "ice cream",
    "sandwich",
    "eatery",
    "creamery",
    "cheesecake",
    "donut",
    "catering"
)

rideshare_services = (
    'uber',
    'lyft',
    'didi',
    'grab',
    'gojek',
    'via',
    'juno',
    'curb',
    'ztrip',
    'wingz',
    'argo',
    'wheely',
    'fasten',
    'safr',
    'ride austin',
    'carmel',
    'gett',
    'ridescout',
    'zum',
    'zūm',
    'moovn',
    'ridelink',
    'waze carpool',
    'wingz',
    'hopSkipDrive',
    'qapital transport',
    'vugo',
    'gocurb',
    'curb',
    'ride yellow'
)

grocery_stores = (
    'walmart',
    'kroger',
    'ralphs',
    'raplhs',
    'vons',
    'costco',
    'safeway',
    'publix',
    'aldi',
    'target',
    'whole foods',
    'whole foods market',
    'trader joes',
    'heb',
    'meijer',
    'wegmans',
    'food lion',
    'giant eagle',
    'stop and shop',
    'albertsons',
    'winco',
    'hy-vee',
    'sprouts',
    'lowes foods',
    'harris teeter',
    'giant food',
    'gelsons',
    'food4less',
    'bristol farms',
    'erewhon',
    'weis markets',
    'piggly wiggly',
    'market basket',
    'kings food markets',
    'fairway market',
    'key food',
    'acme markets',
    'grocery outlet',
    'smart  final',
    'smart and final'
)

convenience_stores = (
    '7 eleven',
    'circle k',
    'wawa',
    'speedway',
    'quiktrip',
    'sheetz',
    'caseys',
    'couche tard',
    'cumberland farms',
    'thorntons',
    'raceway',
    'holiday stationstores',
    'kum  go',
    'kum and go',
    'allsups',
    'buc ees',
    'maverik',
    'stripes',
    'am pm',
    'ampm',
    'gate petroleum',
    'kangaroo express',
    'gulf oil',
    'loves travel stops',
    'chevron extra mile',
    'mobil on the run',
    'petro express',
    'valero',
    'quik mart',
    'ez mart',
    'weigels',
    'roadrunner markets',
    'cvs'
)

gas_stations = (
    "shell",
    "chevron",
    "mobil",
    "arco",
    "bp",
    "exxon",
    "sunoco",
    "valero",
    "miracle mile" 
)

coffee_companies = (
    'starbucks',
    'dunkin donuts',
    'illy',
    'lavazza',
    'maxwell house',
    'blue bottle',
    'grounds for change',
    'batdorf  bronson',
)

categories = (
    (["return", "returns", "refund"], [], "Refunds/Returns"),
    (["covid"], [], "Covid Related Expenses"),
    (["coffee", "café"], coffee_companies, "Coffee"),
    (restaurant_keywords, restaurants, "Restaurants/Food"),
    (["taxi"], rideshare_services, "Rideshare Services"),
    (["grocery"], grocery_stores, "Grocery Stores"),
    (["convenience"], convenience_stores, "Convenience Stores"),
    (["gas station", "gas"], gas_stations, "Gas Stations")
)

subs = (
    (r'\d{4,}|[^a-zA-Z0-9\sé]+|reimbursement', ""),
    (r"flimtools", "filmtools"),
    (r'sirreel', "sireel")
)
