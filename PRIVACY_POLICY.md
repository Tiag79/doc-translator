
---

# 📄 `PRIVACY_POLICY.md`

```markdown
# Privacy & Data Handling Policy

_Last updated: September 2025_

## Purpose
This project is a **demo application** to explore how NGOs might use AI for document digitization and translation.  
It is **not** a certified translation service, and it does **not** replace professional legal, medical, or immigration guidance.

---

## Data Processing

- **In-memory only (privacy app):**  
  Uploaded documents are processed entirely in system RAM.  
  No files are written to disk, unless the user explicitly downloads results.

- **No logging:**  
  Document text is not logged, stored, or transmitted in the privacy app.

- **Public demo (`doc_translator.py`):**  
  Uses online translation via Google (through `deep-translator`).  
  This means extracted text is sent to external APIs for translation.  
  👉 **Do not upload sensitive or personal documents to the public demo.**

---

## Supported Languages

- **OCR:** English, French, Swahili  
- **Offline translation (privacy app):** EN ↔ FR, EN ↔ SW  
- **Online translation (public demo):** EN ↔ FR, EN ↔ SW  
- **Not supported yet:** Portuguese, Lingala

---

## User Responsibility

- This tool is provided **as-is** for informational and educational purposes.  
- It does **not** replace professional **legal, medical, immigration, or certified translation services**.  
- NGOs and individuals remain fully responsible for how outputs are used.  
- Sensitive, personal, or legally significant documents should **not** be processed with this demo.  

---

## Recommendations

- For **official translations**, use a certified translator.  
- For **legal/immigration advice**, consult a licensed professional.  
- For **medical documents**, seek a qualified healthcare provider.  

---

## Liability

The project maintainers are **not liable** for any direct, indirect, or consequential damages resulting from the use of this tool.  
Use of this tool implies acceptance of this policy.

---

## License Reference

This project is released under a **Responsible MIT License**.  
Users must review the [LICENSE](./LICENSE) file for details before use.


