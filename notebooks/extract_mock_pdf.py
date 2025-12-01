from pathlib import Path

import pymupdf

ORIGINAL_PDF_PATH = Path("data/mock/Tesco AR 25.pdf")

pages = [
    # Sales increased by 4%
    # Profit increased by 10.9%
    # Cashflow decreased by 3%
    21,
    # Capex increased by 10.9%
    26,
    # Net Debt / Ebitda from 2.2 to 2.0
    30,
]

EXTRACTED_PAGES_PATH = ORIGINAL_PDF_PATH.parent / "Tesco AR report extracted.pdf"

# Open the source PDF
doc = pymupdf.open(ORIGINAL_PDF_PATH)

# Create a new PDF with selected pages
new_doc = pymupdf.open()

for page_num in pages:
    page = doc[page_num - 1]  # pymupdf uses 0-based indexing
    new_doc.insert_pdf(doc, from_page=page_num - 1, to_page=page_num - 1)

# Save the new PDF
new_doc.save(EXTRACTED_PAGES_PATH)

# Close documents
doc.close()
new_doc.close()
