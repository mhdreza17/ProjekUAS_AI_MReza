"""
ReguBot Multi-Agent System
==========================

Sistem AI Multi-Agent untuk Analisis Compliance Dokumen Digital

Agents:
- DocumentCollectorAgent: Mengumpulkan dan memproses dokumen
- StandardRetrieverAgent: Mengelola database standar regulasi  
- ComplianceCheckerAgent: Menganalisis kepatuhan dokumen
- ReportGeneratorAgent: Membuat laporan audit
- QAAgent: Menjawab pertanyaan pengguna
- AgentCoordinator: Mengkoordinasi semua agent
"""

import os
import logging
from typing import Dict, List, Any, Optional

# Setup logging untuk agents
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Konfigurasi default sistem
DEFAULT_CONFIG = {
    'groq_api_key': os.getenv('GROQ_API_KEY'),
    'vector_db_path': os.getenv('VECTOR_DB_PATH', 'vector_db'),
    'max_file_size': int(os.getenv('MAX_CONTENT_LENGTH', 10485760)),  # 10MB
    'supported_formats': ['.pdf', '.docx', '.txt'],
    'standards_path': 'standards',
    'upload_path': 'uploads',
    'reports_path': 'reports'
}

# Status sistem global
SYSTEM_STATUS = {
    'initialized': False,
    'agents_ready': False,
    'vector_db_ready': False,
    'standards_loaded': False,
    'last_update': None
}

# Registry agent aktif
ACTIVE_AGENTS = {}

def initialize_system():
    """Inisialisasi sistem ReguBot"""
    try:
        logger.info("🤖 Inisialisasi ReguBot Multi-Agent System...")
       
        # Buat direktori utama jika belum ada
        for path in ['uploads', 'reports', 'standards', 'vector_db']:
            os.makedirs(path, exist_ok=True)
        logger.info("✅ Semua direktori utama siap.")
        SYSTEM_STATUS['initialized'] = True
        SYSTEM_STATUS['last_update'] = os.times()
        logger.info("🚀 ReguBot siap digunakan di http://localhost:5000 (local & offline)")
        return True
    except Exception as e:
        logger.error(f"❌ Gagal inisialisasi sistem: {str(e)}")
        return False

def get_system_status() -> Dict[str, Any]:
    """Mendapatkan status sistem saat ini"""
    return SYSTEM_STATUS.copy()

def register_agent(agent_name: str, agent_instance: Any):
    """Mendaftarkan agent ke registry"""
    ACTIVE_AGENTS[agent_name] = agent_instance
    logger.info(f"🔧 Agent {agent_name} terdaftar")

def get_agent(agent_name: str) -> Optional[Any]:
    """Mendapatkan instance agent berdasarkan nama"""
    return ACTIVE_AGENTS.get(agent_name)

def get_config(key: str = None) -> Any:
    """Mendapatkan konfigurasi sistem"""
    if key:
        return DEFAULT_CONFIG.get(key)
    return DEFAULT_CONFIG.copy()

# Auto-initialize saat import
if not SYSTEM_STATUS['initialized']:
    initialize_system()

# Export semua agent classes
try:
    from .document_collector import DocumentCollectorAgent
    from .standard_retriever import StandardRetrieverAgent  
    from .compliance_checker import ComplianceCheckerAgent
    from .report_generator import ReportGeneratorAgent
    from .qa_agent import QAAgent
    from .agent_coordinator import AgentCoordinator
    from .base_agent import BaseAgent
    
    logger.info("📦 Semua agent classes berhasil diimport")
    SYSTEM_STATUS['agents_ready'] = True
    
except ImportError as e:
    logger.error(f"❌ Gagal import agent classes: {str(e)}")
    SYSTEM_STATUS['agents_ready'] = False

# Expose public API
__all__ = [
    'DocumentCollectorAgent',
    'StandardRetrieverAgent', 
    'ComplianceCheckerAgent',
    'ReportGeneratorAgent',
    'QAAgent',
    'AgentCoordinator',
    'BaseAgent',
    'initialize_system',
    'get_system_status',
    'register_agent',
    'get_agent',
    'get_config',
    'DEFAULT_CONFIG',
    'SYSTEM_STATUS'
]

logger.info("🚀 ReguBot Multi-Agent System siap digunakan!")
