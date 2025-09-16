# Sandrine.ai — Document Digitization & Translation

**Computer-vision demo for NGOs assisting immigrants, refugees, and asylum seekers.**  
Upload a photo/scan → OCR (Tesseract) → translate text.

- **Public Demo (online translation):** `doc_translator.py`
- **Privacy-First App (offline translation):** `doc_translator_privacy.py` (FR/SW only)

---

## Features

- 📷 Image cleanup (grayscale / threshold / denoise)
- 🧠 OCR via **Tesseract**
- 🌍 Translation
  - **Public demo:** online (Google via `deep-translator`)
  - **Privacy app:** offline **MarianMT** (FR↔EN, SW↔EN)
- 🛡️ **Privacy-first mode:** in-memory processing, no file writes, no content logs

---

## ⚠️ Disclaimer
This tool is provided **for informational and educational support only**.  
It does **not** replace professional **legal, medical, immigration, or certified translation services**.  

- Do not rely on this tool for decisions with legal, medical, or immigration consequences.  
- Always seek help from a qualified professional for official matters.  
- By using this tool, you accept full responsibility for how outputs are applied.  

👉 [Read our full Privacy & Data Handling Policy](./PRIVACY_POLICY.md)

---

## Supported languages (current)

- **OCR:** English, French, Swahili  
- **Translation (public demo):** EN↔FR, EN↔SW  
- **Translation (privacy app):** EN↔FR, EN↔SW  
- **Not available yet:** Portuguese, Lingala  

> UI note: The apps display:  
> _“⚠️ Portuguese and Lingala translation not available yet — only French and Swahili are supported at this time.”_

---

## Requirements

- Python 3.10+ (Windows 10/11 tested)
- Tesseract OCR installed locally (Windows):
  - Download the 64-bit installer (e.g., `tesseract-ocr-w64-setup-5.x.x.exe`)
  - Default path: `C:\Program Files\Tesseract-OCR\tesseract.exe`
  - If needed, set the path in code:
    ```python
    import pytesseract
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    ```

---

## Local setup

```bash
# Clone this repo
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>

# 1) Public demo (online translation)
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run .\doc_translator.py

# 2) Privacy app (offline FR/SW only)
python -m venv .venv_privacy
.\.venv_privacy\Scripts\Activate.ps1
pip install -r requirements_offline.txt
streamlit run .\doc_translator_privacy.py

