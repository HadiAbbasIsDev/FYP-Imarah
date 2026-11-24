# PPIT Assignment 1

Prepared on 27 September 2026 from the assignment brief, FYP proposal and current phase records.

The documents use black text, black table headings and neutral grey row shading. The embedded logo is a black-and-white copy; the original website logo is unchanged. This follows the team's requested colour revision and preserves the approved wording and layout.

## Editable documents

The `documents/` folder contains the three Word files:

1. `23K-0927_23I-0124_23K-0705_Imarah_MOA.docx`
2. `23K-0927_23I-0124_23K-0705_Imarah_AOA.docx`
3. `23K-0927_23I-0124_23K-0705_Imarah_BusinessPlan.docx`

The filenames include all three group members because the brief permits the FYP team structure. If submission is individual, change the filename prefix to the submitting student's ID. No lecturer name or course section was supplied, so neither was invented.

Open the DOCX files in Word or LibreOffice and edit them directly. Paragraphs and tables are editable, headings use Word styles, page numbers are fields, and external references are clickable. The logo is rendered from `frontend/public/icon.svg`. Use Save As or Export to PDF after reviewing your changes. PDF copies used to inspect layout are under the ignored `.runtime/ppit-review/` directory, not the submission folder.

## Proposed details to review

- Legal name: Imarah Technologies (Private) Limited, trading as Imarah.tech. Registration and name approval have not been claimed.
- Office: Karachi, Sindh; street address not yet selected.
- Ownership: one-third per founder, 150 ordinary shares each at PKR 100 per share.
- Project funding: PKR 15,000 per founder over one year, PKR 45,000 total. Monthly instalments of PKR 1,250 each are a planning assumption; receipt of funds is not claimed.
- Authorised capital: PKR 60,000, including 150 unissued shares.
- Founder business roles, pricing, sales targets and budgets are proposals. The documents label them accordingly.
- Signatures remain blank. Do not add signatures on someone else's behalf.

The business plan distinguishes working inspection features from demo modules and planned commercial access controls. It includes all sections A through K required by the brief, source references, a quarterly project-year cash-flow forecast, a separate three-year commercial scenario, break-even and funding-gap checks. No benchmark accuracy or existing customer base is invented.

## Source text and rebuilding

The `sources/` folder holds the text used to generate the documents. `build_documents.py` creates Word files with standard Python ZIP/XML support and Ubuntu's installed Cairo and Rsvg libraries:

```bash
/usr/bin/python3 PPIT-Assignment/build_documents.py
```

Rebuilding overwrites the three generated DOCX files. If you edit Word files directly, keep those edited copies and do not rebuild over them. No project dependency files were changed.

## Review performed

- Matched document coverage to the assignment PDF.
- Checked founders and registration numbers against the FYP proposal.
- Used SECP resources for the corporate-document structure and primary vendor/PBS sources for market context.
- Recalculated financial totals, cash movement, share totals and break-even independently.
- Opened the DOCX files through LibreOffice, exported review PDFs and inspected page layout.
- Checked the documents for em dashes, malformed XML and missing source links.

These are academic proposals. Current filing requirements, founder agreement, university rights and actual supplier prices need confirmation before using them to start a company.

Budget revision: planned equipment is PKR 30,000, other project spending PKR 9,000 and reserve PKR 6,000. The equipment total remains below PKR 50,000. Commercial costs are separate and require additional funding.
