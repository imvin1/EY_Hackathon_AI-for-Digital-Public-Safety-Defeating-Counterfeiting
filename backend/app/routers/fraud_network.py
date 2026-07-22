from fastapi import APIRouter, HTTPException, status, Query
from typing import List
from backend.app.models.fraud_network import (
    NodeData,
    EdgeData,
    FraudCluster,
    CourtAdmissibleEvidenceResponse
)
from backend.app.services.fraud_network_service import fraud_network_service
import logging

router = APIRouter(prefix="/fraud-network", tags=["Fraud Network Graph Intelligence"])
logger = logging.getLogger("defeatshield.routers.fraud_network")

@router.post(
    "/nodes", 
    status_code=status.HTTP_201_CREATED,
    summary="Add Entity Node to Graph Network",
    description="Registers an entity node (Bank Account, Device, Phone, or IP) into the graph analyzer database."
)
async def add_entity_node(node: NodeData):
    try:
        fraud_network_service.add_entity_node(node)
        return {"status": "success", "message": f"Entity node '{node.id}' successfully registered."}
    except Exception as e:
        logger.error(f"Failed to add entity node: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Graph database write error: {str(e)}"
        )

@router.post(
    "/edges", 
    status_code=status.HTTP_201_CREATED,
    summary="Add Transaction/Relationship Link to Graph",
    description="Establishes a link (financial transaction, shared hardware fingerprint, or common phone number registration) between two graph entities."
)
async def add_transaction_edge(edge: EdgeData):
    try:
        fraud_network_service.add_transaction_edge(edge)
        return {"status": "success", "message": f"Relationship link between '{edge.source}' and '{edge.target}' established."}
    except Exception as e:
        logger.error(f"Failed to add transaction edge: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Graph database relationship write error: {str(e)}"
        )

@router.get(
    "/clusters", 
    response_model=List[FraudCluster], 
    status_code=status.HTTP_200_OK,
    summary="List Detected Organized Fraud Ring Clusters",
    description="Analyzes the global graph database and extracts weakly connected component clusters, identifying money mule rings and common scam infrastructure."
)
async def get_network_clusters():
    try:
        clusters = fraud_network_service.get_network_clusters()
        return clusters
    except Exception as e:
        logger.error(f"Failed to calculate network clusters: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Graph clustering algorithm execution failed: {str(e)}"
        )

@router.get(
    "/evidence/{account_id}", 
    response_model=CourtAdmissibleEvidenceResponse, 
    status_code=status.HTTP_200_OK,
    summary="Generate Court-Admissible Forensic Evidence Package",
    description="Traces path from target suspect node to blacklisted entities, builds chronological legal narrative chain-of-custody, and issues a SHA-256 digital signature."
)
async def get_court_evidence(account_id: str):
    try:
        evidence = fraud_network_service.generate_court_evidence(account_id)
        if evidence.case_id == "CASE-EMPTY":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Account ID '{account_id}' not found in the transaction graph database."
            )
        return evidence
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Failed to build forensic package for {account_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Forensic intelligence package generation error: {str(e)}"
        )
