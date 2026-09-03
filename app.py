import os
# --- Force TensorFlow to use legacy Keras mode for DeepFace ---
os.environ["TF_USE_LEGACY_KERAS"] = "1"

import streamlit as st
import numpy as np
from PIL import Image
import hashlib
import hmac
import json
from io import BytesIO
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.request import Request, urlopen

# --- Page Config ---
st.set_page_config(page_title="Age Verification Technologies", layout="wide", page_icon="🛡️")

title_col, github_col, qr_col = st.columns([6, 3, 1], vertical_alignment="center")
with title_col:
    st.title("🛡️ Age Verification Technologies")
with github_col:
    st.markdown(
        """
        <a href="https://github.com/oscar-ryley/age-verification"
           aria-label="Open oscar-ryley/age-verification on GitHub"
           title="oscar-ryley/age-verification"
           style="display:inline-flex; align-items:center; justify-content:center; gap:8px; padding:8px 12px; border:1px solid #d0d7de; border-radius:6px; color:#ffffff; text-decoration:none; white-space:nowrap;">
            <svg viewBox="0 0 16 16" width="24" height="24" aria-hidden="true" fill="currentColor">
                <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.03.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.09.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0 0 16 8c0-4.42-3.58-8-8-8z"></path>
            </svg>
            <span>/oscar-ryley/age-verification</span>
        </a>
        """,
        unsafe_allow_html=True,
    )
with qr_col:
    import qrcode

    qr = qrcode.make("https://age.oryley.com")
    qr_buffer = BytesIO()
    qr.save(qr_buffer, format="PNG")
    st.image(qr_buffer.getvalue(), caption="Open age.oryley.com", width=110)

if "dark_mode" not in st.session_state:
    st.session_state["dark_mode"] = True

if st.button(
    "Switch to light mode" if st.session_state["dark_mode"] else "Switch to dark mode",
    key="theme_toggle",
):
    st.session_state["dark_mode"] = not st.session_state["dark_mode"]
    st.rerun()

if st.session_state["dark_mode"]:
    theme_css = """
    <style>
    :root { color-scheme: dark !important; }
    html, body, [data-testid="stAppViewContainer"],
    [data-testid="stAppViewContainer"] > .main, [data-testid="stHeader"] {
        background-color: #111827 !important;
    }
    [data-testid="stAppViewContainer"] *, [data-testid="stHeader"] * {
        color: #f9fafb !important;
        border-color: #374151;
    }
    [data-testid="stTextInput"] input, [data-testid="stNumberInput"] input,
    [data-testid="stTextArea"] textarea, [data-testid="stFileUploader"] section,
    [data-baseweb="select"] > div {
        background-color: #1f2937 !important;
        color: #f9fafb !important;
    }
    [data-baseweb="popover"], [data-baseweb="menu"],
    [role="listbox"], [role="option"] {
        background-color: #1f2937 !important;
        color: #f9fafb !important;
    }
    [data-testid="stCodeBlock"], [data-testid="stCodeBlock"] *,
    pre, pre *, code, code * {
        background-color: #1f2937 !important;
        color: #f9fafb !important;
    }
    button, [data-testid="stBaseButton-secondary"] {
        background-color: #374151 !important;
        color: #f9fafb !important;
        border-color: #6b7280 !important;
    }
    [data-testid="stTabs"] [role="tablist"] { border-color: #374151 !important; }
    </style>
    """
else:
    theme_css = """
    <style>
    :root { color-scheme: light !important; }
    html, body, [data-testid="stAppViewContainer"],
    [data-testid="stAppViewContainer"] > .main, [data-testid="stHeader"] {
        background-color: #ffffff !important;
    }
    [data-testid="stAppViewContainer"] *, [data-testid="stHeader"] * {
        color: #111827 !important;
        border-color: #d1d5db;
    }
    [data-testid="stTextInput"] input, [data-testid="stNumberInput"] input,
    [data-testid="stTextArea"] textarea, [data-testid="stFileUploader"] section,
    [data-baseweb="select"] > div {
        background-color: #ffffff !important;
        color: #111827 !important;
    }
    [data-baseweb="popover"], [data-baseweb="menu"],
    [role="listbox"], [role="option"] {
        background-color: #ffffff !important;
        color: #111827 !important;
    }
    [data-testid="stCodeBlock"], [data-testid="stCodeBlock"] *,
    pre, pre *, code, code * {
        background-color: #f3f4f6 !important;
        color: #111827 !important;
    }
    button, [data-testid="stBaseButton-secondary"] {
        background-color: #f3f4f6 !important;
        color: #111827 !important;
        border-color: #d1d5db !important;
    }
    [data-testid="stTabs"] [role="tablist"] { border-color: #d1d5db !important; }
    </style>
    """

