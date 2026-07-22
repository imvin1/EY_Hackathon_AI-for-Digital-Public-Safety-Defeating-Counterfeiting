import streamlit as st
import httpx
import numpy as np
import pandas as pd
import cv2
import matplotlib.pyplot as plt
import networkx as nx
import uuid
import time
from datetime import datetime

# Import backend services directly for seamless fallback execution
from backend.app.config import settings
from backend.app.services.arrest_scam_service import arrest_scam_service
from backend.app.services.counterfeit_service import counterfeit_service
from backend.app.services.fraud_network_service import fraud_network_service
from backend.app.services.geospatial_service import geospatial_service
from backend.app.services.citizen_shield_service import citizen_shield_service

from backend.app.models.arrest_scam import ArrestScamAnalysisRequest, CallerProfile, MediaIndicators
from backend.app.models.counterfeit import CurrencyValidationResponse
from backend.app.models.fraud_network import NodeData, EdgeData
from backend.app.models.geospatial import IncidentPoint
from backend.app.models.citizen_shield import CitizenRiskQuery

# Page Configuration
st.set_page_config(
    page_title="DefeatShield AI - Public Safety Command Center",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for rich dashboard styling
st.markdown("""
<style>
    /* Global App Styles */
    .main {
        background-color: #0f172a;
        color: #f8fafc;
    }
    
    /* Header Gradient Banner */
    .header-banner {
        background: linear-gradient(135deg, #1e3a8a 0%, #0f172a 100%);
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 24px;
        border: 1px solid #1e40af;
        box-shadow: 0 4px 20px rgba(30, 64, 175, 0.2);
    }
    .header-title {
        font-family: 'Outfit', 'Inter', sans-serif;
        color: #60a5fa;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
    }
    .header-subtitle {
        color: #94a3b8;
        font-size: 1.1rem;
        margin-top: 5px;
    }

    /* Card Panels Styling */
    .card-panel {
        background-color: #1e293b;
        border-radius: 8px;
        padding: 20px;
        border: 1px solid #334155;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }

    /* Flashing Red MHA Alert Callout */
    .mha-alert-card {
        background: linear-gradient(135deg, #7f1d1d 0%, #1e293b 100%);
        border: 2px solid #ef4444;
        border-radius: 8px;
        padding: 18px;
        color: #fecaca;
        margin-bottom: 20px;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { border-color: #ef4444; }
        50% { border-color: #b91c1c; }
        100% { border-color: #ef4444; }
    }

    /* Metric Badges */
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #38bdf8;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Code/Memorandum Styling */
    .memo-box {
        background-color: #020617;
        font-family: 'Courier New', Courier, monospace;
        color: #10b981;
        padding: 15px;
        border-radius: 5px;
        border-left: 4px solid #10b981;
        white-space: pre-wrap;
    }
</style>
""", unsafe_allow_html=True)

# Top Brand Banner
st.markdown("""
<div class="header-banner">
    <h1 class="header-title"> DEFEATSHIELD AI</h1>
    <div class="header-subtitle">Digital Public Safety & Fraud Counter-Intelligence Command Center</div>
</div>
""", unsafe_allow_html=True)

# Sidebar - Settings and Framework status
st.sidebar.markdown("### SYSTEM GATEWAY STATUS")
backend_url = "http://localhost:8000/api/v1"
api_online = False

try:
    response = httpx.get("http://localhost:8000/", timeout=1.0)
    if response.status_code == 200:
        api_online = True
except Exception:
    api_online = False

if api_online:
    st.sidebar.success("REST Backend API Connected")
else:
    st.sidebar.warning("REST API Offline (Using In-Process AI Services)")

st.sidebar.markdown("---")
st.sidebar.markdown("###  CORE INTEGRATIONS")
st.sidebar.info(f"**Gemini Model:** gemini-1.5-flash\n\n**CV Module:** OpenCV 4.9 (active)\n\n**Graph Engine:** NetworkX 3.2 (active)\n\n**Geospatial:** Spherical Haversine (active)")

# Setup main tabs for all 5 distinct modules
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Digital Arrest Alerting",
    "FICN Banknote Inspector",
    "Fraud Network Graph",
    "Spatial Patrol Optimizer",
    "Citizen Fraud Shield"
])

