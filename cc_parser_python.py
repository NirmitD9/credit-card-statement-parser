

import re
import json
from datetime import datetime
from pathlib import Path
import sys

try:
    import pdfplumber
except ImportError:
    print("Error: pdfplumber not installed. Install with: pip install pdfplumber")
    sys.exit(1)


class CreditCardParser:
    """Parser for extracting data from credit card statements"""
    
    # Supported card issuers and their patterns
    ISSUERS = {
        'HDFC': r'HDFC\s*Bank',
        'ICICI': r'ICICI\s*Bank',
        'SBI': r'SBI\s*Card|State\s*Bank',
        'AXIS': r'Axis\s*Bank',
        'AMEX': r'American\s*Express|AMEX'
    }
    
    def __init__(self, pdf_path):
        """Initialize parser with PDF file path"""
        self.pdf_path = Path(pdf_path)
        self.text = ""
        self.data = {
            'card_issuer': None,
            'last_4_digits': None,
            'billing_cycle': None,
            'due_date': None,
            'total_due': None
        }
    
    def extract_text(self):
        """Extract text from PDF using pdfplumber"""
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                text_parts = []
                for page in pdf.pages:
                    text_parts.append(page.extract_text())
                self.text = '\n'.join(text_parts)
            return True
        except Exception as e:
            print(f"Error reading PDF: {e}")
            return False
    
    def detect_issuer(self):
        """Detect which card issuer the statement is from"""
        for issuer, pattern in self.ISSUERS.items():
            if re.search(pattern, self.text, re.IGNORECASE):
                self.data['card_issuer'] = issuer
                return issuer
        self.data['card_issuer'] = 'UNKNOWN'
        return None
    
    def extract_last_4_digits(self):
        """Extract last 4 digits of card number"""
        patterns = [
            r'Card\s*(?:Number|No\.?)[\s:]*(?:XXXX|xxxx|\*{4}|\*{12})[\s-]*(\d{4})',
            r'(?:XXXX|xxxx|\*{4}|\*{12})[\s-]*(\d{4})',
            r'Card\s*ending\s*(?:in|with)[\s:]*(\d{4})',
            r'(?:Primary|Credit)\s*Card[\s:]*(?:XXXX|xxxx|\*{4})[\s-]*(\d{4})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.text, re.IGNORECASE)
            if match:
                self.data['last_4_digits'] = match.group(1)
                return match.group(1)
        
        self.data['last_4_digits'] = 'Not Found'
        return None
    
    def extract_billing_cycle(self):
        """Extract billing cycle dates"""
        patterns = [
            r'(?:Billing\s*(?:Cycle|Period|Date)[\s:]*)?(\d{1,2}[-/]\w{3}[-/]\d{2,4})\s*(?:to|–|-|through)\s*(\d{1,2}[-/]\w{3}[-/]\d{2,4})',
            r'Statement\s*(?:Period|Date)[\s:]*(\d{1,2}[-/]\w{3}[-/]\d{2,4})\s*(?:to|–|-)\s*(\d{1,2}[-/]\w{3}[-/]\d{2,4})',
            r'From[\s:]*(\d{1,2}[-/]\w{3}[-/]\d{2,4})\s*To[\s:]*(\d{1,2}[-/]\w{3}[-/]\d{2,4})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.text, re.IGNORECASE)
            if match:
                cycle = f"{match.group(1)} to {match.group(2)}"
                self.data['billing_cycle'] = cycle
                return cycle
        
        self.data['billing_cycle'] = 'Not Found'
        return None
    
    def extract_due_date(self):
        """Extract payment due date"""
        patterns = [
            r'(?:Payment\s*)?Due\s*(?:Date|By|On)[\s:]*(\d{1,2}[-/]\w{3,}[-/]\d{2,4})',
            r'Pay\s*(?:By|Before)[\s:]*(\d{1,2}[-/]\w{3,}[-/]\d{2,4})',
            r'Due\s*Date[\s:]*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.text, re.IGNORECASE)
            if match:
                self.data['due_date'] = match.group(1)
                return match.group(1)
        
        self.data['due_date'] = 'Not Found'
        return None
    
    def extract_total_due(self):
        """Extract total amount due"""
        patterns = [
            r'(?:Total\s*(?:Amount\s*)?Due|Amount\s*Payable|Total\s*Balance\s*Due)[\s:]*(?:Rs\.?|INR|₹)?\s*([\d,]+\.?\d*)',
            r'(?:Minimum\s*)?Amount\s*Due[\s:]*(?:Rs\.?|INR|₹)?\s*([\d,]+\.?\d*)',
            r'(?:Outstanding|Payable)\s*(?:Amount|Balance)[\s:]*(?:Rs\.?|INR|₹)?\s*([\d,]+\.?\d*)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.text, re.IGNORECASE)
            if match:
                amount = match.group(1).replace(',', '')
                self.data['total_due'] = f"₹{amount}"
                return amount
        
        self.data['total_due'] = 'Not Found'
        return None
    
    def parse(self):
        """Main parsing method - extracts all data points"""
        print(f"\n{'='*60}")
        print(f"Parsing: {self.pdf_path.name}")
        print(f"{'='*60}\n")
        
        # Extract text from PDF
        if not self.extract_text():
            return None
        
        print(f"✓ Extracted text from PDF ({len(self.text)} characters)")
        
        # Extract all data points
        print("\nExtracting data points...")
        self.detect_issuer()
        print(f"  1. Card Issuer: {self.data['card_issuer']}")
        
        self.extract_last_4_digits()
        print(f"  2. Last 4 Digits: {self.data['last_4_digits']}")
        
        self.extract_billing_cycle()
        print(f"  3. Billing Cycle: {self.data['billing_cycle']}")
        
        self.extract_due_date()
        print(f"  4. Due Date: {self.data['due_date']}")
        
        self.extract_total_due()
        print(f"  5. Total Due: {self.data['total_due']}")
        
        return self.data
    
    def save_json(self, output_path=None):
        """Save extracted data to JSON file"""
        if output_path is None:
            output_path = self.pdf_path.with_suffix('.json')
        
        with open(output_path, 'w') as f:
            json.dump(self.data, f, indent=2)
        
        print(f"\n✓ Saved results to: {output_path}")
        return output_path


def parse_multiple_statements(pdf_directory):
    """Parse all PDF files in a directory"""
    pdf_dir = Path(pdf_directory)
    pdf_files = list(pdf_dir.glob('*.pdf'))
    
    if not pdf_files:
        print(f"No PDF files found in {pdf_directory}")
        return
    
    print(f"\nFound {len(pdf_files)} PDF statement(s)")
    
    results = []
    for pdf_file in pdf_files:
        parser = CreditCardParser(pdf_file)
        data = parser.parse()
        if data:
            results.append({
                'filename': pdf_file.name,
                'data': data
            })
            parser.save_json()
    
    # Save summary
    summary_path = pdf_dir / 'parsing_summary.json'
    with open(summary_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n{'='*60}")
    print(f"Parsing Complete! Summary saved to: {summary_path}")
    print(f"{'='*60}")


def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python cc_parser.py <pdf_file>           # Parse single file")
        print("  python cc_parser.py <directory>          # Parse all PDFs in directory")
        return
    
    path = Path(sys.argv[1])
    
    if path.is_file() and path.suffix.lower() == '.pdf':
        # Parse single file
        parser = CreditCardParser(path)
        data = parser.parse()
        if data:
            parser.save_json()
            print("\n✓ Parsing successful!")
    
    elif path.is_dir():
        # Parse directory
        parse_multiple_statements(path)
    
    else:
        print(f"Error: {path} is not a valid PDF file or directory")


if __name__ == "__main__":
    main()