st.markdown(theme_css, unsafe_allow_html=True)

st.markdown("""
This application demonstrates the seven age-check methods described in Ofcom's guidance.
It shows local processing for facial and document checks, plus the consent, token, and verification steps used by external providers.
""")

# --- Caching the ML Model ---
@st.cache_resource
def load_deepface():
    from deepface import DeepFace
    return DeepFace

# --- Create Tabs ---
tab1, tab2, tab3, tab7 = st.tabs([
    "📸 1. Facial Age",
    "🪪 2. Photo-ID Matching",
    "🔎 3–6. Alternative Age Checks",
    "🔐 7. Digital Identity"
])

# ==========================================
# TAB 1: FACIAL ESTIMATION
# ==========================================
with tab1:
    st.subheader("Biometric Age Estimation via Deep Learning")
    st.caption("Ofcom description: You show your face via photo or video, and technology analyses it to estimate your age.")

    baby_example_1 = Path(__file__).resolve().parent / "docs" / "assets" / "baby_example.jpg"
    baby_example_2 = Path(__file__).resolve().parent / "docs" / "assets" / "baby_example2.jpg"
    example_col1, example_col2 = st.columns(2)
    with example_col1:
        if st.button("Baby Example 1", key="baby_example_1", disabled=not baby_example_1.exists()):
            st.session_state["facial_age_example"] = baby_example_1.read_bytes()
            st.session_state["facial_age_example_name"] = "Baby Example 1"
            st.rerun()
    with example_col2:
        if st.button("Baby Example 2", key="baby_example_2", disabled=not baby_example_2.exists()):
            st.session_state["facial_age_example"] = baby_example_2.read_bytes()
            st.session_state["facial_age_example_name"] = "Baby Example 2"
            st.rerun()

    uploaded_img = st.file_uploader(
        "Upload an image for inference",
        type=["jpg", "jpeg", "png"],
        key="facial_age_upload",
    )
    camera_img = st.camera_input("Capture image for inference", key="cam")
    generated_img = st.session_state.get("facial_age_generated")
    example_img = st.session_state.get("facial_age_example")
    if uploaded_img is not None:
        img_file = uploaded_img
        img_caption = "Uploaded Input"
    elif camera_img is not None:
        img_file = camera_img
        img_caption = "Camera Input"
    elif generated_img is not None:
        img_file = BytesIO(generated_img)
        img_caption = "Generated Example Input"
    elif example_img is not None:
        img_file = BytesIO(example_img)
        img_caption = st.session_state.get("facial_age_example_name", "Baby Example Input")
    else:
        img_file = None
        img_caption = "Input Frame"
    
    if img_file is not None:
        img = Image.open(img_file)
        img_np = np.array(img)
        
        with st.spinner("Executing neural network inference..."):
            try:
                deepface = load_deepface()
                results = deepface.analyze(
                    img_np, 
                    actions=['age'], 
                    enforce_detection=False,
                    detector_backend='mtcnn'
                )
                
                res = results[0] if isinstance(results, list) else results
                est_age = int(res['age'])
                
                col1, col2 = st.columns(2)
                col1.image(img, caption=img_caption, width=350)
                
                with col2:
                    st.metric(label="Inference: Estimated Age", value=f"{est_age} years")
                    if est_age >= 18:
                        st.success("System Output: Threshold Met (>= 18)")
                    else:
                        st.error("System Output: Threshold Not Met (< 18)")
            except Exception as e:
                st.error(f"Inference failed. Error: {e}")

    st.markdown("### Limitations and Considerations")
    st.caption(
        "Facial age estimation can be inaccurate and may be affected by image quality, lighting, "
        "facial presentation, or synthetic images. For an example of photorealistic generated faces, "
        "see [thispersondoesnotexist.com](https://thispersondoesnotexist.com/)."
    )
    if st.button("Use a generated example face", key="fetch_generated_face"):
        try:
            request = Request(
                "https://thispersondoesnotexist.com/random-person.jpeg",
                headers={
                    "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
                    "User-Agent": "Mozilla/5.0 (Age-Verification-Demo)",
                },
            )
            with urlopen(request, timeout=20) as response:
                content_type = response.headers.get_content_type()
                generated_bytes = response.read()
            if not content_type.startswith("image/"):
                raise ValueError(f"image endpoint returned {content_type} instead")
            Image.open(BytesIO(generated_bytes)).verify()
            st.session_state["facial_age_generated"] = generated_bytes
            st.rerun()
        except Exception as exc:
            st.error(f"Could not fetch a generated example face. Error: {exc}")

