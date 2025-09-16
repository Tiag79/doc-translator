# -*- coding: utf-8 -*-
import os   # 👈 add this
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"   # 👈 add this line

import streamlit as st
import numpy as np
import cv2
import pytesseract
from PIL import Image
from io import BytesIO
import gc

# --- Torch version check ---
try:
    import torch
    if not torch.__version__.startswith("2.3.1"):
        st.warning(
            f"⚠️ Torch version {torch.__version__} detected. "
            "For stability on Windows, please use torch==2.3.1 (CPU build)."
        )
except ImportError:
    st.error("❌ Torch is not installed in this environment. Run: pip install torch==2.3.1")


# If Windows can't find Tesseract automatically, set the path:
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Offline translation (MarianMT)
from transformers import MarianMTModel, MarianTokenizer

st.set_page_config(page_title="Doc Translator — Privacy Mode", page_icon="🛡️", layout="wide")
st.title("🛡️ Document Digitization & Translation (Privacy-First)")
st.caption("All processing in memory • No file storage • No content logs")
st.caption("All processing in memory • No file storage • Offline MarianMT for French/Swahili only")
st.caption("⚠️ Portuguese and Lingala translation not available yet — only French and Swahili are supported at this time.")


# --------- Consent gate ----------
consent = st.checkbox(
    "✅ I understand this tool does not provide legal, medical, or official translation advice. "
    "I am responsible for how I use the outputs."
)
if not consent:
    st.warning("You must check the box above to continue.")
    st.stop()

