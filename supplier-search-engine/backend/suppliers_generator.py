"""Generate suppliers matching the HTML dashboard data structure."""

import random
from typing import List, Dict, Any


class SeededRandom:
    """Seeded random number generator using seed 1962 (Walmart's founding year)."""
    
    def __init__(self, seed: int = 1962):
        self.seed = seed
        self.rng = random.Random(seed)
    
    def random(self) -> float:
        """Generate a random float between 0 and 1."""
        return self.rng.random()


class SupplierGenerator:
    """Generate suppliers matching the HTML dashboard."""
    
    def __init__(self):
        self.seeded_rng = SeededRandom(1962)
        self.product_categories = {
            "Lumber & Wood Products": ["2x4 Lumber", "Plywood", "Particle Board", "MDF", "Hardwood Flooring", "Cedar Shingles"],
            "Concrete & Masonry": ["Portland Cement", "Ready-Mix Concrete", "Cinder Blocks", "Bricks", "Gravel", "Sand"],
            "Steel & Metal": ["Steel Beams", "Rebar", "Steel Pipe", "Aluminum Siding", "Metal Roofing", "Wire Mesh"],
            "Electrical Supplies": ["Electrical Wire", "Outlets", "Light Fixtures", "Circuit Breakers", "Conduit", "Switches"],
            "Plumbing Supplies": ["PVC Pipe", "Copper Pipe", "Faucets", "Valves", "Toilets", "Sink Fixtures"],
            "HVAC Equipment": ["Air Conditioning Units", "Furnaces", "Heat Pumps", "Ductwork", "Thermostats", "Insulation"],
            "Roofing Materials": ["Asphalt Shingles", "Metal Roofing", "Tar & Gravel", "Underlayment", "Flashing", "Gutters"],
            "Windows & Doors": ["Vinyl Windows", "Wood Doors", "Sliding Glass Doors", "Storm Windows", "Hardware", "Weather Stripping"],
            "Paint & Finishes": ["Interior Paint", "Exterior Paint", "Primer", "Stain", "Polyurethane", "Caulk"],
            "Hardware & Fasteners": ["Nails", "Screws", "Bolts", "Hinges", "Locks", "Tools"]
        }
        
        self.certifications = [
            "ISO 9001", "ISO 14001", "OSHA Certified", "EPA Certified",
            "NSF Certified", "UL Listed", "ANSI Certified", "Green Building",
            "Walmart Supplier Standards", "WBE Certified"
        ]
        
        self.company_sizes = ["Small (1-50)", "Medium (51-250)", "Large (251-1000)", "Enterprise (1000+)"]
        self.price_ranges = ["Budget ($)", "Mid-Range ($$)", "Premium ($$$)", "Enterprise ($$$$)"]
        self.company_types = ['Inc.', 'LLC', 'Corp.', 'Co.', 'Supply Co.', 'Distributors', 'Materials', 'Solutions', 'Industries', 'Group', 'Enterprises', 'Services', 'Systems', 'Technologies']
        self.adjectives = ['Premier', 'Elite', 'Pro', 'Superior', 'Quality', 'Reliable', 'National', 'Metro', 'Coastal', 'Summit', 'Precision', 'BuildRight', 'Apex', 'Pioneer', 'TruValue', 'First Choice', 'Top Tier', 'Allied', 'United', 'Global', 'Platinum', 'Diamond', 'Crown', 'Ace', 'Master', 'Prime', 'Advantage', 'American', 'Industrial', 'Commercial', 'Advanced', 'Superior', 'Dynamic', 'Innovative', 'Strategic', 'Certified', 'Professional', 'Executive', 'Specialist', 'Expert', 'Mega', 'Ultra', 'Super', 'Best', 'Direct', 'Express', 'Rapid', 'Swift', 'Instant', 'Quick']
        
        self.cities = [
            {'city': 'New York', 'state': 'NY', 'region': 'Northeast'},
            {'city': 'Los Angeles', 'state': 'CA', 'region': 'West'},
            {'city': 'Chicago', 'state': 'IL', 'region': 'Midwest'},
            {'city': 'Houston', 'state': 'TX', 'region': 'Southwest'},
            {'city': 'Phoenix', 'state': 'AZ', 'region': 'Southwest'},
            {'city': 'Philadelphia', 'state': 'PA', 'region': 'Northeast'},
            {'city': 'San Antonio', 'state': 'TX', 'region': 'Southwest'},
            {'city': 'San Diego', 'state': 'CA', 'region': 'West'},
            {'city': 'Dallas', 'state': 'TX', 'region': 'Southwest'},
            {'city': 'San Jose', 'state': 'CA', 'region': 'West'},
            {'city': 'Austin', 'state': 'TX', 'region': 'Southwest'},
            {'city': 'Jacksonville', 'state': 'FL', 'region': 'Southeast'},
            {'city': 'Fort Worth', 'state': 'TX', 'region': 'Southwest'},
            {'city': 'Columbus', 'state': 'OH', 'region': 'Midwest'},
            {'city': 'Charlotte', 'state': 'NC', 'region': 'Southeast'},
            {'city': 'Seattle', 'state': 'WA', 'region': 'West'},
            {'city': 'Denver', 'state': 'CO', 'region': 'West'},
            {'city': 'Boston', 'state': 'MA', 'region': 'Northeast'},
            {'city': 'Portland', 'state': 'OR', 'region': 'West'},
            {'city': 'Las Vegas', 'state': 'NV', 'region': 'West'},
            {'city': 'Detroit', 'state': 'MI', 'region': 'Midwest'},
            {'city': 'Memphis', 'state': 'TN', 'region': 'Southeast'},
            {'city': 'Baltimore', 'state': 'MD', 'region': 'Northeast'},
            {'city': 'Milwaukee', 'state': 'WI', 'region': 'Midwest'},
            {'city': 'Atlanta', 'state': 'GA', 'region': 'Southeast'},
            {'city': 'Miami', 'state': 'FL', 'region': 'Southeast'},
            {'city': 'Indianapolis', 'state': 'IN', 'region': 'Midwest'},
            {'city': 'Kansas City', 'state': 'MO', 'region': 'Midwest'},
            {'city': 'Minneapolis', 'state': 'MN', 'region': 'Midwest'},
            {'city': 'Raleigh', 'state': 'NC', 'region': 'Southeast'}
        ]
    
    def generate_suppliers(self) -> List[Dict[str, Any]]:
        """Generate all suppliers using seeded randomness."""
        suppliers = []
        used_names = set()
        
        supplier_id = 1
        for category, products in self.product_categories.items():
            suppliers_per_category = 5000 // len(self.product_categories)
            
            for i in range(suppliers_per_category):
                supplier_name = None
                attempts = 0
                category_short = category.split()[0]
                
                # Generate unique name
                while attempts < 20:
                    adj = self.adjectives[int(self.seeded_rng.random() * len(self.adjectives))]
                    type_suffix = self.company_types[int(self.seeded_rng.random() * len(self.company_types))]
                    supplier_name = f"{adj} {category_short} {type_suffix}"
                    attempts += 1
                    
                    if supplier_name not in used_names:
                        break
                    
                    if attempts > 10:
                        supplier_name = f"{adj} {category_short} {type_suffix} #{int(self.seeded_rng.random() * 999 + 1)}"
                        break
                
                used_names.add(supplier_name)
                city_data = self.cities[int(self.seeded_rng.random() * len(self.cities))]
                
                # Generate products
                num_products = int(self.seeded_rng.random() * 5) + 2
                supplier_products = []
                for _ in range(num_products):
                    prod = products[int(self.seeded_rng.random() * len(products))]
                    if prod not in supplier_products:
                        supplier_products.append(prod)
                
                # Generate certifications
                num_certs = int(self.seeded_rng.random() * 3) + 1
                supplier_certs = []
                for _ in range(num_certs):
                    cert = self.certifications[int(self.seeded_rng.random() * len(self.certifications))]
                    if cert not in supplier_certs:
                        supplier_certs.append(cert)
                
                # Build supplier object
                supplier = {
                    'id': supplier_id,
                    'name': supplier_name,
                    'description': f"Leading provider of {category.lower()} with over {int(self.seeded_rng.random() * 40 + 5)} years of experience. We specialize in delivering high-quality construction materials to commercial and residential projects across the {city_data['region']} region. Our commitment to customer satisfaction and competitive pricing has made us a trusted partner for contractors and builders nationwide.",
                    'website': f"https://www.{adj.lower().replace(' ', '')}{category_short.lower()}.com",
                    'email': f"{['sales', 'info', 'contact', 'support'][int(self.seeded_rng.random() * 4)]}@{adj.lower().replace(' ', '')}{category_short.lower()}.com",
                    'phone': f"({int(self.seeded_rng.random() * 900 + 200)}) {int(self.seeded_rng.random() * 900 + 200)}-{int(self.seeded_rng.random() * 9000 + 1000)}",
                    'address': f"{int(self.seeded_rng.random() * 9000 + 1000)} {['Main', 'Oak', 'Maple', 'Industrial', 'Commerce', 'Market', 'Park', 'Center'][int(self.seeded_rng.random() * 8)]} {['Street', 'Avenue', 'Boulevard', 'Drive', 'Way', 'Road'][int(self.seeded_rng.random() * 6)]}",
                    'city': city_data['city'],
                    'state': city_data['state'],
                    'category': category,
                    'products': supplier_products,
                    'location': f"{city_data['city']}, {city_data['state']}",
                    'region': city_data['region'],
                    'rating': round(self.seeded_rng.random() * 1.5 + 3.5, 1),
                    'aiScore': int(self.seeded_rng.random() * 30 + 70),
                    'certifications': supplier_certs,
                    'size': self.company_sizes[int(self.seeded_rng.random() * len(self.company_sizes))],
                    'priceRange': self.price_ranges[int(self.seeded_rng.random() * len(self.price_ranges))],
                    'yearsInBusiness': int(self.seeded_rng.random() * 40 + 5),
                    'projectsCompleted': int(self.seeded_rng.random() * 5000 + 100),
                    'walmartVerified': self.seeded_rng.random() > 0.7,
                    'employees': int(self.seeded_rng.random() * 900 + 50),
                    'responseTime': f"{int(self.seeded_rng.random() * 24 + 1)} hours",
                    'minOrder': f"${(int(self.seeded_rng.random() * 50 + 10) * 100):,}",
                    'paymentTerms': ['Net 30', 'Net 60', '2/10 Net 30', 'Credit Card', 'COD'][int(self.seeded_rng.random() * 5)]
                }
                
                suppliers.append(supplier)
                supplier_id += 1
        
        return suppliers