# ==========================================
# TAB 2: PHOTO-ID MATCHING
# ==========================================
with tab2:
    st.subheader("Photo-ID Matching: Document + Selfie")
    st.caption("Ofcom description: An image of an identity document and a selfie are compared to confirm that the document belongs to you.")

    sample_dir = Path(__file__).resolve().parent / "docs" / "assets"
    original_sample = sample_dir / "passport_sample.jpg"
    doctored_sample = sample_dir / "passport_sample_doctored.jpg"
    example_col1, example_col2 = st.columns(2)
    with example_col1:
        if st.button("Example 1", key="photo_id_example_1", disabled=not original_sample.exists()):
            st.session_state["photo_id_example"] = original_sample.read_bytes()
            st.session_state["photo_id_example_name"] = "Example 1"
    with example_col2:
        if st.button("Example 2", key="photo_id_example_2", disabled=not doctored_sample.exists()):
            st.session_state["photo_id_example"] = doctored_sample.read_bytes()
            st.session_state["photo_id_example_name"] = "Example 2"

    uploaded_id = st.file_uploader("Upload an Identity Document (Passport/ID)", type=["jpg", "png", "jpeg"])
    selfie = st.camera_input("Capture a selfie for face matching", key="id_selfie")
    selected_example = st.session_state.get("photo_id_example")
    id_input = uploaded_id if uploaded_id is not None else BytesIO(selected_example) if selected_example else None
    if st.session_state.get("photo_id_example_name") and uploaded_id is None:
        st.caption(f"Selected document: {st.session_state['photo_id_example_name']}")

    if id_input is not None and selfie is not None:
        id_img = Image.open(id_input)
        selfie_img = Image.open(selfie)
        photo_id_age_passed = False
        
        col1, col2, col3 = st.columns(3)
        col1.image(id_img, caption="Document Input", use_container_width=True)
        col2.image(selfie_img, caption="Selfie Input", use_container_width=True)
        
        with st.spinner("Executing OCR and parsing MRZ..."):
            try:
                from passporteye import read_mrz

                with TemporaryDirectory() as temp_dir:
                    temp_path = Path(temp_dir) / "document.png"
                    id_img.save(temp_path, format="PNG")
                    mrz = read_mrz(str(temp_path))
            except Exception as exc:
                mrz = None
                st.error(f"OCR failure. Error: {exc}")
            
            with col3:
                if mrz is not None:
                    data = mrz.to_dict()
                    raw_dob = str(data.get('date_of_birth', '')).strip()
                    
                    if raw_dob and len(raw_dob) == 6:
                        try:
                            current_date = date.today()
                            current_two_digit_year = current_date.year % 100
                            century = current_date.year // 100
                            
                            # Pivot year logic for YYMMDD parsing
                            birth_year = (century if int(raw_dob[:2]) <= current_two_digit_year else century - 1) * 100 + int(raw_dob[:2])
                            birth_date = date.fromisoformat(f"{birth_year:04d}-{raw_dob[2:4]}-{raw_dob[4:6]}")
                            
                            if birth_date > current_date:
                                raise ValueError("Future date parsed")
                                
                            exact_age = current_date.year - birth_date.year - ((current_date.month, current_date.day) < (birth_date.month, birth_date.day))
                        
                        except (TypeError, ValueError):
                            st.warning("MRZ detected, but date of birth checksum failed or is invalid.")
                        else:
                            st.success("MRZ Decoded and Validated")
                            st.write(f"**Document Type Code:** {data.get('type', 'N/A')}")
                            st.write(f"**Issuing State Code:** {data.get('country', 'N/A')}")
                            st.write(f"**Parsed Date of Birth:** {birth_date}")
                            st.metric("Computed Age", exact_age)
                            
                            if exact_age >= 18:
                                st.success("Condition (Age >= 18): True")
                                photo_id_age_passed = True
                            else:
                                st.error("Condition (Age >= 18): False")
                    else:
                        st.warning("MRZ read incomplete: Date of birth field missing.")
                else:
                    st.error("No valid MRZ detected in the input image.")
            if photo_id_age_passed:
                if st.button("Run local face match", key="face_match"):
                    with st.spinner("Comparing face embeddings..."):
                        try:
                            deepface = load_deepface()
                            with TemporaryDirectory() as temp_dir:
                                document_path = Path(temp_dir) / "document.png"
                                selfie_path = Path(temp_dir) / "selfie.png"
                                id_img.save(document_path, format="PNG")
                                selfie_img.save(selfie_path, format="PNG")
                                match = deepface.verify(
                                    img1_path=str(document_path),
                                    img2_path=str(selfie_path),
                                    detector_backend="mtcnn",
                                    enforce_detection=False,
                                )
                            distance = float(match.get("distance", 0))
                            threshold = float(match.get("threshold", 0))
                            st.write(f"Embedding distance: `{distance:.4f}` (match threshold: `{threshold:.4f}`)")
                            if bool(match.get("verified")):
                                st.success("Face match passed: document portrait and selfie are consistent.")
                            else:
                                st.error("Face match not confirmed: the images are not sufficiently similar.")
                        except Exception as exc:
                            st.error(f"Face matching failed. Error: {exc}")
            else:
                st.warning("Complete a valid 18+ photo-ID age check before running face matching.")
    elif id_input is not None:
        st.info("Capture a selfie as the second input to demonstrate document-to-face matching.")

    st.markdown("### Limitations and Considerations")
    st.caption(
        "Photo-ID checks can be defeated by altered or fraudulent documents, and OCR may not detect "
        "every change. These examples show a non-doctored document beside a doctored version."
    )
    if original_sample.exists() and doctored_sample.exists():
        sample_col1, sample_col2 = st.columns(2)
        sample_col1.image(str(original_sample), caption="Non-doctored ID example", use_container_width=True)
        sample_col2.image(str(doctored_sample), caption="Doctored ID example", use_container_width=True)
    else:
        st.warning("The local document comparison examples could not be found.")