# -------------------------------------------------------------
# TAB 1: Digital Arrest Scam Detection & Alerting
# -------------------------------------------------------------
with tab1:
    st.header(" Digital Arrest Call Flow Intelligence")
    st.markdown("Tracks coercion scripts, voice synthetic markers, and visual uniforms to dispatch Ministry of Home Affairs (MHA) cyber blocks.")
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.subheader("Call Telemetry & Transcript Input")
        
        # Test templates for quick demo evaluation
        st.markdown("**Sample Scripts (Click to copy/paste below):**")
        st.code("CBI HEADQUARTERS CALL: You are under digital arrest. A parcel sent via FedEx in your name contains 50 grams of MDMA drugs and fake passports. Do not call your family or disconnect Skype, or the local police will arrest you within 2 hours.", language="text")
        st.code("Electricity board warning. Your bill is overdue. Your power connection will be cut off by 6 PM tonight. Call our manager at 9922114400 to verify your payment immediately.", language="text")

        session_id = st.text_input("Session ID", value=f"CALL-{uuid.uuid4().hex[:8].upper()}")
        phone_number = st.text_input("Caller Phone Identifier", value="+91 98452-90111")
        call_duration = st.slider("Session Duration (Seconds)", min_value=10, max_value=600, value=120)
        
        transcript_text = st.text_area(
            "Call Conversation Transcript",
            value="",
            placeholder="Paste call transcription or script logs here..."
        )
        
        # Meta flags
        st.markdown("##### Network & Spoofing Indicators")
        s_col1, s_col2 = st.columns(2)
        with s_col1:
            is_voip = st.checkbox("VoIP Number Signature Detected", value=True)
            carrier_mismatch = st.checkbox("Carrier Registry Mismatch", value=False)
        with s_col2:
            spoof_conf = st.slider("Caller ID Spoof Probability", 0.0, 1.0, 0.70)
            
        st.markdown("##### CV & Speech Signal Indicators")
        m_col1, m_col2 = st.columns(2)
        with m_col1:
            fake_uniform = st.checkbox("Visual: Impersonated Police Uniform/Backdrop detected", value=False)
            fake_backdrop = st.checkbox("Visual: Fake courtroom setup detected", value=False)
        with m_col2:
            voice_synth = st.slider("Audio: Cloned/Synthetic Voice Probability", 0.0, 1.0, 0.15)
            
        analyze_btn = st.button("Evaluate Call Session Threat", type="primary")

    with col2:
        st.subheader("⚡ Threat Analytics & MHA Alert Feed")
        
        if analyze_btn:
            if not transcript_text:
                st.error("Please enter a call transcript to analyze.")
            else:
                with st.spinner("Executing sensor fusion classification..."):
                    # Build request model
                    caller_prof = CallerProfile(
                        phone_number=phone_number,
                        is_voip=is_voip,
                        carrier_mismatch=carrier_mismatch,
                        spoofing_confidence=spoof_conf
                    )
                    media_ind = MediaIndicators(
                        fake_uniform_detected=fake_uniform,
                        fake_backdrop_detected=fake_backdrop,
                        voice_synthetic_probability=voice_synth
                    )
                    payload = ArrestScamAnalysisRequest(
                        call_id=session_id,
                        transcript=transcript_text,
                        caller=caller_prof,
                        media=media_ind,
                        call_duration_seconds=call_duration
                    )

                    # Execute service (REST or local fallback)
                    if api_online:
                        try:
                            res = httpx.post(f"{backend_url}/arrest-scam/analyze", json=payload.model_dump())
                            result = res.json()
                        except Exception as ex:
                            st.warning(f"REST call failed: {ex}. Falling back to internal engine.")
                            result = arrest_scam_service.analyze_scam_session(payload)
                    else:
                        import asyncio
                        # Streamlit is synchronous, run async service method
                        result = asyncio.run(arrest_scam_service.analyze_scam_session(payload))
                    
                    # Display Results
                    prob = result.scam_probability
                    coercion = result.coercion_score
                    
                    st.markdown(f"#### Scam Probability: **{prob * 100:.1f}%**")
                    st.progress(prob)
                    
                    st.markdown(f"#### Coercion Score: **{coercion * 100:.1f}%**")
                    st.progress(coercion)

                    # Match indicators
                    st.markdown("##### Triggered Indicators")
                    if result.spoofing_indicators_triggered:
                        for ind in result.spoofing_indicators_triggered:
                            st.info(f"🔹 {ind}")
                    else:
                        st.write("No anomalous network/media indicators triggered.")

                    st.markdown("#####  Matched Script Templates")
                    for tmpl in result.matched_script_templates:
                        st.warning(f" {tmpl}")

                    # MHA Alerts
                    if result.mha_alert_generated:
                        alert = result.alert_details
                        st.markdown(f"""
                        <div class="mha-alert-card">
                            <h3> OFFICIAL MHA CYBER WARNING</h3>
                            <p><strong>Alert ID:</strong> {alert.alert_id}</p>
                            <p><strong>Target Suspect ID:</strong> {alert.target_phone}</p>
                            <p><strong>Threat Severity:</strong> {alert.severity}</p>
                            <p><strong>Warning Trigger Reasons:</strong> {', '.join(alert.reasons)}</p>
                            <p><strong>System Action:</strong> Forwarded to Telecom blocklist and Cyber Cell units.</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.success(" Call flow does not meet severity threshold for official MHA cyber alerts.")
        else:
            st.info("Awaiting input data. Copy a sample script and click 'Evaluate Call Session Threat' to run.")

# -------------------------------------------------------------
# TAB 2: Counterfeit Currency Identification Agent
# -------------------------------------------------------------
with tab2:
    st.header(" FICN Counterfeit Note Inspector")
    st.markdown("Utilizes computer vision (OpenCV) to examine security threads, color-shifting, microprint details, and serial structures.")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader(" Banknote Scanning Portal")
        denomination = st.selectbox("Currency Denomination (INR)", [10, 20, 50, 100, 200, 500, 2000], index=5)
        
        uploaded_file = st.file_uploader("Upload Banknote Scan (Front Face)", type=["png", "jpg", "jpeg"])
        
        # Helper button to test with sample data if user has no image
        use_sample = st.button("Simulate Verification with Sample 500 INR Banknote Image")
        
        st.markdown("""
        > [!NOTE]
        > High-resolution images containing the security thread column (right-center) and the serial number box (bottom-right) produce optimal analysis.
        """)

    with col2:
        st.subheader("🔬 Verification Diagnostics")
        
        if uploaded_file or use_sample:
            with st.spinner("Analyzing physical security parameters..."):
                if uploaded_file:
                    file_bytes = uploaded_file.read()
                else:
                    # Create a mock green/blue shaded array to simulate a banknote image block for OpenCV
                    mock_img = np.zeros((300, 600, 3), dtype=np.uint8)
                    # Add green security thread vertical column
                    mock_img[:, 400:410, :] = [30, 200, 30] # Greenish thread
                    # Add serial box text area lines
                    cv2.putText(mock_img, "9BC 102938", (420, 280), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                    success, encoded_img = cv2.imencode('.png', mock_img)
                    file_bytes = encoded_img.tobytes()

                # Call Service
                if api_online:
                    try:
                        files = {'file': ('banknote.png', file_bytes, 'image/png')}
                        data = {'denomination': denomination}
                        res = httpx.post(f"{backend_url}/counterfeit/validate", data=data, files=files)
                        result = CurrencyValidationResponse(**res.json())
                    except Exception as ex:
                        st.warning(f"REST call failed: {ex}. Falling back to internal engine.")
                        import asyncio
                        result = asyncio.run(counterfeit_service.validate_banknote(file_bytes, denomination))
                else:
                    import asyncio
                    result = asyncio.run(counterfeit_service.validate_banknote(file_bytes, denomination))

                # Plot processed CV image
                # Decode image and show Canny edge detection representation next to original
                nparr = np.frombuffer(file_bytes, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                if img is not None:
                    edges = cv2.Canny(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), 50, 150)
                    
                    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
                    ax1.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
                    ax1.set_title("Original Scan")
                    ax1.axis('off')
                    ax2.imshow(edges, cmap='gray')
                    ax2.set_title("CV Security Edge Extractor")
                    ax2.axis('off')
                    st.pyplot(fig)

                # Verdict Callout
                prob = result.authenticity_probability
                if result.is_genuine:
                    st.success(f" **VERDICT: {result.system_verdict.upper()} (Genuine Likelihood: {prob*100:.1f}%)**")
                else:
                    st.error(f" **VERDICT: {result.system_verdict.upper()} (Genuine Likelihood: {prob*100:.1f}%)**")

                # Telemetry Cards
                metric_col1, metric_col2, metric_col3 = st.columns(3)
                
                with metric_col1:
                    thread_valid = "Continuous (Pass)" if result.security_thread.is_continuous else "Broken (Fail)"
                    st.metric("Security Thread Status", thread_valid, 
                              delta="1.0" if result.security_thread.is_continuous else "-1.0")
                    st.caption(f"Alignment Conf: {result.security_thread.alignment_confidence*100:.0f}%")
                    
                with metric_col2:
                    micro_valid = "Sharp (Pass)" if result.microprint.is_microprint_sharp else "Blurred (Fail)"
                    st.metric("Microprint Quality", micro_valid, 
                              delta="1.0" if result.microprint.is_microprint_sharp else "-1.0")
                    st.caption(f"Print Sharpness: {result.microprint.sharpness_score*100:.0f}%")
                    
                with metric_col3:
                    ocr_valid = result.ocr_result.extracted_serial_number
                    delta_ocr = "Format Match" if result.ocr_result.format_matches_rbi_standards else "Pattern Error"
                    st.metric("OCR Banknote Serial", ocr_valid, delta=delta_ocr)
                    st.caption(f"Blacklisted: {'YES' if result.ocr_result.is_blacklisted else 'NO'}")
        else:
            st.info("Upload a currency photo scan or click 'Simulate Verification' to run the CV diagnostic.")

# -------------------------------------------------------------
# TAB 3: Fraud Network Graph Intelligence
# -------------------------------------------------------------
with tab3:
    st.header(" Transaction & Fingerprint Linkage Graph")
    st.markdown("Exposes money laundering mule clusters, shared phone/IMEI rings, and generates signed evidence packages for litigation.")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader(" Load Entity / Edge to Live Graph")
        
        with st.form("add_node_form"):
            st.markdown("**Add Node Entity**")
            node_id = st.text_input("Unique Node Identifier", value="ACC-SUSPECT-888")
            node_type = st.selectbox("Node Classification Type", ["BANK_ACCOUNT", "DEVICE_FINGERPRINT", "PHONE_NUMBER", "IP_ADDRESS"])
            node_risk = st.slider("Known Risk Bias Score", 0.0, 1.0, 0.40)
            
            node_submit = st.form_submit_button("Inject Node")
            if node_submit:
                node = NodeData(id=node_id, type=node_type, risk_score=node_risk, attributes={"district": "Mewat"})
                fraud_network_service.add_entity_node(node)
                st.success(f"Node '{node_id}' successfully added.")

        with st.form("add_edge_form"):
            st.markdown("**Add Transaction/Link Relationship**")
            source_id = st.text_input("Source Node ID", value="ACC-SUSPECT-888")
            target_id = st.text_input("Target Node ID", value="ACC-MULE-L2-051")
            rel_type = st.selectbox("Relationship Connection", ["TRANSACTED_WITH", "SHARED_DEVICE", "LINKED_PHONE"])
            weight = st.number_input("Transaction Volume Amount (INR)", min_value=1.0, value=75000.0)
            
            edge_submit = st.form_submit_button("Inject Link")
            if edge_submit:
                edge = EdgeData(source=source_id, target=target_id, relationship=rel_type, weight=weight)
                fraud_network_service.add_transaction_edge(edge)
                st.success(f"Edge from '{source_id}' to '{target_id}' added.")

    with col2:
        st.subheader(" Network Visualizer & Legal Intelligence")
        
        # Plot NetworkX Graph
        fig, ax = plt.subplots(figsize=(8, 6))
        G = fraud_network_service.G
        pos = nx.spring_layout(G, seed=42)
        
        # Color code nodes by risk
        node_colors = []
        for n in G.nodes:
            r = G.nodes[n].get("risk_score", 0.0)
            if r > 0.8:
                node_colors.append('#ef4444')  # Red
            elif r > 0.5:
                node_colors.append('#f97316')  # Orange
            else:
                node_colors.append('#10b981')  # Green
                
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=600, ax=ax)
        nx.draw_networkx_labels(G, pos, font_size=8, font_color="white", ax=ax)
        
        # Categorize edge lines by type
        edges_trans = [(u, v) for u, v, d in G.edges(data=True) if d.get('relationship') == 'TRANSACTED_WITH']
        edges_device = [(u, v) for u, v, d in G.edges(data=True) if d.get('relationship') == 'SHARED_DEVICE']
        edges_phone = [(u, v) for u, v, d in G.edges(data=True) if d.get('relationship') == 'LINKED_PHONE']

        nx.draw_networkx_edges(G, pos, edgelist=edges_trans, edge_color='#60a5fa', style='solid', arrows=True, ax=ax)
        nx.draw_networkx_edges(G, pos, edgelist=edges_device, edge_color='#eab308', style='dashed', arrows=True, ax=ax)
        nx.draw_networkx_edges(G, pos, edgelist=edges_phone, edge_color='#ec4899', style='dotted', arrows=True, ax=ax)

        ax.set_facecolor('#0f172a')
        fig.patch.set_facecolor('#0f172a')
        plt.title("Syndicate Link Map (Green: Safe | Red: High Mule)", color="white")
        st.pyplot(fig)

        st.markdown("---")
        
        # Evidence Generation
        st.markdown("##### Court-Admissible Intelligence Package Builder")
        target_acc = st.selectbox("Select Target Suspect Entity", list(G.nodes))
        
        if st.button("Generate Case Evidence Report"):
            evidence = fraud_network_service.generate_court_evidence(target_acc)
            
            st.markdown(f"**Case File ID:** `{evidence.case_id}` | **Syndicate ID:** `{evidence.suspect_ring_id}`")
            st.markdown(f"**SHA-256 Digital Signature:** `{evidence.digital_signature}`")
            st.markdown("**Forensic Legal Narrative:**")
            st.markdown(f"""
            <div class="memo-box">
{evidence.legal_memorandum_text}
            </div>
            """, unsafe_allow_html=True)

# -------------------------------------------------------------
# TAB 4: Geospatial Crime Pattern Intelligence
# -------------------------------------------------------------
with tab4:
    st.header(" Geospatial Patrol Vector Optimization")
    st.markdown("Coordinates spatial clusters of ATM cashouts, fraud call centers, and maps optimized patrol routes for police units.")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader(" Report Geographic Crime Incident")
        
        with st.form("report_incident_form"):
            inc_id = st.text_input("Incident Identifier", value=f"INC-{uuid.uuid4().hex[:4].upper()}")
            lat = st.number_input("Latitude", value=28.1220, format="%.4f")
            lng = st.number_input("Longitude", value=77.0180, format="%.4f")
            c_type = st.selectbox("Incident Threat Category", ["scammer_den_call_center", "mule_atm_withdrawal", "counterfeit_circulation"])
            district = st.text_input("Administrative Police District", value="Nuh")
            state = st.text_input("Indian State", value="Haryana")
            loss = st.number_input("Financial Loss (INR)", min_value=0.0, value=250000.0)
            
            inc_submit = st.form_submit_button("Register Incident Coordinates")
            if inc_submit:
                point = IncidentPoint(
                    incident_id=inc_id,
                    latitude=lat,
                    longitude=lng,
                    crime_type=c_type,
                    district=district,
                    state=state,
                    reported_timestamp=datetime.utcnow(),
                    financial_impact_inr=loss
                )
                geospatial_service.report_incident(point)
                st.success(f"Incident {inc_id} logged at ({lat}, {lng}) successfully.")

    with col2:
        st.subheader(" Hotspot Visualization & Routing Leg Optimizer")
        
        # Load incident dataset to display on map
        inc_data = []
        for inc in geospatial_service.incidents:
            inc_data.append({
                "latitude": inc.latitude,
                "longitude": inc.longitude,
                "crime": inc.crime_type,
                "loss": inc.financial_impact_inr
            })
        df_map = pd.DataFrame(inc_data)
        
        # Render Streamlit map
        st.map(df_map)
        
        # Optimize Routes
        st.markdown("##### Traveling Salesperson (TSP) Patrol Optimizer")
        start_lat = st.number_input("Police Station Dispatch Latitude", value=28.1300, format="%.4f")
        start_lng = st.number_input("Police Station Dispatch Longitude", value=77.0000, format="%.4f")
        target_dist = st.text_input("Patrol Focus District", value="Nuh")
        
        if st.button("Generate Optimized Route Leg Summary"):
            route = geospatial_service.optimize_patrol_vectors(start_lat, start_lng, target_dist)
            
            st.write(f"**Route Identifier:** `{route.route_id}` | **Alert Level:** `{route.alert_level}`")
            st.write(f"**Total Distance:** `{route.total_distance_km} KM` | **Estimated Duration:** `{route.estimated_duration_minutes} Mins` (inc. inspections)")
            
            # Convert waypoints to dataframe for display
            if route.waypoints:
                wp_data = []
                for wp in route.waypoints:
                    wp_data.append({
                        "Leg": wp.sequence,
                        "Latitude": wp.latitude,
                        "Longitude": wp.longitude,
                        "Action Item": wp.action_item
                    })
                st.table(pd.DataFrame(wp_data))
            else:
                st.warning("No nearby hotspots detected in target zone.")

# -------------------------------------------------------------
# TAB 5: Citizen Fraud Shield
# -------------------------------------------------------------
with tab5:
    st.header(" Citizen Threat Shield")
    st.markdown("Immediate threat evaluation of SMS messages, link queries, or caller claims, translated across 12 Indian regional languages.")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader(" Suspicious Communication Input")
        
        lang_selection = st.selectbox(
            "Select Preferred Communication Language",
            [
                ("English (en)", "en"),
                ("Hindi (hi)", "hi"),
                ("Tamil (ta)", "ta"),
                ("Telugu (te)", "te"),
                ("Bengali (bn)", "bn"),
                ("Marathi (mr)", "mr"),
                ("Kannada (kn)", "kn"),
                ("Gujarati (gu)", "gu"),
                ("Malayalam (ml)", "ml"),
                ("Punjabi (pa)", "pa"),
                ("Odia (or)", "or"),
                ("Assamese (as)", "as")
            ]
        )
        
        medium = st.selectbox("Inbound Channel Medium", ["SMS", "WHATSAPP", "PHONE_CALL", "UPI_ID", "WEBSITE_URL"])
        sender = st.text_input("Sender Identification (Number/UPI/Link)", value="SBI-URGENT-UPDATE")
        
        # Test templates
        st.markdown("**Sample Alerts (Copy to query box):**")
        st.code("Dear customer, your power bill is pending. To avoid immediate cut-off, pay immediately through our agent desk or update your verification profile here: http://electricity-bill-pay.com/", language="text")
        st.code("Congratulation! You selected for work from home part time job. Earn 5000 per day by clicking youtube links. Message on WhatsApp 9822334400 to join.", language="text")

        query_text = st.text_area(
            "Suspicious Alert Message Content",
            value="",
            placeholder="Paste text contents from SMS, WhatsApp, or details of calls here..."
        )
        
        shield_btn = st.button("Evaluate Alert Risk", type="primary")

    with col2:
        st.subheader(" Risk Advisory & NCRB Submission Guide")
        
        if shield_btn:
            if not query_text:
                st.error("Please enter a suspicious message to analyze.")
            else:
                with st.spinner("Analyzing message risk level..."):
                    payload = CitizenRiskQuery(
                        query_id=f"CITIZEN-{uuid.uuid4().hex[:6].upper()}",
                        query_text=query_text,
                        input_medium=medium,
                        sender_identifier=sender,
                        language_code=lang_selection[1]
                    )

                    # REST or Direct Call
                    if api_online:
                        try:
                            res = httpx.post(f"{backend_url}/citizen-shield/query", json=payload.model_dump())
                            result = res.json()
                            
                            # Parse into variables for rendering
                            risk_level = result["risk_level"]
                            risk_score = result["risk_score"]
                            detected_type = result["detected_scam_type"]
                            risk_factors = result["risk_factors"]
                            advisory = result["dynamic_advisory"]
                            ncrb = result["ncrb_guide"]
                        except Exception as ex:
                            st.warning(f"REST call failed: {ex}. Falling back to internal engine.")
                            import asyncio
                            res = asyncio.run(citizen_shield_service.evaluate_risk(payload))
                            risk_level = res.risk_level
                            risk_score = res.risk_score
                            detected_type = res.detected_scam_type
                            risk_factors = res.risk_factors
                            advisory = res.dynamic_advisory
                            ncrb = res.ncrb_guide
                    else:
                        import asyncio
                        res = asyncio.run(citizen_shield_service.evaluate_risk(payload))
                        risk_level = res.risk_level
                        risk_score = res.risk_score
                        detected_type = res.detected_scam_type
                        risk_factors = res.risk_factors
                        advisory = res.dynamic_advisory
                        ncrb = res.ncrb_guide

                    # Color-coded display of risk
                    if risk_level in ["CRITICAL", "HIGH_RISK"]:
                        st.error(f"🚨 **ALERT LEVEL: {risk_level} (Threat Score: {risk_score*100:.1f}%)**")
                    elif risk_level == "SUSPICIOUS":
                        st.warning(f"⚠️ **ALERT LEVEL: {risk_level} (Threat Score: {risk_score*100:.1f}%)**")
                    else:
                        st.success(f"✅ **ALERT LEVEL: {risk_level} (Threat Score: {risk_score*100:.1f}%)**")

                    if detected_type:
                        st.markdown(f"**Detected Vector:** {detected_type}")

                    # Injected translated safety advisory
                    st.markdown("##### Translated Safety Advisory:")
                    st.info(advisory)

                    # List anomalies
                    if risk_factors:
                        st.markdown("**Detected Threat Anomalies:**")
                        for fact in risk_factors:
                            st.markdown(f"- `{fact}`")

                    # Pre-filled NCRB copy box
                    st.markdown("---")
                    st.markdown("##### NCRB Cybercrime Portal Reporting Template")
                    st.caption("We have pre-filled and structured your complaint. Copy and paste this directly onto the National Cyber Crime Reporting Portal (cybercrime.gov.in) to report the scammer.")
                    
                    st.text_input("NCRB Category", value=ncrb.portal_category if hasattr(ncrb, 'portal_category') else ncrb['portal_category'], disabled=True)
                    st.text_input("NCRB Subcategory", value=ncrb.portal_subcategory if hasattr(ncrb, 'portal_subcategory') else ncrb['portal_subcategory'], disabled=True)
                    st.text_area("Draft Complaint Narrative", value=ncrb.draft_complaint_text if hasattr(ncrb, 'draft_complaint_text') else ncrb['draft_complaint_text'], height=150)
                    
                    st.markdown("**Suggested Attachments:**")
                    attachments = ncrb.suggested_evidence_attachments if hasattr(ncrb, 'suggested_evidence_attachments') else ncrb['suggested_evidence_attachments']
                    for att in attachments:
                        st.markdown(f"- 📂 {att}")
        else:
            st.info("Provide alert details or select a sample copy template, then click 'Evaluate Alert Risk'.")
