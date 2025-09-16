
# Document Digitization & Translation — Public Demo + Privacy-First

This repository contains **two Streamlit apps** designed to help NGOs and immigrant-serving organizations digitize and translate documents.

---

## ⚠️ Disclaimer
This tool is provided **for informational support only**.  
It does **not** replace professional legal, medical, or certified translation services.  
By using this tool, you accept responsibility for how outputs are used.  
👉 [Read our full Privacy & Data Handling Policy](./PRIVACY_POLICY.md)

---

## 📑 Apps Included

### 1. Public Demo App (`doc_translator.py`)
- Lightweight, easy to deploy (e.g., Streamlit Cloud)
- Uses online translation (`deep-translator` + Google services)
- Best for **non-sensitive documents** (e.g., flyers, school notices)

**Run locally (Windows PowerShell):**
```powershell
cd "C:\path\to\doc-translator"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run .\doc_translator.py
```

---

### 2. Privacy-First App (`doc_translator_privacy.py`)
- Processes documents **in memory only** (no storage, no logs)
- Adds a **consent checkbox** before uploading
- Supports **offline translation** (French, Portuguese, Swahili via MarianMT)
- Lingala available **only in online mode** (disabled by default)

**Run locally (Windows PowerShell):**
```powershell
cd "C:\path\to\doc-translator"
python -m venv .venv_privacy
.\.venv_privacy\Scripts\Activate.ps1
pip install -r requirements_offline.txt
streamlit run .\doc_translator_privacy.py
```

---

## 🌐 Deployment

### Streamlit Cloud (for the public demo)
1. Push your repo to GitHub.  
2. Include `packages.txt` in the repo root (installs Tesseract + language packs).  
3. Deploy via [https://streamlit.io/cloud](https://streamlit.io/cloud).  

### Self-Hosting (recommended for NGOs with sensitive docs)
- Run the **privacy-first app** locally or on a secure server.  
- Use **HTTPS + access control** if deployed online.  

---

## 🛡️ Privacy & Security

- Documents processed **in memory** only.  
- **No storage, no logging.**  
- Users must **check a consent box** before uploading.  
- Two clear modes:  
  - Privacy Mode → Offline translation only (FR/PT/SW)  
  - Online Mode → Optional, but text may leave device  

👉 [Read our full Privacy & Data Handling Policy](./PRIVACY_POLICY.md)

---

## 🙌 Credits
Built by **Sandrine Mujinga (Sandrine.ai)** to empower NGOs and immigrant communities with responsible AI tools.