# ==========================================
# TAB 3: OPEN BANKING
# ==========================================
with tab3:
    st.subheader("Open Banking Age Check (Mock Provider)")
    st.caption("Ofcom description: You give permission for an age-check service to access confirmation from your bank about whether you are over 18.")
    st.caption("Demonstrates the consent and callback pattern. No bank connection is made.")
    bank = st.selectbox("Choose a mock bank", ["Northstar Bank", "Civic Credit Union", "Example Building Society"])
    if st.button("Request age confirmation", key="bank_check"):
        request_id = hashlib.sha256(f"{bank}:{date.today()}".encode()).hexdigest()[:16]
        st.code(json.dumps({"provider": bank, "scope": "age_over_18", "consent": "granted", "request_id": request_id, "result": "over_18"}, indent=2), language="json")
        st.success("Mock bank callback received: age threshold passed.")

    st.caption(
        "Open banking checks depend on bank participation, accurate account records, and user consent. "
        "A bank's age signal may be unavailable, outdated, or not equivalent to verified identity."
    )

# ==========================================
# TAB 4: CREDIT CARD
# ==========================================
with tab3:
    st.subheader("Credit Card Age Check (Mock Payment Processor)")
    st.caption("Ofcom description: A payment processor checks whether a provided card is valid; obtaining a credit card indicates the holder is over 18.")
    st.caption("Only a tokenized authorization result is shown; card details are not collected or stored.")
    card_brand = st.selectbox("Card network", ["Visa", "Mastercard", "American Express"], key="card_brand")
    card_last_four = st.text_input("Last four digits", max_chars=4, placeholder="1234")
    if st.button("Run card eligibility check", key="card_check"):
        if card_last_four.isdigit() and len(card_last_four) == 4:
            token = hashlib.sha256(f"{card_brand}:{card_last_four}".encode()).hexdigest()[:20]
            st.code(json.dumps({"processor_token": token, "card_valid": True, "age_over_18": True}, indent=2), language="json")
            st.success("Mock processor response: age threshold passed.")
        else:
            st.warning("Enter four numeric digits to simulate a tokenized card response.")

    st.caption(
        "A valid payment card does not prove the cardholder's age. Cards may be shared, borrowed, "
        "fraudulently obtained, or issued under different eligibility rules."
    )

# ==========================================
# TAB 5: EMAIL AGE ESTIMATION
# ==========================================
with tab3:
    st.subheader("Email-Based Age Estimation (Mock Signals Provider)")
    st.caption("Ofcom description: A service analyses other online services linked to your email address to estimate your age.")
    st.caption("A real provider would assess account tenure and verified services linked to the address.")
    email = st.text_input("Email address", placeholder="person@example.com")
    if st.button("Estimate age from linked signals", key="email_check"):
        if "@" in email and "." in email.rsplit("@", 1)[-1]:
            signal_id = hashlib.sha256(email.strip().lower().encode()).hexdigest()[:16]
            st.code(json.dumps({"signal_request_id": signal_id, "account_history_found": True, "estimated_age_band": "18+", "confidence": "mock-high"}, indent=2), language="json")
            st.success("Mock signals response: age threshold passed.")
        else:
            st.warning("Enter a valid-looking email address.")

    st.caption(
        "Email-based signals are indirect and can be incomplete or misleading. Account age, linked "
        "services, and provider confidence are not reliable proof of a person's legal age."
    )

