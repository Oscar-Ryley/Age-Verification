import os
# --- Force TensorFlow to use legacy Keras mode for DeepFace ---
os.environ["TF_USE_LEGACY_KERAS"] = "1"

import streamlit as st
import numpy as np
from PIL import Image
import hashlib
import hmac
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory

# --- Page Config ---
st.set_page_config(page_title="Gov Age Assurance", layout="wide", page_icon="🛡️")
st.title("🛡️ Age Assurance & Verification Showcase")
st.markdown("""
**Public Sector Hackathon Demo** | Comparing three distinct technical paradigms for age verification. 
Evaluate these based on *Friction*, *Accuracy*, and *Privacy*.
""")

# --- Caching the ML Model so it loads quickly ---
@st.cache_resource
def load_deepface():
    from deepface import DeepFace
    return DeepFace

# --- Create Tabs ---
tab1, tab2, tab3 = st.tabs([
    "📸 1. Facial Biometrics (AI)", 
    "🛂 2. Document OCR (Deterministic)", 
    "🔐 3. Digital Wallet / Zero-Knowledge"
])

# ==========================================
# TAB 1: FACIAL ESTIMATION
# ==========================================
with tab1:
    st.subheader("Method 1: Biometric Age Estimation")
    st.info("**Policy view:** Zero user friction (no ID needed). Medium privacy (processes biometric data). Probabilistic accuracy (± 3-5 years margin of error).")
    
    img_file = st.camera_input("Take a photo to estimate age", key="cam")
    
    if img_file is not None:
        img = Image.open(img_file)
        img_np = np.array(img)
        
        with st.spinner("Analyzing facial features using AI..."):
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
                col1.image(img, caption="Analyzed Frame", width=350)
                
                with col2:
                    st.metric(label="AI Estimated Age", value=f"{est_age} years")
                    if est_age >= 18:
                        st.success("✅ **Result:** Adult (Over 18). Access Granted.")
                    else:
                        st.error("❌ **Result:** Minor (Under 18). Access Denied.")
                        
                    st.warning("⚠️ **Hackathon Note:** Notice how AI can be fooled by lighting, makeup, or demographics. This is why policy requires a 'buffer' (e.g., challenge anyone who looks under 25).")
            except Exception as e:
                st.error(f"Could not analyze face. Please ensure you are clearly visible. Error: {e}")

# ==========================================
# TAB 2: DOCUMENT MRZ PARSING
# ==========================================
with tab2:
    st.subheader("Method 2: ID Document Scanning (MRZ)")
    st.info("**Policy view:** High user friction (must find and scan physical ID). Low privacy (exposes name, exact DOB, and ID number). 100% Deterministic accuracy.")
    
    uploaded_id = st.file_uploader("Upload a Passport or ID photo", type=["jpg", "png", "jpeg"])
    
    if uploaded_id is not None:
        id_img = Image.open(uploaded_id)
        
        col1, col2 = st.columns(2)
        col1.image(id_img, caption="Uploaded Document", use_container_width=True)
        
        with st.spinner("Extracting Machine Readable Zone (MRZ)..."):
            try:
                from passporteye import read_mrz

                with TemporaryDirectory() as temp_dir:
                    temp_path = Path(temp_dir) / "document.png"
                    id_img.save(temp_path, format="PNG")
                    mrz = read_mrz(str(temp_path))
            except Exception as exc:
                mrz = None
                st.error(f"Could not read the document. Please upload a clearer image. Error: {exc}")
            
            with col2:
                if mrz is not None:
                    data = mrz.to_dict()
                    raw_dob = str(data.get('date_of_birth', '')).strip()
                    
                    if raw_dob and len(raw_dob) == 6:
                        # Convert YYMMDD to YYYY-MM-DD
                        try:
                            current_date = date.today()
                            current_two_digit_year = current_date.year % 100
                            century = current_date.year // 100
                            birth_year = (century if int(raw_dob[:2]) <= current_two_digit_year else century - 1) * 100 + int(raw_dob[:2])
                            birth_date = date.fromisoformat(f"{birth_year:04d}-{raw_dob[2:4]}-{raw_dob[4:6]}")
                            if birth_date > current_date:
                                raise ValueError("birth date is in the future")
                            exact_age = current_date.year - birth_date.year - ((current_date.month, current_date.day) < (birth_date.month, birth_date.day))
                        except (TypeError, ValueError):
                            st.warning("MRZ found, but birth date is invalid.")
                        else:
                            st.success("🎯 MRZ Successfully Decoded")
                            st.write(f"**Document Type:** {data.get('type', 'N/A')}")
                            st.write(f"**Issuing Country:** {data.get('country', 'N/A')}")
                            st.write(f"**Extracted Birthdate:** {birth_date}")
                            st.metric("Calculated Age", exact_age)
                            
                            if exact_age >= 18:
                                st.success("✅ Access Granted: User is mathematically verified 18+")
                            else:
                                st.error("❌ Access Denied: Under 18")
                    else:
                        st.warning("MRZ found, but birth date unreadable.")
                else:
                    st.error("❌ No MRZ detected. Upload a clearer image of the bottom of the passport.")

# ==========================================
# TAB 3: ZERO-KNOWLEDGE PROOF
# ==========================================
with tab3:
    st.subheader("Method 3: Privacy-Preserving Attestation (The Future)")
    st.info("**Policy view:** Low friction (tap phone to approve). Maximum privacy (zero personal data shared). 100% Cryptographic accuracy.")
    
    st.markdown("### 📱 1. User's Government Digital Wallet (Private)")
    st.write("The user has a digital ID on their phone. The government signed it. The user only shares a 'Yes/No' proof, *not* their actual birthday.")
    
    gov_secret_key = b"GOV_SIGNING_KEY_UK_2026"
    birth_year = st.slider("Simulate Your Birth Year", min_value=1950, max_value=2020, value=2000)
    is_adult = (date.today().year - birth_year) >= 18
    
    # Generate cryptographic token / proof
    proof_payload = f"ELIGIBLE_OVER_18:{is_adult}".encode('utf-8')
    signature = hmac.new(gov_secret_key, proof_payload, hashlib.sha256).hexdigest()
    
    st.code(f"""
    [Simulated Payload sent to Website]
    Attestation: "Age >= 18" -> {is_adult}
    Issuer Signature: {signature[:32]}... 
    *Notice: Name and DOB are NEVER transmitted*
    """, language="json")
    
    st.markdown("### 🏢 2. The Website Verifying the User")
    if st.button("Authenticate with Digital Wallet"):
        expected_sig = hmac.new(gov_secret_key, proof_payload, hashlib.sha256).hexdigest()
        if hmac.compare_digest(signature, expected_sig) and is_adult:
            st.success("✅ **Verified!** Cryptographic proof is valid. The user is over 18. Zero personal data was stored.")
        else:
            st.error("❌ **Rejected:** Under 18 or invalid signature.")
