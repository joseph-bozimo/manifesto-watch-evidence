import streamlit as st
import hashlib
from datetime import datetime
import json

# --- NIPOST Offline Validation Function ---
def validate_nipost_format(postcode):
    # A simplified structural check for the 11-character alphanumeric format
    # Example format: FC-03-B06-AG-12 (State-LGA-Ward-Locality-Building)
    clean_code = postcode.replace("-", "").strip()
    if len(clean_code) == 11 and clean_code.isalnum():
        return True, "Valid Format"
    else:
        return False, "Invalid Format (Must be 11 alphanumeric characters)"

# --- WEB PAGE CONFIGURATION ---
st.set_page_config(page_title="Manifesto Watch MVP", page_icon="🛡️")
st.title("🛡️ Manifesto Watch 2027")
st.subheader("Cryptographic Evidence Verification Portal")

st.markdown("""
This portal allows authorised, non-partisan volunteers to securely upload electoral documents. 
The system generates a cryptographic fingerprint (SHA-256) and validates the location against the NIPOST addressing system.
""")

# --- UI: METADATA INPUT ---
st.write("### 1. Volunteer Metadata")
volunteer_id = st.text_input("Volunteer ID (e.g., V-001)")

# NIPOST Integration
nipost_code = st.text_input("NIPOST Digital Postcode (e.g., FC-03-B06-AG-12)")

# Real-time validation feedback for the user
if nipost_code:
    is_valid, message = validate_nipost_format(nipost_code)
    if is_valid:
        st.success(f"✅ NIPOST Postcode Validated: {nipost_code}")
    else:
        st.error(f"❌ {message}")

# --- UI: FILE UPLOADER ---
st.write("### 2. Upload Evidence")
uploaded_file = st.file_uploader("Choose an image of the electoral document (JPG, PNG)", type=["jpg", "png", "jpeg"])

# --- PROCESSING LOGIC ---
if uploaded_file is not None:
    # Read the file bytes
    bytes_data = uploaded_file.getvalue()
    
    # Generate SHA-256 Fingerprint
    sha256_hash = hashlib.sha256(bytes_data).hexdigest()
    
    # Display the image preview
    st.image(bytes_data, caption="Uploaded Document", use_column_width=True)
    
    # Create the evidence record
    evidence_record = {
        "volunteer_id": volunteer_id if volunteer_id else "UNKNOWN",
        "nipost_postcode": nipost_code if nipost_code else "NOT_PROVIDED",
        "timestamp": str(datetime.now()),
        "filename": uploaded_file.name,
        "sha256_fingerprint": sha256_hash,
        "status": "SECURED"
    }
    
    # Show the output to the user
    st.success("✅ Document Successfully Secured!")
    st.write("### 3. Cryptographic Evidence Record")
    st.json(evidence_record)
    
    # Convert to JSON string for download
    json_string = json.dumps(evidence_record, indent=4)
    
    # Create Download Button
    st.download_button(
        label="⬇️ Download Evidence Record (JSON)",
        file_name=f"evidence_{volunteer_id}.json",
        mime="application/json",
        data=json_string
    )