# ==========================================
# TAB 6: MOBILE NETWORK OPERATOR
# ==========================================
with tab3:
    st.subheader("Mobile Network Operator Age Check (Mock API)")
    st.caption("Ofcom description: With permission, an age-check service confirms whether age filters are applied to your mobile number.")
    st.caption("This models a permissioned lookup of an age restriction flag held by a mobile operator.")
    phone = st.text_input("Mobile number", placeholder="+44 7700 900123")
    permission = st.checkbox("I consent to the operator lookup")
    if st.button("Check mobile age filter", key="mobile_check"):
        if permission and phone.strip():
            lookup_id = hashlib.sha256(phone.strip().encode()).hexdigest()[:16]
            st.code(json.dumps({"lookup_id": lookup_id, "age_filter": "18+", "operator_result": "confirmed"}, indent=2), language="json")
            st.success("Mock operator response: age threshold passed.")
        elif not permission:
            st.warning("Consent is required before the lookup.")
        else:
            st.warning("Enter a mobile number to simulate the lookup.")

    st.caption(
        "Mobile-network age filters depend on accurate account records and operator coverage. A number "
        "may be shared, transferred, misregistered, or unavailable for verification."
    )

# ==========================================
# TAB 7: ZERO-KNOWLEDGE PROOF / ATTESTATION
# ==========================================
with tab7:
    st.subheader("Cryptographic Attestation (Selective Disclosure)")
    st.caption("Ofcom description: A digital identity wallet securely stores and shares information that proves your age.")
    
    st.markdown("### Holder Environment (Digital Wallet)")
    
    # Mock issuer key
    ISSUER_SECRET_KEY = b"STATE_ISSUER_KEY_2026"
    
    birth_year = st.slider("Select Birth Year (Local State)", min_value=1950, max_value=2026, value=2000)
    is_adult = (date.today().year - birth_year) >= 18
    
    # Generate cryptographic token / proof
    proof_payload = f"CLAIM:OVER_18:{is_adult}".encode('utf-8')
    signature = hmac.new(ISSUER_SECRET_KEY, proof_payload, hashlib.sha256).hexdigest()
    
    st.code(f"""
// Payload generated by Digital Wallet and sent over network
{{
  "claim": "Age >= 18",
  "value": {str(is_adult).lower()},
  "issuer_signature": "{signature}"
}}
    """, language="json")
    
    st.markdown("### Relying Party Environment (Verifier)")
    if st.button("Verify Attestation"):
        # The verifier receives the payload and checks the signature against the expected issuer key
        expected_sig = hmac.new(ISSUER_SECRET_KEY, proof_payload, hashlib.sha256).hexdigest()
        
        # Constant-time comparison to prevent timing attacks
        if hmac.compare_digest(signature, expected_sig):
            if is_adult:
                st.success("✅ Signature verified. Cryptographic proof is valid. Claim (OVER_18) == True.")
            else:
                st.error("❌ Signature verified. Cryptographic proof is valid. Claim (OVER_18) == False.")
        else:
            st.error("❌ Invalid Signature. Payload integrity compromised.")

# --- Added Explanation Section ---
    st.divider()
    st.markdown("### What's the difference between this and a standard Digital ID?")
    st.markdown("""
    Normally, using a **traditional Digital ID** (e.g. showing a digital driving licence, uploading a document scan, or signing in via an identity provider) forces you to provide unnecessary PII (Personally Identifiable Information) just to prove how old you are. The website receives your full name, exact date of birth, home address, and photo, then calculates on its servers whether you meet the age rule. This creates privacy risks: websites hold sensitive data they don't actually need, and your identity can be tracked across the internet.

    **In Cryptographic Attestation (Selective Disclosure):**
    * **The local device does the calculation:** Your digital wallet holds your verified identity locally (e.g. in your phone's hardware Secure Enclave) and evaluates your age criteria on-device.
    * **Only the cryptographic proof is sent to the verifier:** Instead of broadcasting personal data across the internet, the wallet issues a tamper-proof cryptographic token that states nothing more than `"Age >= 18: True"`.
    * **Zero identity disclosure:** The website gets mathematical certainty that an official authority verified your age, but learns nothing else about your name, birthdate, or identity.
    """)
