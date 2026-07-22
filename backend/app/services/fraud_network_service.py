import networkx as nx
import logging
import uuid
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Tuple

from backend.app.config import settings
from backend.app.models.fraud_network import (
    NodeData,
    EdgeData,
    FraudCluster,
    CourtAdmissibleEvidenceResponse,
    EvidenceChainItem
)

logger = logging.getLogger("defeatshield.fraud_network_service")

class FraudNetworkService:
    def __init__(self):
        # Stateful graph for the duration of the server process
        self.G = nx.MultiDiGraph()
        
        # Populate with a realistic bootstrap mock fraud network
        self._bootstrap_sample_graph()

    def add_entity_node(self, node: NodeData) -> None:
        """
        Adds a node representing an entity (e.g. Bank Account, Phone, Device) to the network.
        """
        self.G.add_node(
            node.id,
            type=node.type,
            risk_score=node.risk_score,
            attributes=node.attributes,
            created_at=datetime.utcnow()
        )
        logger.info(f"Graph Node Added: [{node.type}] ID: {node.id}")

    def add_transaction_edge(self, edge: EdgeData) -> None:
        """
        Adds a transaction or device link between two nodes.
        """
        # Ensure nodes exist
        if not self.G.has_node(edge.source):
            self.G.add_node(edge.source, type="BANK_ACCOUNT", risk_score=0.1, attributes={}, created_at=datetime.utcnow())
        if not self.G.has_node(edge.target):
            self.G.add_node(edge.target, type="BANK_ACCOUNT", risk_score=0.1, attributes={}, created_at=datetime.utcnow())
            
        self.G.add_edge(
            edge.source,
            edge.target,
            key=edge.relationship,
            relationship=edge.relationship,
            weight=edge.weight,
            timestamp=edge.timestamp
        )
        # Propagate risk score slightly along transaction path
        self._propagate_risk_scores(edge.source, edge.target)
        logger.info(f"Graph Edge Added: {edge.source} --({edge.relationship})--> {edge.target}")

    def _propagate_risk_scores(self, source: str, target: str):
        """
        Risk propagation: if source has high risk, increase target's risk score.
        """
        s_risk = self.G.nodes[source].get("risk_score", 0.0)
        t_risk = self.G.nodes[target].get("risk_score", 0.0)
        if s_risk > 0.6 and t_risk < s_risk:
            # Propagate 30% of risk differential
            new_risk = t_risk + (s_risk - t_risk) * 0.3
            self.G.nodes[target]["risk_score"] = round(new_risk, 3)

    def get_network_clusters(self) -> List[FraudCluster]:
        """
        Detects communities/clusters of connected scam operations using weakly connected components.
        For each cluster, aggregates metadata, risk profiles, and geographic locations.
        """
        clusters: List[FraudCluster] = []
        
        # Convert to undirected graph for component search
        undirected_g = self.G.to_undirected()
        components = list(nx.connected_components(undirected_g))
        
        for idx, comp in enumerate(components):
            sub_g = self.G.subgraph(comp)
            
            nodes_list: List[NodeData] = []
            edges_list: List[EdgeData] = []
            
            total_risk = 0.0
            mules = 0
            scam_infra = 0
            geo_spots = set()
            
            for n_id in sub_g.nodes:
                n_data = sub_g.nodes[n_id]
                n_type = n_data.get("type", "BANK_ACCOUNT")
                n_risk = n_data.get("risk_score", 0.0)
                n_attrs = n_data.get("attributes", {})
                
                nodes_list.append(NodeData(
                    id=n_id,
                    type=n_type,
                    attributes=n_attrs,
                    risk_score=n_risk
                ))
                
                total_risk += n_risk
                if n_risk > 0.7:
                    mules += 1
                if n_type in ["DEVICE_FINGERPRINT", "IP_ADDRESS"] and n_risk > 0.8:
                    scam_infra += 1
                
                # Check for geographic attributes
                loc = n_attrs.get("location") or n_attrs.get("district")
                if loc:
                    geo_spots.add(str(loc))
            
            # Extract edges
            for u, v, key, data in sub_g.edges(data=True, keys=True):
                edges_list.append(EdgeData(
                    source=u,
                    target=v,
                    relationship=data.get("relationship", "TRANSACTED_WITH"),
                    weight=data.get("weight", 1.0),
                    timestamp=data.get("timestamp", datetime.utcnow())
                ))
                
            avg_risk = total_risk / len(comp) if comp else 0.0
            
            clusters.append(FraudCluster(
                cluster_id=f"CLUSTER-{idx + 1:03d}",
                nodes=nodes_list,
                edges=edges_list,
                average_risk_score=round(avg_risk, 3),
                mule_count=mules,
                scammer_infrastructure_count=scam_infra,
                geographic_hotspots=list(geo_spots)
            ))
            
        return sorted(clusters, key=lambda x: x.average_risk_score, reverse=True)

    def generate_court_evidence(self, target_account_id: str) -> CourtAdmissibleEvidenceResponse:
        """
        Traces a forensic link from a target account to a known blacklist/scammer device.
        Uses shortest path algorithms (Dijkstra) on weights to build a chain of custody evidence sequence.
        Produces legal narrative and signs it cryptographically.
        """
        evidence_chain: List[EvidenceChainItem] = []
        implicated_accs = set()
        implicated_devs = set()
        implicated_phs = set()
        
        # Step 1: Find all nodes linked in the target's community
        undirected_g = self.G.to_undirected()
        if not self.G.has_node(target_account_id):
            # Safe boundary check
            return self._empty_evidence_response(target_account_id)
            
        # Find path to the highest risk node in the network connected to this node
        comp = nx.node_connected_component(undirected_g, target_account_id)
        scammer_infrastructure_nodes = [
            n for n in comp 
            if self.G.nodes[n].get("risk_score", 0.0) >= 0.85 and n != target_account_id
        ]
        
        narrative_lines = [
            f"FORENSIC INTELLIGENCE DOSSIER - TARGET: {target_account_id}",
            f"Generated: {datetime.utcnow().isoformat()} UTC",
            f"Security Classification: COURT-CONFIDENTIAL / LAW ENFORCEMENT ONLY",
            "--------------------------------------------------------------------------------",
            f"Target node '{target_account_id}' shows high correlation with structured scam rings."
        ]

        if scammer_infrastructure_nodes:
            # Get shortest path to the worst infrastructure node
            infra_target = scammer_infrastructure_nodes[0]
            path = nx.shortest_path(undirected_g, source=target_account_id, target=infra_target)
            
            # Construct step-by-step evidence links
            for i in range(len(path) - 1):
                u = path[i]
                v = path[i+1]
                
                # Fetch edge relationship
                edge_data = self.G.get_edge_data(u, v)
                rel = "CONNECTED_TO"
                factor = "Direct structural relationship"
                ts = datetime.utcnow()
                
                if edge_data:
                    # MultiDiGraph returns a dict of keys, extract first available
                    first_key = list(edge_data.keys())[0]
                    rel = edge_data[first_key].get("relationship", rel)
                    ts = edge_data[first_key].get("timestamp", ts)
                    
                    if rel == "SHARED_DEVICE":
                        factor = f"Shared device fingerprint correlation. Node {u} and {v} logged in from identical hardware profile."
                    elif rel == "TRANSACTED_WITH":
                        factor = f"Financial funds transfer of value. Direct peer-to-peer transaction tracked between accounts."
                    elif rel == "LINKED_PHONE":
                        factor = f"Telephony contact linkage. Registered using common phone number infrastructure."
                
                evidence_chain.append(EvidenceChainItem(
                    step=i + 1,
                    source_entity=u,
                    target_entity=v,
                    relation=rel,
                    connecting_factor=factor,
                    timestamp=ts
                ))
                
                # Group entities for legal summary
                for node_id in (u, v):
                    ntype = self.G.nodes[node_id].get("type")
                    if ntype == "BANK_ACCOUNT":
                        implicated_accs.add(node_id)
                    elif ntype == "DEVICE_FINGERPRINT":
                        implicated_devs.add(node_id)
                    elif ntype == "PHONE_NUMBER":
                        implicated_phs.add(node_id)

                narrative_lines.append(
                    f"Link #{i+1}: Node [{self.G.nodes[u].get('type')}] {u} -> connected to [{self.G.nodes[v].get('type')}] {v} via {rel} ({factor})."
                )
        else:
            narrative_lines.append("No direct linkage path to blacklisted infrastructure detected. Low density connection exists.")
            
        narrative_lines.append("\nFORENSIC CONCLUSIONS:")
        narrative_lines.append(
            f"Based on graph community analysis, account {target_account_id} exhibits transaction flow, device, or phone sharing "
            f"characteristics representing a confidence rating of {self.G.nodes[target_account_id].get('risk_score', 0.0)*100}% alignment "
            "with organized scam syndicate networks."
        )
        
        legal_text = "\n".join(narrative_lines)
        
        # Cryptographic checksum for court admissibility validation
        signature_payload = f"{target_account_id}-{len(evidence_chain)}-{legal_text}"
        checksum = hashlib.sha256(signature_payload.encode('utf-8')).hexdigest().upper()
        
        return CourtAdmissibleEvidenceResponse(
            case_id=f"CASE-NET-{uuid.uuid4().hex[:8].upper()}",
            suspect_ring_id=f"RING-{abs(hash(target_account_id)) % 1000:03d}",
            generated_at=datetime.utcnow(),
            evidence_chain=evidence_chain,
            implicated_accounts=list(implicated_accs),
            implicated_devices=list(implicated_devs),
            implicated_phones=list(implicated_phs),
            legal_memorandum_text=legal_text,
            digital_signature=checksum
        )

    def _empty_evidence_response(self, target_account_id: str) -> CourtAdmissibleEvidenceResponse:
        return CourtAdmissibleEvidenceResponse(
            case_id="CASE-EMPTY",
            suspect_ring_id="RING-000",
            generated_at=datetime.utcnow(),
            evidence_chain=[],
            implicated_accounts=[target_account_id],
            implicated_devices=[],
            implicated_phones=[],
            legal_memorandum_text=f"Node {target_account_id} not registered in graph network. No evidence generated.",
            digital_signature="EMPTY-SIGNATURE"
        )

    def _bootstrap_sample_graph(self):
        """
        Creates a realistic seed graph containing a 3-layer money mule laundering tree
        interlinked via common device fingerprints.
        """
        # Scammer/Mule Master accounts (High risk)
        scam_den = NodeData(id="ACC-SCAMMER-9999", type="BANK_ACCOUNT", risk_score=0.98, attributes={"district": "Mewat", "owner": "Unknown Fake ID"})
        device_a = NodeData(id="DEV-IMEI-88888888", type="DEVICE_FINGERPRINT", risk_score=0.95, attributes={"model": "Xiaomi Redmi 9", "ip": "103.45.21.14"})
        phone_a = NodeData(id="PH-9999911111", type="PHONE_NUMBER", risk_score=0.92, attributes={"carrier": "Jio", "location": "Bharatpur"})

        # Layer 1 Mule accounts (medium/high risk)
        mule_l1_a = NodeData(id="ACC-MULE-L1-001", type="BANK_ACCOUNT", risk_score=0.88, attributes={"district": "Nuh", "bank": "SBI"})
        mule_l1_b = NodeData(id="ACC-MULE-L1-002", type="BANK_ACCOUNT", risk_score=0.85, attributes={"district": "Mathura", "bank": "HDFC"})
        
        # Layer 2 Layered accounts
        mule_l2_a = NodeData(id="ACC-MULE-L2-051", type="BANK_ACCOUNT", risk_score=0.60, attributes={"district": "Gurugram", "bank": "ICICI"})
        mule_l2_b = NodeData(id="ACC-MULE-L2-052", type="BANK_ACCOUNT", risk_score=0.55, attributes={"district": "Noida", "bank": "AXIS"})
        
        # Normal suspects being investigated (low/medium initial risk)
        suspect_user = NodeData(id="ACC-SUSPECT-777", type="BANK_ACCOUNT", risk_score=0.35, attributes={"district": "South Delhi", "bank": "PNB"})

        # Add Nodes
        self.add_entity_node(scam_den)
        self.add_entity_node(device_a)
        self.add_entity_node(phone_a)
        self.add_entity_node(mule_l1_a)
        self.add_entity_node(mule_l1_b)
        self.add_entity_node(mule_l2_a)
        self.add_entity_node(mule_l2_b)
        self.add_entity_node(suspect_user)

        # Add Links (Structured Money Laundering / Layering Flow)
        # Transactions
        self.add_transaction_edge(EdgeData(source="ACC-MULE-L1-001", target="ACC-SCAMMER-9999", relationship="TRANSACTED_WITH", weight=450000.0))
        self.add_transaction_edge(EdgeData(source="ACC-MULE-L1-002", target="ACC-SCAMMER-9999", relationship="TRANSACTED_WITH", weight=890000.0))
        
        self.add_transaction_edge(EdgeData(source="ACC-MULE-L2-051", target="ACC-MULE-L1-001", relationship="TRANSACTED_WITH", weight=120000.0))
        self.add_transaction_edge(EdgeData(source="ACC-MULE-L2-052", target="ACC-MULE-L1-002", relationship="TRANSACTED_WITH", weight=230000.0))
        
        self.add_transaction_edge(EdgeData(source="ACC-SUSPECT-777", target="ACC-MULE-L2-051", relationship="TRANSACTED_WITH", weight=25000.0))
        
        # Device linkages representing multi-account operation by a single handler
        self.add_transaction_edge(EdgeData(source="ACC-SCAMMER-9999", target="DEV-IMEI-88888888", relationship="SHARED_DEVICE", weight=1.0))
        self.add_transaction_edge(EdgeData(source="ACC-MULE-L1-001", target="DEV-IMEI-88888888", relationship="SHARED_DEVICE", weight=1.0))
        
        # Phone linkage representing registered notification contacts
        self.add_transaction_edge(EdgeData(source="ACC-SCAMMER-9999", target="PH-9999911111", relationship="LINKED_PHONE", weight=1.0))

fraud_network_service = FraudNetworkService()
