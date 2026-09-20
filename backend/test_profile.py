import time
from pathlib import Path
from kartikey.document_processing.extractor import extract_text, scan_is_references
from kartikey.analysis.profile_extractor import extract_profile

pdf_path = Path("/Users/kartikeygupta/Desktop/Hackathons/sih_26108/backend/uploads/ef70ec28-66f1-4c99-9134-ef1d069c5877/hindi:english tender.pdf")

t0 = time.time()
text = extract_text(pdf_path)
t1 = time.time()
print(f"extract_text: {t1-t0:.2f}s")

refs = scan_is_references(text)
t2 = time.time()
print(f"scan_is_references: {t2-t1:.2f}s, found {len(refs)}")

prof = extract_profile(text)
t3 = time.time()
print(f"extract_profile: {t3-t2:.2f}s")