with st.sidebar:
    st.header("Privacy Controls")
    privacy_mode = st.toggle(
        "Enable Privacy Mode (offline translation)",
        value=True,
        help="Offline MarianMT for French/Portuguese/Swahili. Lingala is disabled in Privacy Mode."
    )
    st.markdown("- Data is processed **in memory only**.")
    st.markdown("- We do **not** store files or log document content.")
    if st.button("Clear All", type="primary"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        gc.collect()
        st.success("All in-memory data cleared.")

    st.divider()
    st.header("OCR Settings")
    OCR_LANGS = {
        "English (eng)": "eng",
        "French (fra)": "fra",
        "Portuguese (por)": "por",
        "Swahili (swa)": "swa",
    }
    ocr_lang_label = st.selectbox("OCR language printed on the page", list(OCR_LANGS.keys()), index=0)
    ocr_lang = OCR_LANGS[ocr_lang_label]

    st.subheader("Image cleanup (optional)")
    use_gray = st.checkbox("Convert to grayscale", value=True)
    use_thresh = st.checkbox("Binarize (adaptive threshold)", value=True)
    use_denoise = st.checkbox("Denoise (camera noise)", value=False)

# Map OCR langs -> ISO2 for MarianMT models
ISO2_FROM_OCR = {"eng": "en", "fra": "fr", "por": "pt", "swa": "sw"}
OFFLINE_TARGETS = {
    "French / Français": "fr",
    "Portuguese / Português": "pt",
    "Swahili / Kiswahili": "sw",
}
ONLINE_ONLY = {"Lingala": "ln"}  # no MarianMT pair we can rely on

if privacy_mode:
    target_label = st.selectbox("Translate into", list(OFFLINE_TARGETS.keys()), index=0)
    target_iso2 = OFFLINE_TARGETS[target_label]
else:
    all_targets = dict(**OFFLINE_TARGETS, **ONLINE_ONLY)
    target_label = st.selectbox("Translate into", list(all_targets.keys()), index=0)
    target_iso2 = all_targets[target_label]

if privacy_mode:
    st.info("🔒 Privacy Mode is ON: translation is **offline** via MarianMT for FR/PT/SW. Lingala is disabled.")
else:
    st.warning("🌐 Privacy Mode is OFF: translation may use online services; text may leave this device.")

def enhance_image(img_bgr, to_gray=True, do_thresh=False, do_denoise=False):
    work = img_bgr.copy()
    if to_gray:
        work = cv2.cvtColor(work, cv2.COLOR_BGR2GRAY)
    if do_denoise:
        work = cv2.fastNlMeansDenoising(work, h=10)
    if do_thresh:
        work = cv2.adaptiveThreshold(work, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                     cv2.THRESH_BINARY, 31, 8)
    return work
# --- Robust Marian model resolver for specific pairs ---
PAIR_TO_MODEL = {
    ("en", "fr"): "Helsinki-NLP/opus-mt-en-fr",
    ("fr", "en"): "Helsinki-NLP/opus-mt-fr-en",
    ("en", "pt"): "Helsinki-NLP/opus-mt-en-pt",
    ("pt", "en"): "Helsinki-NLP/opus-mt-pt-en",
    ("en", "sw"): "Helsinki-NLP/opus-mt-en-sw",
    ("sw", "en"): "Helsinki-NLP/opus-mt-sw-en",
}

FALLBACK_BY_SRC = {
    "en": ["Helsinki-NLP/opus-mt-en-ROMANCE"],
    "fr": ["Helsinki-NLP/opus-mt-ROMANCE-en"],
    "pt": ["Helsinki-NLP/opus-mt-ROMANCE-en"],
    "sw": [],
}

@st.cache_resource(show_spinner=False)
def load_marian_model(src_iso2: str, tgt_iso2: str):
    from transformers import MarianMTModel, MarianTokenizer

    model_id = PAIR_TO_MODEL.get((src_iso2, tgt_iso2))
    tried = []
    if model_id:
        tried.append(model_id)
        try:
            tok = MarianTokenizer.from_pretrained(model_id)
            model = MarianMTModel.from_pretrained(model_id)
            return tok, model, model_id
        except Exception:
            pass

    generic_id = f"Helsinki-NLP/opus-mt-{src_iso2}-{tgt_iso2}"
    if generic_id not in tried:
        tried.append(generic_id)
        try:
            tok = MarianTokenizer.from_pretrained(generic_id)
            model = MarianMTModel.from_pretrained(generic_id)
            return tok, model, generic_id
        except Exception:
            pass

    for fb in FALLBACK_BY_SRC.get(src_iso2, []):
        if fb not in tried:
            tried.append(fb)
            try:
                tok = MarianTokenizer.from_pretrained(fb)
                model = MarianMTModel.from_pretrained(fb)
                return tok, model, fb
            except Exception:
                pass

    raise OSError(
        f"Could not load a MarianMT model for {src_iso2}->{tgt_iso2}. "
        f"Tried: {', '.join(tried)}."
    )

def offline_translate_with_marian(text: str, src_iso2: str, tgt_iso2: str) -> str:
    if not text.strip() or src_iso2 == tgt_iso2:
        return text
    tok, model, used_id = load_marian_model(src_iso2, tgt_iso2)
    batch = tok([text], return_tensors="pt", truncation=True)
    gen = model.generate(**batch, max_new_tokens=1024)
    return tok.decode(gen[0], skip_special_tokens=True)


uploaded = st.file_uploader("Upload a document image (JPG/PNG)", type=["jpg", "jpeg", "png"])

if uploaded is not None:
    # In-memory bytes only
    file_bytes = uploaded.getvalue()
    image = Image.open(BytesIO(file_bytes)).convert("RGB")
    img_rgb = np.array(image)
    st.image(img_rgb, caption="Uploaded image", channels="RGB", use_column_width=True)

    # Preprocess for OCR
    img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
    pre = enhance_image(img_bgr, to_gray=use_gray, do_thresh=use_thresh, do_denoise=use_denoise)

    st.subheader("Preprocessed image (for OCR)")
    if len(pre.shape) == 2:
        st.image(pre, clamp=True, channels="GRAY", use_column_width=True)
    else:
        show_rgb = cv2.cvtColor(pre, cv2.COLOR_BGR2RGB)
        st.image(show_rgb, channels="RGB", use_column_width=True)

    # OCR
    try:
        config = "--oem 3 --psm 6"
        text = pytesseract.image_to_string(pre, lang=ocr_lang, config=config)
    except pytesseract.TesseractError:
        st.error("Tesseract OCR error. Ensure Tesseract and selected language data are installed.")
        st.stop()

    st.subheader("📜 Extracted Text")
    st.text_area("OCR result (in-memory only, not saved)", value=text, height=220)

    # Determine source ISO code from OCR setting
    src_iso2 = ISO2_FROM_OCR.get(ocr_lang, "en")

    # Translate
    if privacy_mode:
        with st.spinner("Translating offline with MarianMT… (first run may take longer)"):
            try:
                translated = offline_translate_with_marian(text, src_iso2, target_iso2)
            except Exception as e:
                st.error("Offline translation failed. Try another language pair or disable Privacy Mode.")
                st.exception(e)
                translated = ""
    else:
        # Online translation path for languages not supported offline (e.g., Lingala)
        try:
            from deep_translator import GoogleTranslator
            translator = GoogleTranslator(source="auto", target=target_iso2)
            translated = translator.translate(text)
        except Exception as e:
            st.error("Online translation failed (network/service).")
            st.exception(e)
            translated = ""

    st.subheader("🌍 Translated Text")
    st.text_area("Translation (in-memory only, not saved)", value=translated, height=220)

    # Proactive cleanup button
    if st.button("Clear This Document Now"):
        try:
            del file_bytes, image, img_rgb, img_bgr, pre, text, translated
        except Exception:
            pass
        gc.collect()
        st.success("Cleared from memory. You may upload a new document.")
else:
    st.info("Upload a document image to begin. We do not store files or log content.")
