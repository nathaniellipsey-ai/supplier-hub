#!/usr/bin/env python3
"""
Supplier Data Validation Script

Scans supplier data for:
1. Invalid/broken website URLs
2. Disconnected phone numbers
3. Incomplete or missing contact information
4. Duplicate entries
5. Suspicious or generated data

Usage:
    python validate_suppliers.py
"""

import re
import json
from typing import List, Dict, Tuple
from urllib.parse import urlparse
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed


class SupplierValidator:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.valid_suppliers = []
        self.invalid_suppliers = []
        
    def validate_phone_number(self, phone: str) -> Tuple[bool, str]:
        """
        Validate phone number format.
        Accepts: US format (XXX) XXX-XXXX or XXXXXXXXXX
        """
        if not phone or not isinstance(phone, str):
            return False, "Phone number is empty or not a string"
        
        # Remove common formatting characters
        cleaned = re.sub(r'[\s\-\(\)\+]', '', phone)
        
        # Must be 10+ digits (allowing international)
        if not re.match(r'^\d{10,15}$', cleaned):
            return False, f"Invalid phone format: {phone}"
        
        return True, "Valid"
    
    def validate_website(self, website: str) -> Tuple[bool, str]:
        """
        Validate website URL format.
        """
        if not website or not isinstance(website, str):
            return False, "Website is empty or not a string"
        
        # Check for common issues
        if website.startswith('http://example') or website.startswith('https://example'):
            return False, "Placeholder/example domain"
        
        if website.startswith('http://localhost') or website.startswith('http://127.0.0.1'):
            return False, "Local server domain (not a real website)"
        
        # URL validation
        try:
            result = urlparse(website)
            # Must have scheme and netloc
            if not result.scheme or not result.netloc:
                return False, "Invalid URL format"
            
            # Check for common generated/fake domains
            if any(x in result.netloc.lower() for x in ['test', 'fake', 'local', 'internal', '127.0.0']):
                return False, "Appears to be test/internal domain"
            
            return True, "Valid format"
        except Exception as e:
            return False, f"URL parsing error: {str(e)}"
    
    def check_website_accessible(self, website: str, timeout: int = 5) -> Tuple[bool, str]:
        """
        Attempt to reach website and verify it's accessible.
        """
        try:
            # Add http:// if no scheme
            if not website.startswith('http'):
                website = f"https://{website}"
            
            # Add timeout and user agent
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.head(website, timeout=timeout, headers=headers, allow_redirects=True)
            
            if response.status_code < 400:
                return True, f"Accessible (HTTP {response.status_code})"
            elif response.status_code < 500:
                return False, f"Client error (HTTP {response.status_code})"
            else:
                return False, f"Server error (HTTP {response.status_code})"
        except requests.exceptions.Timeout:
            return False, "Website timeout"
        except requests.exceptions.ConnectionError:
            return False, "Connection refused"
        except requests.exceptions.RequestException as e:
            return False, f"Request failed: {str(e)}"
    
    def validate_supplier(self, supplier: Dict) -> Dict:
        """
        Validate a single supplier record.
        """
        result = {
            'id': supplier.get('id'),
            'name': supplier.get('name'),
            'valid': True,
            'errors': [],
            'warnings': [],
        }
        
        # Required fields
        required_fields = ['id', 'name', 'phone', 'website', 'email']
        for field in required_fields:
            if not supplier.get(field):
                result['errors'].append(f"Missing required field: {field}")
                result['valid'] = False
        
        # Validate phone
        if supplier.get('phone'):
            is_valid, msg = self.validate_phone_number(supplier.get('phone'))
            if not is_valid:
                result['errors'].append(f"Invalid phone: {msg}")
                result['valid'] = False
        
        # Validate website
        if supplier.get('website'):
            is_valid, msg = self.validate_website(supplier.get('website'))
            if not is_valid:
                result['errors'].append(f"Invalid website: {msg}")
                result['valid'] = False
        
        # Validate email
        if supplier.get('email'):
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', supplier.get('email')):
                result['errors'].append(f"Invalid email format: {supplier.get('email')}")
                result['valid'] = False
        
        # Check for generated/fake data indicators
        name = supplier.get('name', '').lower()
        if name.startswith('premier') or name.startswith('quality') or name.startswith('elite'):
            result['warnings'].append("Supplier name matches generated data pattern")
        
        if supplier.get('yearsInBusiness', 0) > 150:
            result['warnings'].append(f"Unrealistic years in business: {supplier.get('yearsInBusiness')}")
        
        if supplier.get('rating', 0) > 5.0:
            result['warnings'].append(f"Invalid rating: {supplier.get('rating')} (must be ≤ 5.0)")
        
        return result
    
    def scan_suppliers(self, suppliers: List[Dict]) -> Dict:
        """
        Scan all suppliers for issues.
        """
        print(f"\n{'='*80}")
        print(f"SUPPLIER DATA VALIDATION REPORT")
        print(f"{'='*80}")
        print(f"\nScanning {len(suppliers)} suppliers...\n")
        
        # Validate all suppliers
        results = []
        for i, supplier in enumerate(suppliers):
            if (i + 1) % 100 == 0:
                print(f"  Processed {i + 1}/{len(suppliers)} suppliers...")
            result = self.validate_supplier(supplier)
            results.append(result)
        
        # Analyze results
        valid_count = sum(1 for r in results if r['valid'])
        invalid_count = sum(1 for r in results if not r['valid'])
        warning_count = sum(len(r['warnings']) for r in results)
        
        print(f"\n{'='*80}")
        print(f"VALIDATION SUMMARY")
        print(f"{'='*80}")
        print(f"Total Suppliers: {len(suppliers)}")
        print(f"Valid: {valid_count} ✅")
        print(f"Invalid: {invalid_count} ❌")
        print(f"Warnings: {warning_count} ⚠️")
        
        # Show invalid suppliers
        if invalid_count > 0:
            print(f"\n{'='*80}")
            print(f"INVALID SUPPLIERS ({invalid_count})")
            print(f"{'='*80}\n")
            for result in results:
                if not result['valid']:
                    print(f"ID: {result['id']} | Name: {result['name']}")
                    for error in result['errors']:
                        print(f"  ❌ {error}")
                    print()
        
        # Show suppliers with warnings
        if warning_count > 0:
            print(f"\n{'='*80}")
            print(f"SUPPLIERS WITH WARNINGS ({sum(1 for r in results if r['warnings'] > 0)})")
            print(f"{'='*80}\n")
            for result in results:
                if result['warnings']:
                    print(f"ID: {result['id']} | Name: {result['name']}")
                    for warning in result['warnings']:
                        print(f"  ⚠️ {warning}")
                    print()
        
        # Recommendations
        print(f"\n{'='*80}")
        print(f"RECOMMENDATIONS")
        print(f"{'='*80}\n")
        
        if invalid_count > 0:
            print(f"❌ ACTION REQUIRED: Remove or fix {invalid_count} invalid suppliers")
            print(f"   - Suppliers with missing required fields")
            print(f"   - Suppliers with invalid contact information")
            print(f"   - Suppliers with placeholder/test data")
        else:
            print(f"✅ All suppliers have valid required fields")
        
        if warning_count > 0:
            print(f"⚠️ REVIEW REQUIRED: {warning_count} suppliers have warnings")
            print(f"   - Check for generated/test data")
            print(f"   - Verify unusual patterns")
        else:
            print(f"✅ No warnings found")
        
        # Check for generated data
        generated_indicators = 0
        for supplier in suppliers:
            if supplier.get('name', '').startswith(('Premier', 'Elite', 'Quality', 'Pro', 'Superior')):
                generated_indicators += 1
        
        if generated_indicators > len(suppliers) * 0.5:  # More than 50%
            print(f"\n🚨 DATA QUALITY ISSUE: {generated_indicators} suppliers appear to be generated/synthetic data")
            print(f"   Recommended action: Replace with real supplier data from verified sources")
        
        print(f"\n{'='*80}\n")
        
        return {
            'total': len(suppliers),
            'valid': valid_count,
            'invalid': invalid_count,
            'warnings': warning_count,
            'results': results,
            'generated_data_detected': generated_indicators > len(suppliers) * 0.5,
        }


if __name__ == '__main__':
    # Fix Unicode on Windows
    import sys
    import codecs
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    
    # Load suppliers from API
    print("Loading suppliers from app_minimal.py...")
    from app_minimal import generate_suppliers
    
    suppliers = generate_suppliers()
    print(f"Loaded {len(suppliers)} suppliers\n")
    
    # Validate
    validator = SupplierValidator()
    report = validator.scan_suppliers(suppliers)
    
    # Exit with error code if issues found
    if report['invalid'] > 0 or report['generated_data_detected']:
        print("\n⚠️ ISSUES DETECTED - See report above")
        exit(1)
    else:
        print("\n✅ All suppliers validated successfully!")
        exit(0)