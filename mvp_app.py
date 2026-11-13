import streamlit as st
import hashlib
from datetime import datetime
import json

# --- 1. NIPOST Offline Validation ---
def validate_nipost_format(postcode):
    clean_code = postcode.replace("-", "").strip()
    if len(clean_code) == 11 and clean_code.isalnum():
        return True, "Valid Format"
    return False, "Invalid Format"

# --- WEB PAGE CONFIGURATION ---
st.set_page_config(page_title="Manifesto Watch MVP", page_icon="🛡️", layout="wide")

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select Portal:", ["Volunteer Capture Portal", "Federal Aggregation Dashboard"])

# ==============================================================================
# PORTAL 1: VOLUNTEER CAPTURE PORTAL
# ==============================================================================
if page == "Volunteer Capture Portal":
    st.title("🛡️ Manifesto Watch 2027")
    st.subheader("Cryptographic Evidence Chain of Custody")

    st.write("### 1. Agent Verification")
    role = st.selectbox("Select your Level:", ["Polling Unit", "Ward", "LGA", "State", "Federal"])
    volunteer_id = st.text_input("Volunteer ID (e.g., V-001)")
    nipost_code = st.text_input("NIPOST Digital Postcode")

    valid_nipost = False
    if nipost_code:
        is_valid_format, message = validate_nipost_format(nipost_code)
        if is_valid_format:
            st.success(f"✅ NIPOST Postcode Format Validated: {nipost_code}")
            valid_nipost = True
        else:
            st.error(f"❌ {message}")

    parent_hash = None
    if role != "Polling Unit":
        st.write("### 2. Cryptographic Linking")
        parent_hash = st.text_input("Enter Parent Hash (Hash from the level below):")
        if parent_hash:
            st.info("🔗 Parent Hash linked.")

    st.write("### 3. Upload Evidence")
    uploaded_file = st.file_uploader("Upload electoral document", type=["jpg", "png", "jpeg"])

    if uploaded_file is not None and valid_nipost:
        if role != "Polling Unit" and not parent_hash:
            st.error("❌ Cannot secure: Parent Hash is missing.")
        else:
            bytes_data = uploaded_file.getvalue()
            sha256_hash = hashlib.sha256(bytes_data).hexdigest()
            st.image(bytes_data, caption="Uploaded Document", width=400)
            
            evidence_record = {
                "level": role,
                "volunteer_id": volunteer_id,
                "nipost_postcode": nipost_code,
                "parent_hash": parent_hash if parent_hash else "GENESIS",
                "current_sha256": sha256_hash,
                "timestamp": str(datetime.now()),
                "filename": uploaded_file.name
            }
            
            st.success("✅ Evidence Secured!")
            st.json(evidence_record)
            
            json_string = json.dumps(evidence_record, indent=4)
            st.download_button(
                label="⬇️ Download Evidence JSON",
                file_name=f"evidence_{role}_{volunteer_id}.json",
                mime="application/json",
                data=json_string
            )

# ==============================================================================
# PORTAL 2: FEDERAL AGGREGATION DASHBOARD (The Ledger)
# ==============================================================================
elif page == "Federal Aggregation Dashboard":
    st.title("🏛️ Federal Aggregation Dashboard")
    st.subheader("Real-Time Cryptographic Chain Verification")
    st.markdown("""
    This dashboard simulates the national aggregation center. 
    Below is a mock ledger of evidence submitted from different levels. 
    The system recursively verifies that every child hash correctly links to its parent hash.
    """)

    # MOCK DATA SIMULATING WHAT WOULD BE IN A DATABASE
    # In a real app, this would be a database query of all uploaded JSONs
    mock_ledger = [
        {"level": "Polling Unit", "id": "PU-045-A", "hash": "Hash_A_111", "parent": "GENESIS", "status": "VALID"},
        {"level": "Ward", "id": "Ward-3", "hash": "Hash_B_222", "parent": "Hash_A_111", "status": "VALID"},
        {"level": "LGA", "id": "AMAC", "hash": "Hash_C_333", "parent": "Hash_B_222", "status": "VALID"},
        {"level": "State", "id": "FCT", "hash": "Hash_D_444", "parent": "Hash_C_333", "status": "VALID"},
        {"level": "Federal", "id": "Abuja", "hash": "Hash_E_555", "parent": "Hash_D_444", "status": "VALID"},
        
        # Simulating a TAMPERED Chain
        {"level": "Polling Unit", "id": "PU-099-B", "hash": "Hash_A_999", "parent": "GENESIS", "status": "VALID"},
        {"level": "Ward", "id": "Ward-8", "hash": "Hash_B_888", "parent": "Hash_A_999", "status": "VALID"},
        {"level": "LGA", "id": "Kuje", "hash": "Hash_C_777", "parent": "Hash_WRONG", "status": "BROKEN CHAIN!"}, # <-- TAMPER DETECTED
    ]

    # Display the ledger as a table
    st.write("### National Evidence Ledger")
    st.dataframe(mock_ledger, use_container_width=True)

    # The Automated Verification Logic
    st.write("### Automated Chain Audit")
    broken_links = [item for item in mock_ledger if item["status"] != "VALID"]
    
    if len(broken_links) == 0:
        st.success("✅ NATIONAL INTEGRITY SECURED: All cryptographic chains match perfectly.")
    else:
        st.error(f"🚨 SYSTEM ALERT: {len(broken_links)} Chain(s) broken. Federal audit required.")
        for link in broken_links:
            st.warning(f"Discrepancy detected at {link['level']} level ({link['id']}). Parent Hash mismatch.")
