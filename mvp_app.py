import streamlit as st
import hashlib
from datetime import datetime
import json
import pandas as pd
import random
import pytesseract
from PIL import Image
import re
from img2table.document import Image as Img2TableImage
from img2table.ocr import TesseractOCR

# --- 1. NIPOST & OCR Geo-Validation Engine ---
def process_document_and_validate(uploaded_file, nipost_code):
    try:
        image = Image.open(uploaded_file)
        
        # Save image temporarily for img2table
        temp_path = "temp_uploaded_image.png"
        image.save(temp_path)

        # 1. Determine NIPOST State
        if nipost_code.upper().startswith("FC"):
            nipost_state = "FCT (ABUJA)"
        elif nipost_code.upper().startswith("ED"):
            nipost_state = "EDO"
        else:
            nipost_state = "UNKNOWN"

        # 2. Extract Table Data using img2table
        ocr = TesseractOCR(lang="eng")
        table_img = Img2TableImage(src=temp_path)
        extracted_tables = table_img.extract_tables(ocr=ocr, implicit_rows=True, borderless_tables=True, min_confidence=50)

        votes = {"APC": 0, "PDP": 0, "LP": 0, "NDC": 0, "ADC": 0}
        doc_state = "UNKNOWN"

        if extracted_tables:
            # Convert the first detected table to a pandas DataFrame
            df = extracted_tables[0].df
            
            # Search the extracted cells for the state name (Geo-validation)
            table_text = df.to_string().upper()
            if "EDO" in table_text:
                doc_state = "EDO"
            elif "ABUJA" in table_text or "FCT" in table_text:
                doc_state = "FCT (ABUJA)"

            # Search for party acronyms in the table and get the number in the next column
            for index, row in df.iterrows():
                row_values = row.values
                for i, cell in enumerate(row_values):
                    cell_upper = str(cell).upper()
                    if "APC" in cell_upper:
                        # The votes are usually in the column immediately to the right
                        try: votes["APC"] = int(re.search(r'\d+', str(row_values[i+2])).group())
                        except: pass
                    elif "PDP" in cell_upper:
                        try: votes["PDP"] = int(re.search(r'\d+', str(row_values[i+2])).group())
                        except: pass
                    elif "LP" in cell_upper:
                        try: votes["LP"] = int(re.search(r'\d+', str(row_values[i+2])).group())
                        except: pass

        # 3. GEO-MATCH VALIDATION
        if nipost_state != doc_state and doc_state != "UNKNOWN":
            return False, f"🚨 GEO-MISMATCH DETECTED: NIPOST is for {nipost_state}, but the document text says {doc_state}. Upload Rejected.", None

        return True, f"✅ GEO-MATCH VERIFIED: Document ({doc_state}) matches NIPOST ({nipost_state}).", votes

    except Exception as e:
        return False, f"Error processing image: {e}", None

# --- INITIALIZE SESSION STATE ---
if 'evidence_db' not in st.session_state:
    st.session_state.evidence_db = []
if 'extracted_votes' not in st.session_state:
    st.session_state.extracted_votes = {}

# --- WEB PAGE CONFIGURATION ---
st.set_page_config(page_title="Civic Audit MVP", page_icon="🛡️", layout="wide")

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select Portal:", ["Volunteer Capture Portal", "The 'Holy Grail' National Dashboard"])

# ==============================================================================
# PORTAL 1: VOLUNTEER CAPTURE PORTAL
# ==============================================================================
if page == "Volunteer Capture Portal":
    st.title("🛡️ Manifesto Watch 2027")
    st.subheader("Live Evidence Capture & Automated Table Extraction")

    st.write("### 1. Agent Verification")
    col1, col2 = st.columns(2)
    with col1:
        role = st.selectbox("Select your Level:", ["Polling Unit", "Ward", "LGA", "State"])
        volunteer_id = st.text_input("Volunteer ID (e.g., V-001)")
        pu_name = st.text_input("Polling Unit / Ward Name (e.g., PU-AMAC-05)")
    with col2:
        nipost_code = st.text_input("NIPOST Digital Postcode (e.g., ED123456789)")

    st.write("### 2. Upload Evidence")
    uploaded_file = st.file_uploader("Upload electoral document", type=["jpg", "png", "jpeg"])
    
    if uploaded_file is not None and nipost_code:
        if st.button("🔍 Run Advanced Table Extraction"):
            with st.spinner("Scanning grid lines and extracting table data..."):
                is_valid, message, extracted_votes = process_document_and_validate(uploaded_file, nipost_code)
                if is_valid:
                    st.success(message)
                    st.write("### Automated Vote Extraction Results:")
                    st.json(extracted_votes)
                    st.session_state.extracted_votes = extracted_votes
                else:
                    st.error(message)

    st.write("#### Enter/Verify Votes from the Document")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        apc_votes = st.number_input("APC", min_value=0, value=st.session_state.extracted_votes.get('APC', 0))
    with col2:
        pdp_votes = st.number_input("PDP", min_value=0, value=st.session_state.extracted_votes.get('PDP', 0))
    with col3:
        lp_votes = st.number_input("LP", min_value=0, value=st.session_state.extracted_votes.get('LP', 0))
    with col4:
        ndc_votes = st.number_input("NDC", min_value=0, value=st.session_state.extracted_votes.get('NDC', 0))
    with col5:
        adc_votes = st.number_input("ADC", min_value=0, value=st.session_state.extracted_votes.get('ADC', 0))

    if st.button("Secure & Add to National Aggregation"):
        if uploaded_file is None or not pu_name or not nipost_code:
            st.error("Please complete all fields.")
        else:
            bytes_data = uploaded_file.getvalue()
            sha256_hash = hashlib.sha256(bytes_data).hexdigest()
            
            evidence_record = {
                "level": role, "pu": pu_name, "nipost": nipost_code,
                "hash": sha256_hash, "time": str(datetime.now()),
                "votes": {"APC": apc_votes, "PDP": pdp_votes, "LP": lp_votes, "NDC": ndc_votes, "ADC": adc_votes}
            }
            
            st.session_state.evidence_db.append(evidence_record)
            st.success(f"✅ Evidence secured and added!")

# ==============================================================================
# PORTAL 2: THE 'HOLY GRAIL' NATIONAL DASHBOARD
# ==============================================================================
elif page == "The 'Holy Grail' National Dashboard":
    st.title("🏛️ National Civic Audit Dashboard")
    db = st.session_state.evidence_db
    
    if st.button("🚀 Inject Demo Data"):
        for i in range(1000):
            db.append({"level": "PU", "pu": f"PU-DEMO-{i}", "nipost": "FC-DEMO", "hash": f"hash_{i}", "time": "2027", "votes": {"APC": random.randint(50, 200), "PDP": random.randint(50, 200), "LP": random.randint(20, 150), "NDC": 5, "ADC": 5}})

    total_apc = sum(item['votes']['APC'] for item in db)
    total_pdp = sum(item['votes']['PDP'] for item in db)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("APC Total", f"{total_apc:,}")
    col2.metric("PDP Total", f"{total_pdp:,}")
    col3.metric("Total Units", f"{len(db):,}")
