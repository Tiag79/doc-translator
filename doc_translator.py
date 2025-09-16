
# -*- coding: utf-8 -*-
import streamlit as st
import numpy as np
import cv2
import pytesseract
from PIL import Image
from io import BytesIO
from deep_translator import GoogleTranslator
from gtts import gTTS

# If Windows can't find Tesseract, uncomment the next two lines and set the path
# import pytesseract
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

st.set_page_config(page_title="Document Digitization & Translation", page_icon="📑", layout="wide")
st.title("📑 Document Digitization & Translation (Public Demo)")
st.caption("Upload a document → OCR → translate → (optional) download text or audio.")
st.caption("Upload → OCR → translate (online). Supported pairs: EN↔FR, EN↔SW.")
st.caption("⚠️ Portuguese and Lingala translation not available yet — only French and Swahili are supported at this time.")


# ---------- Consent ----------
consent = st.checkbox(
    "✅ I understand this tool does not provide legal, medical, or official translation advice. "
    "I am responsible for how I use the outputs."
)
if not consent:
    st.warning("You must check the box above to continue.")
    st.stop()

# ---------- Sidebar help ----------
with st.sidebar:
    st.header("How to use")
    st.markdown(
        "- Upload a **JPG/PNG** photo/scan of the document.\n"
        "- Set **OCR language** (the language printed on the page).\n"
        "- Choose your **translation target**.\n"
        "- Try **Image cleanup** if the photo is faint or noisy."
    )
    st.divider()
    st.header("Tips")
    st.markdown(
        "- Good lighting, flat page, fill the frame.\n"
        "- For US notices: OCR language = **English (eng)**."
    )

# ---------- Config ----------
OCR_LANGS = {
    "English (eng)": "eng",
    "French (fra)": "fra",
    "Portuguese (por)": "por",
    "Swahili (swa)": "swa",
}
TARGET_LANGS = {
    "English": "en",
    "French / Français": "fr",
    "Portuguese / Português": "pt",
    "Swahili / Kiswahili": "sw",
    "Lingala": "ln",
}

def enhance_image(img_bgr, to_gray=True, do_thresh=False, do_denoise=False):
    work = img_bgr.copy()
    if to_gray:
        work = cv2.cvtColor(work, cv2.COLOR_BGR2GRAY)
    if do_denoise:
        work = cv2.fastNlMeansDenoising(work, h=10)
    if do_thresh:
        work = cv2.adaptiveThreshold(
            work, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 8
        )
    return work

def bytes_from_text(text: str) -> bytes:
    return text.encode("utf-8")

# ---------- UI controls ----------
uploaded = st.file_uploader("Upload a document image (JPG/PNG)", type=["jpg", "jpeg", "png"])

OCR_LANGS = {
    "English (eng)": "eng",
    "French (fra)": "fra",
    "Portuguese (por)": "por",
    "Swahili (swa)": "swa",
}
TARGET_LANGS = {
    "English": "en",
    "French / Français": "fr",
    "Portuguese / Português": "pt",
    "Swahili / Kiswahili": "sw",
    "Lingala": "ln",
}

col1, col2 = st.columns(2)
with col1:
    st.subheader("OCR Settings")
    ocr_lang_label = st.selectbox("OCR language on the page", list(OCR_LANGS.keys()), index=0)
    ocr_lang = OCR_LANGS[ocr_lang_label]

    st.subheader("Image cleanup (optional)")
    use_gray = st.checkbox("Convert to grayscale", value=True)
    use_thresh = st.checkbox("Binarize (adaptive threshold)", value=True)
    use_denoise = st.checkbox("Denoise (camera noise)", value=False)

with col2:
    st.subheader("Translation")
    tgt_label = st.selectbox("Translate into", list(TARGET_LANGS.keys()), index=1)
    target_lang = TARGET_LANGS[tgt_label]
    do_tts = st.checkbox("Generate audio of translation (gTTS)", value=False)

def enhance_image(img_bgr, to_gray=True, do_thresh=False, do_denoise=False):
    work = img_bgr.copy()
    if to_gray:
        work = cv2.cvtColor(work, cv2.COLOR_BGR2GRAY)
    if do_denoise:
        work = cv2.fastNlMeansDenoising(work, h=10)
    if do_thresh:
        work = cv2.adaptiveThreshold(
            work, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 8
        )
    return work

def bytes_from_text(text: str) -> bytes:
    return text.encode("utf-8")

# ---------- Processing ----------
if uploaded is not None:
    # Read image in-memory
    file_bytes = uploaded.getvalue()
    image = Image.open(BytesIO(file_bytes)).convert("RGB")
    img_rgb = np.array(image)
    st.image(img_rgb, caption="Uploaded image", channels="RGB")

    # Preprocess for OCR
    img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
    pre = enhance_image(img_bgr, to_gray=use_gray, do_thresh=use_thresh, do_denoise=use_denoise)

    st.subheader("Preprocessed image (for OCR)")
    if len(pre.shape) == 2:
        st.image(pre, clamp=True, channels="GRAY")
    else:
        show_rgb = cv2.cvtColor(pre, cv2.COLOR_BGR2RGB)
        st.image(show_rgb, channels="RGB")

    # -------- OCR (this is the critical call) --------
    try:
        config = "--oem 3 --psm 6"
        text = pytesseract.image_to_string(pre, lang=ocr_lang, config=config)
    except pytesseract.TesseractError:
        st.error("Tesseract OCR error. Make sure Tesseract and the selected language data are installed.")
        text = ""

    st.subheader("📜 Extracted Text")
    if text.strip():
        st.text_area("OCR result", value=text, height=220)
        st.download_button("Download OCR (.txt)", data=bytes_from_text(text),
                           file_name="ocr_text.txt", mime="text/plain")
    else:
        st.info("No text detected. Try the cleanup options or a clearer photo.")

    # -------- Translation --------
    if text.strip():
        try:
            translator = GoogleTranslator(source="auto", target=target_lang)
            translated = translator.translate(text)
        except Exception as e:
            st.error("Translation failed (network or service issue).")
            st.exception(e)
            translated = ""

        st.subheader("🌍 Translated Text")
        if translated.strip():
            st.text_area("Translation", value=translated, height=220)
            st.download_button("Download translation (.txt)", data=bytes_from_text(translated),
                               file_name="translation.txt", mime="text/plain")
            if do_tts:
                try:
                    tts = gTTS(translated, lang=target_lang)
                    tts_bytes = BytesIO()
                    tts.write_to_fp(tts_bytes)
                    tts_bytes.seek(0)
                    st.audio(tts_bytes, format="audio/mp3")
                    st.download_button("Download audio (.mp3)", data=tts_bytes.getvalue(),
                                       file_name="translation_audio.mp3", mime="audio/mpeg")
                except Exception as e:
                    st.warning("Text-to-speech failed (language voice may be unavailable).")
                    st.exception(e)
        else:
            st.info("No translation produced.")
else:
    st.info("Upload a document image to begin.")
