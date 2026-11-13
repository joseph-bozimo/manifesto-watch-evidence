import streamlit as st
import hashlib
from datetime import datetime
import json

# --- 1. NIPOST Offline Validation ---
def validate_nipost_format(postcode):
    clean_code = postcode.replace("-", "").strip()
    if len(clean_code) == 11 and clean_code.isalnum():
        return True, "Valid Format"
    else:
        return False, "Invalid Format (Must be 11 alphanumeric characters)"

# --- 2. Mock INEC Polling Unit Register ---
MOCK_INEC_REGISTER = {
    "FC03B06AG12": {"pu_name": "Polling Unit 045-A", "ward": "Ward 3", "lga": "AMAC"},
    "FC03B06AG13": {"pu_name": "Polling Unit 045-B", "ward": "Ward 3", "lga": "AMAC"},
    "FC01A02BC34": {"pu_name": "Polling Unit 012-C", "ward": "Ward 1", "lga": "Gwagwalada"}
}

# --- WEB PAGE CONFIGURATION ---
st.set_page_config(page_title="Manifesto Watch MVP", page_icon="🛡️")
st.title("🛡️ Manifesto Watch 2027")
st.subheader("Cryptographic Evidence Verification Portal")

st.markdown("""
This portal allows authorised, non-partisan volunteers to securely upload electoral documents. 
The system generates a SHA-256 fingerprint and validates the location against both NIPOST and the INEC Polling Unit Register.
""")

# --- UI: METADATA INPUT ---
st.write("### 1. Volunteer Metadata")
volunteer_id = st.text_input("Volunteer ID (e.g., V-001)")
nipost_code = st.text_input("NIPOST Digital Postcode (e.g., FC03B06AG12)")

# Real-time validation feedback
valid_inec = False
inec_data = None

if nipost_code:
    is_valid_format, message = validate_nipost_format(nipost_code)
    if is_valid_format:
        st.success(f"✅ NIPOST Postcode Format Validated: {nipost_code}")
        
        clean_code = nipost_code.replace("-", "").upper()
        if clean_code in MOCK_INEC_REGISTER:
            inec_data = MOCK_INEC_REGISTER[clean_code]
            st.info(f"🗳️ INEC Register Match: {inec_data['pu_name']} ({inec_data['lga']}, {inec_data['ward']})")
            valid_inec = True
        else:
            st.warning("⚠️ Warning: This postcode is not linked to a known INEC Polling Unit in our database.")
    else:
        st.error(f"❌ {message}")

# --- UI: FILE UPLOADER ---
st.write("### 2. Upload Evidence")
uploaded_file = st.file_uploader("Choose an image of the electoral document (JPG, PNG)", type=["jpg", "png", "jpeg"])

# --- PROCESSING LOGIC ---
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    sha256_hash = hashlib.sha256(bytes_data).hexdigest()
    st.image(bytes_data, caption="Uploaded Document", use_column_width=True)
    
    evidence_record = {
        "volunteer_id": volunteer_id if volunteer_id else "UNKNOWN",
        "nipost_postcode": nipost_code,
        "inec_verification": "VERIFIED" if valid_inec else "UNVERIFIED",
        "pu_name": inec_data['pu_name'] if valid_inec else "N/A",
        "timestamp": str(datetime.now()),
        "filename": uploaded_file.name,
        "sha256_fingerprint": sha256_hash,
        "status": "SECURED"
    }
    
    st.success("✅ Document Successfully Secured!")
    st.write("### 3. Cryptographic Evidence Record")
    st.json(evidence_record)
    
    json_string = json.dumps(evidence_record, indent=4)
    st.download_button(
        label="⬇️ Download Evidence Record (JSON)",
        file_name=f"evidence_{volunteer_id}.json",
        mime="application/json",
        data=json_string
    )
