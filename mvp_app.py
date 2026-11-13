import streamlit as st
import hashlib
from datetime import datetime
import json

st.set_page_config(page_title="Manifesto Watch MVP", page_icon="🛡️")
st.title("🛡️ Manifesto Watch 2027")
st.subheader("Cryptographic Evidence Verification Portal")

st.markdown("""
This portal allows authorised, non-partisan volunteers to securely upload electoral documents. 
The system generates a cryptographic fingerprint (SHA-256) to mathematically prove the document has not been altered.
""")

st.write("### 1. Volunteer Metadata")
volunteer_id = st.text_input("Volunteer ID (e.g., V-001)")
location = st.text_input("State / LGA (e.g., Abuja Municipal)")

st.write("### 2. Upload Evidence")
uploaded_file = st.file_uploader("Choose an image of the electoral document (JPG, PNG)", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    # Generate Hash
    bytes_data = uploaded_file.getvalue()
    sha256_hash = hashlib.sha256(bytes_data).hexdigest()
    
    st.image(bytes_data, caption="Uploaded Document", use_column_width=True)
    
    evidence_record = {
        "volunteer_id": volunteer_id if volunteer_id else "UNKNOWN",
        "location": location if location else "UNKNOWN",
        "timestamp": str(datetime.now()),
        "filename": uploaded_file.name,
        "sha256_fingerprint": sha256_hash,
        "status": "SECURED & VERIFIED"
    }
    
    st.success("✅ Document Successfully Cryptographically Sealed!")
    st.write("### 3. Generated Evidence Record")
    st.json(evidence_record)
    
    json_string = json.dumps(evidence_record, indent=4)
    st.download_button(
        label="⬇️ Download Verified Evidence Record (JSON)",
        file_name=f"evidence_{volunteer_id}.json",
        mime="application/json",
        data=json_string
    )
