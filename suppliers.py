#!/usr/bin/env python3
"""Seeded supplier data generator.

Generates consistent supplier data using seed 1962 (Walmart's founding year).
Every run produces the SAME suppliers - perfect for demos and testing.
"""

import random
from typing import List, Dict, Any


class SupplierGenerator:
    """Generates consistent supplier data using seeded randomness."""
    
    SEED = 1962  # Walmart founding year
    
    def __init__(self):
        self.rng = random.Random(self.SEED)
        self.product_categories = {
            "Lumber & Wood Products": [
                "2x4 Lumber", "Plywood", "Particle Board", "MDF", "Hardwood Flooring",
                "Pressure Treated Wood", "Composite Decking", "Cedar Shingles"
            ],
            "Concrete & Masonry": [
                "Portland Cement", "Ready-Mix Concrete", "Cinder Blocks", "Bricks",
                "Concrete Pavers", "Retaining Wall Blocks", "Mortar Mix", "Concrete Sealers"
            ],
            "Steel & Metal": [
                "Steel Beams", "Rebar", "Steel Pipe", "Aluminum Siding", "Corrugated Metal",
                "Steel Roofing", "Metal Studs", "Angle Iron"
            ],
            "Electrical Supplies": [
                "Electrical Wire", "Outlets", "Light Fixtures", "Circuit Breakers",
                "Conduit", "Switch Plates", "Transformers", "Panel Boards"
            ],
            "Plumbing Supplies": [
                "PVC Pipe", "Copper Pipe", "Faucets", "Valves", "Shut-Off Valves",
                "Water Heaters", "Drain Cleanout", "Plumbing Fixtures"
            ],
            "HVAC Equipment": [
                "Air Conditioning Units", "Furnaces", "Heat Pumps", "Ductwork",
                "Thermostats", "Refrigerant", "HVAC Filters", "Compressors"
            ],
            "Roofing Materials": [
                "Asphalt Shingles", "Metal Roofing", "Tar & Gravel", "Roof Underlayment",
                "Ridge Caps", "Roof Vents", "Flashing", "Roofing Nails"
            ],
            "Windows & Doors": [
                "Vinyl Windows", "Wood Doors", "Sliding Glass Doors", "Garage Doors",
                "Exterior Doors", "Interior Doors", "Window Frames", "Door Hinges"
            ],
            "Paint & Finishes": [
                "Interior Paint", "Exterior Paint", "Primer", "Stain", "Polyurethane",
                "Epoxy Paint", "Sealers", "Paint Thinner"
            ],
            "Hardware & Fasteners": [
                "Nails", "Screws", "Bolts", "Anchors", "Hinges", "Latches",
                "Handles", "Brackets"
            ]
        }
        
        self.regions = [
            "Northeast", "Southeast", "Midwest", "Southwest", "West Coast",
            "Pacific", "Mountain", "Great Plains", "South Central"
        ]
        
        self.certifications = [
            "ISO 9001", "ISO 14001", "OSHA Certified", "EPA Certified",
            "UL Listed", "CSA Certified", "NSF Certified", "LEED Certified",
            "RoHS Compliant", "ITAR Registered"
        ]
    
    def generate_suppliers(self, count: int = 500) -> List[Dict[str, Any]]:
        """Generate suppliers with seeded randomness."""
        suppliers = []
        
        company_prefixes = [
            "Advanced", "Allied", "American", "Anderson", "Austin", "Baker",
            "Benson", "Best", "Big", "Blue", "Border", "Bradford", "Bright",
            "Bristol", "Brown", "Builders", "Capital", "Cardinal", "Central",
            "Century", "Champion", "Coastal", "Columbia", "Commercial", "Complete",
            "Consolidated", "Construction", "Continental", "Cooper", "Cornerstone",
            "Corporate", "Craftsman", "Creative", "Crown", "Crystal", "Custom",
            "Dakota", "Dayton", "Delta", "Denver", "Diamond", "Diversified",
            "East", "Eastern", "Economy", "Electrical", "Elite", "Emery",
            "Empire", "Enterprise", "Epic", "Essential", "Estelle", "Eternal",
            "Evergreen", "Excellence", "Excellent", "Executive", "Expo", "Express"
        ]
        
        company_suffixes = [
            "Supply", "Supplies", "Company", "Corporation", "Industries", "Inc",
            "LLC", "Materials", "Group", "Distributors", "Traders", "Wholesale",
            "Retail", "Sales", "Services", "Solutions", "Systems", "Tech",
            "Technologies", "Tools", "Trade", "Trading", "Works", "Workshop"
        ]
        
        for i in range(count):
            prefix = company_prefixes[self.rng.randint(0, len(company_prefixes) - 1)]
            suffix = company_suffixes[self.rng.randint(0, len(company_suffixes) - 1)]
            name = f"{prefix} {suffix}"
            
            category = self.rng.choice(list(self.product_categories.keys()))
            products = self.rng.sample(
                self.product_categories[category],
                k=self.rng.randint(2, 5)
            )
            
            region = self.rng.choice(self.regions)
            
            certifications = self.rng.sample(
                self.certifications,
                k=self.rng.randint(0, 3)
            )
            
            # Consistent data generation
            rating = round(self.rng.uniform(2.5, 5.0), 1)
            ai_score = self.rng.randint(65, 98)
            employee_count = self.rng.choice([10, 25, 50, 100, 250, 500, 1000, 5000])
            year_founded = self.rng.randint(1950, 2020)
            verified = self.rng.random() < 0.3  # 30% verified
            
            suppliers.append({
                "id": i + 1,
                "name": name,
                "category": category,
                "region": region,
                "location": f"{self.rng.choice(['Cleveland', 'Memphis', 'Des Moines', 'Austin', 'Portland', 'Denver', 'Phoenix', 'Atlanta', 'Chicago', 'Dallas'])}, {region}",
                "rating": rating,
                "aiScore": ai_score,
                "products": products,
                "certifications": certifications,
                "employeeCount": employee_count,
                "yearFounded": year_founded,
                "verified": verified,
                "description": f"Leading supplier of {', '.join(products[:2])} with {employee_count} employees since {year_founded}."
            })
        
        return suppliers


if __name__ == "__main__":
    gen = SupplierGenerator()
    suppliers = gen.generate_suppliers(5)
    for s in suppliers:
        print(f"✓ {s['name']} ({s['category']}) - {s['aiScore']} AI Score")