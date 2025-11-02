# credit-card-statement-parser
PDF parser for credit card statements (HDFC, ICICI, SBI, Axis, AmEx)
# 💳 Credit Card Statement Parser

A Python-based PDF parser that extracts key information from credit card statements across 5 major Indian card issuers.

![Python](https://img.shields.io/badge/python-3.7+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

## 🎯 Features

- ✅ Supports 5 major card issuers: HDFC, ICICI, SBI, Axis, American Express
- ✅ Extracts 5 key data points from each statement
- ✅ Batch processing capability
- ✅ JSON output for easy integration
- ✅ Handles multiple date and amount formats

## 📊 Extracted Data Points

1. **Card Issuer** - Bank name identification
2. **Last 4 Digits** - Card number (last 4 digits)
3. **Billing Cycle** - Statement period
4. **Payment Due Date** - When payment is due
5. **Total Amount Due** - Outstanding balance

## 🚀 Quick Start

### Installation
```bash
pip install pdfplumber
```

### Usage

Parse a single statement:
```bash
python cc_parser.py statement.pdf
```

Parse multiple statements:
```bash
python cc_parser.py statements_folder/
```

## 📁 Project Structure
