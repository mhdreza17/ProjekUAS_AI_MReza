from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
import os
import json
import uuid
from datetime import datetime
from dotenv import load_dotenv

# Import enhanced agents
from agents.document_collector import DocumentCollectorAgent
from agents.compliance_checker import ComplianceCheckerAgent
from agents.standard_retriever import StandardRetrieverAgent
from agents.report_generator import ReportGeneratorAgent
from agents.qa_agent import QAAgent
from agents.agent_coordinator import AgentCoordinator

import logging
import traceback

os.environ['ANONYMIZED_TELEMETRY'] = 'False'
os.environ['CHROMA_CLIENT_AUTH_PROVIDER'] = ''

load_dotenv()

# Enhanced logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enhanced_app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
REPORTS_FOLDER = 'reports'
STANDARDS_FOLDER = 'standards'

for folder in [UPLOAD_FOLDER, REPORTS_FOLDER, STANDARDS_FOLDER]:
    os.makedirs(folder, exist_ok=True)

# Enhanced GROQ API validation
groq_api_key = os.getenv('GROQ_API_KEY')
if not groq_api_key:
    logger.error("⚠️  GROQ_API_KEY tidak ditemukan!")
    print("📝 Silakan set GROQ_API_KEY di file .env atau environment variable")
    print("🔗 Dapatkan API key di: https://console.groq.com/")
    print("💡 Contoh: GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
else:
    logger.info("✅ GROQ_API_KEY berhasil dimuat")
    print("✅ GROQ_API_KEY berhasil dimuat")

# Enhanced standards validation
def validate_standards_directory():
    """Enhanced validation of standards directory"""
    standards_status = {}
    expected_standards = {
        'Global': ['GDPR.pdf', 'NIST.pdf'],
        'Nasional': ['UU_PDP.pdf', 'POJK.pdf', 'BSSN_A.pdf', 'BSSN_B.pdf', 'BSSN_C.pdf']
    }
    
    missing_files = []
    
    for category, files in expected_standards.items():
        category_path = os.path.join(STANDARDS_FOLDER, category)
        if os.path.exists(category_path):
            existing_files = [f for f in os.listdir(category_path) if f.endswith('.pdf')]
            standards_status[category] = {
                'exists': True,
                'files': existing_files,
                'count': len(existing_files)
            }
            
            for expected_file in files:
                if expected_file not in existing_files:
                    missing_files.append(f"{category}/{expected_file}")
            
            logger.info(f"📁 {category} standards: {len(existing_files)} files found")
        else:
            standards_status[category] = {
                'exists': False,
                'files': [],
                'count': 0
            }
            missing_files.extend([f"{category}/{f}" for f in files])
            logger.warning(f"⚠️  {category} standards directory not found")
    
    if missing_files:
        logger.warning(f"⚠️  Missing standard files: {', '.join(missing_files[:10])}")
    else:
        logger.info("✅ All expected standard files found")
    
    return standards_status, missing_files

standards_status, missing_files = validate_standards_directory()

# Enhanced coordinator initialization - FIXED VERSION
_coordinator = None

def get_coordinator():
    """Get coordinator instance with enhanced error handling - FIXED VERSION"""
    global _coordinator
    try:
        if _coordinator is None:
            logger.info("Initializing Enhanced AgentCoordinator...")
            _coordinator = AgentCoordinator()
            logger.info("✅ Enhanced AgentCoordinator initialized successfully")
        return _coordinator
    except Exception as e:
        logger.error(f"Failed to initialize Enhanced AgentCoordinator: {str(e)}")
        logger.error(traceback.format_exc())
        raise

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/health')
def health_check():
    """Enhanced health check with detailed system status"""
    try:
        coordinator_status = "unknown"
        try:
            coordinator = get_coordinator()
            coordinator_status = "healthy"
        except:
            coordinator_status = "failed"
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': 'ReguBot Enhanced v2.1 - FIXED',
            'system_components': {
                'groq_api_available': bool(groq_api_key),
                'coordinator_status': coordinator_status,
                'standards_status': standards_status,
                'missing_files': missing_files if missing_files else None,
                'directories': {
                    'uploads': os.path.exists(UPLOAD_FOLDER),
                    'reports': os.path.exists(REPORTS_FOLDER),
                    'standards': os.path.exists(STANDARDS_FOLDER)
                }
            },
            'features': {
                'adaptive_analysis': True,
                'confidence_scoring': True,
                'enhanced_reporting': True,
                'context_aware_qa': True,
                'multi_standard_support': True,
                'persistent_sessions': True,
                'fixed_qa_agent': True,
                'improved_session_management': True
            }
        })
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/upload', methods=['POST'])
def upload_document():
    """Enhanced document upload with better validation"""
    try:
        logger.info("📁 Enhanced document upload request received")
        
        if 'file' not in request.files:
            logger.warning("Upload failed: No file in request")
            return jsonify({'error': 'Tidak ada file yang diupload'}), 400
        
        file = request.files['file']
        if file.filename == '':
            logger.warning("Upload failed: Empty filename")
            return jsonify({'error': 'Nama file kosong'}), 400
        
        # Enhanced file validation
        allowed_extensions = {'pdf', 'docx', 'txt'}
        file_extension = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        
        if file_extension not in allowed_extensions:
            logger.warning(f"Upload failed: Invalid file type: {file_extension}")
            return jsonify({
                'error': f'Tipe file tidak didukung. Hanya mendukung: {", ".join(allowed_extensions)}'
            }), 400
        
        # Enhanced file size validation
        file.seek(0, 2)
        file_size = file.tell()
        file.seek(0)
        
        max_size = 15 * 1024 * 1024
        if file_size > max_size:
            logger.warning(f"Upload failed: File too large: {file_size} bytes")
            return jsonify({
                'error': f'File terlalu besar. Maksimal {max_size//1024//1024}MB'
            }), 400
        
        # Generate session ID and save file
        session_id = str(uuid.uuid4())
        safe_filename = f"{session_id}_{file.filename}"
        filepath = os.path.join(UPLOAD_FOLDER, safe_filename)
        
        file.save(filepath)
        
        # Verify file was saved correctly
        if not os.path.exists(filepath):
            logger.error("File save failed: File not found after save")
            return jsonify({'error': 'Gagal menyimpan file'}), 500
        
        actual_size = os.path.getsize(filepath)
        logger.info(f"✅ Enhanced upload successful: {safe_filename} ({actual_size} bytes)")
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'filename': safe_filename,
            'original_filename': file.filename,
            'file_size': actual_size,
            'file_type': file_extension,
            'message': 'File berhasil diupload dengan sistem enhanced validation',
            'enhanced_features': {
                'adaptive_analysis_ready': True,
                'multi_standard_support': True,
                'confidence_scoring': True,
                'persistent_qa_context': True,
                'fixed_qa_processing': True
            }
        })
        
    except Exception as e:
        logger.error(f"Enhanced upload error: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': f'Error upload: {str(e)}'}), 500

@app.route('/api/analyze', methods=['POST'])
def analyze_document():
    """Enhanced document analysis with improved session management - FIXED VERSION"""
    try:
        data = request.json
        session_id = data.get('session_id')
        standards = data.get('standards', [])

        logger.info(f"🔍 Enhanced analysis request: session={session_id}, standards={standards}")

        if not session_id:
            logger.warning("Analysis failed: Missing session ID")
            return jsonify({'error': 'Session ID diperlukan'}), 400

        if not standards:
            logger.warning("Analysis failed: No standards selected")
            return jsonify({'error': 'Pilih minimal satu standar untuk analisis'}), 400

        # Enhanced file validation
        uploaded_files = [f for f in os.listdir(UPLOAD_FOLDER) if f.startswith(session_id)]
        if not uploaded_files:
            logger.warning(f"Analysis failed: No uploaded file found for session {session_id}")
            return jsonify({
                'error': 'File tidak ditemukan. Silakan upload ulang.',
                'session_id': session_id
            }), 404

        # FIXED: Enhanced standards validation before processing
        coordinator = get_coordinator()
        try:
            validation_result = coordinator.validate_standards_selection(standards)
            if not validation_result.get('valid'):
                logger.warning(f"Analysis failed: Invalid standards: {validation_result.get('error')}")
                return jsonify({
                    'error': validation_result.get('error'),
                    'session_id': session_id,
                    'invalid_standards': validation_result.get('invalid_standards', []),
                    'recommendations': validation_result.get('recommendations', []),
                    'action_required': 'fix_standards_selection'
                }), 400
        except Exception as validation_error:
            logger.error(f"Standards validation error: {str(validation_error)}")
            return jsonify({
                'error': f'Standards validation error: {str(validation_error)}',
                'session_id': session_id
            }), 500
        
        # FIXED: Process compliance analysis with enhanced error handling
        try:
            result = coordinator.process_compliance_analysis(session_id, standards)
            if result.get('success'):
                logger.info(f"✅ Analysis completed successfully for session {session_id}")
                logger.info(f"   📊 Compliance Score: {result.get('summary', {}).get('compliance_score', 0)}%")
                logger.info(f"   🎯 QA Ready: {result.get('qa_ready', False)}")
                logger.info(f"   📄 Report Generated: {result.get('report_generated', False)}")
                
                # Additional success metrics
                result['enhanced_metrics'] = {
                    'qa_context_stored': result.get('qa_ready', False),
                    'session_persistent': True,
                    'analysis_version': 'v2.1_fixed',
                    'timestamp': datetime.now().isoformat()
                }
                
                return jsonify(result)
            else:
                logger.error(f"❌ Analysis failed for session {session_id}: {result.get('error')}")
                return jsonify({
                    'success': False,
                    'error': result.get('error', 'Unknown analysis error'),
                    'session_id': session_id,
                    'step': result.get('step', 'unknown'),
                    'debug_info': {
                        'files_found': uploaded_files,
                        'standards_requested': standards
                    }
                }), 500
        except Exception as analysis_error:
            logger.error(f"Enhanced analysis execution error: {str(analysis_error)}")
            logger.error(traceback.format_exc())
            return jsonify({
                'success': False,
                'error': f'Error dalam enhanced analysis execution: {str(analysis_error)}',
                'session_id': session_id,
                'step': 'analysis_execution_error'
            }), 500
    except Exception as e:
        logger.error(f"Enhanced analysis request error: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': f'Error dalam request analysis: {str(e)}',
            'session_id': data.get('session_id') if 'data' in locals() else None
        }), 500

@app.route('/api/download/<session_id>/<format>')
def download_report(session_id, format):
    """Enhanced report download with better file handling"""
    try:
        logger.info(f"📥 Enhanced download request: session={session_id}, format={format}")
        
        if format not in ['pdf', 'docx']:
            logger.warning(f"Download failed: Invalid format {format}")
            return jsonify({
                'error': 'Format tidak valid. Gunakan pdf atau docx',
                'supported_formats': ['pdf', 'docx']
            }), 400
        
        import glob
        
        # Enhanced file search patterns
        if format == 'docx':
            patterns = [
                f"ReguBot_Audit_Report_{session_id}_*.docx",
                f"compliance_report_{session_id}.docx",
                f"*{session_id}*.docx"
            ]
            
            filepath = None
            for pattern in patterns:
                matches = glob.glob(os.path.join(REPORTS_FOLDER, pattern))
                if matches:
                    filepath = matches[0]
                    break
            
            if not filepath:
                logger.warning(f"DOCX report not found for session {session_id}")
        else:
            filename = f"compliance_report_{session_id}.pdf"
            filepath = os.path.join(REPORTS_FOLDER, filename)
        
        if not filepath or not os.path.exists(filepath):
            logger.warning(f"Enhanced download failed: Report not found: {filepath}")
            
            available_reports = []
            try:
                available_reports = [f for f in os.listdir(REPORTS_FOLDER) if session_id in f]
            except:
                pass
            
            return jsonify({
                'error': f'File laporan {format.upper()} tidak ditemukan',
                'session_id': session_id,
                'format': format,
                'available_files': available_reports,
                'suggestion': 'Lakukan analisis ulang untuk menghasilkan laporan baru'
            }), 404
        
        file_size = os.path.getsize(filepath)
        filename = os.path.basename(filepath)
        
        logger.info(f"✅ Enhanced download: Sending {filename} ({file_size:,} bytes)")
        
        mime_types = {
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'pdf': 'application/pdf'
        }
        
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename,
            mimetype=mime_types.get(format, 'application/octet-stream')
        )
        
    except Exception as e:
        logger.error(f"Enhanced download error: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': f'Error dalam download: {str(e)}',
            'session_id': session_id,
            'format': format
        }), 500

@app.route('/api/standards')
def get_available_standards():
    """Enhanced standards endpoint with detailed metadata"""
    try:
        logger.info("📚 Enhanced standards request received")
        
        try:
            coordinator = get_coordinator()
            standards_result = coordinator.get_available_standards()
            
            if standards_result.get('success'):
                logger.info("✅ Enhanced standards information compiled successfully")
                
                file_validation = {}
                standard_mapping = {
                    'GDPR': {'category': 'Global', 'files': ['GDPR.pdf']},
                    'NIST': {'category': 'Global', 'files': ['NIST.pdf']},
                    'UU_PDP': {'category': 'Nasional', 'files': ['UU_PDP.pdf']},
                    'POJK': {'category': 'Nasional', 'files': ['POJK.pdf']},
                    'BSSN': {'category': 'Nasional', 'files': ['BSSN_A.pdf', 'BSSN_B.pdf', 'BSSN_C.pdf']}
                }
                
                for standard_key, standard_info in standard_mapping.items():
                    category = standard_info['category']
                    files = standard_info['files']
                    
                    files_exist = []
                    for file in files:
                        file_path = os.path.join(STANDARDS_FOLDER, category, file)
                        files_exist.append(os.path.exists(file_path))
                    
                    file_validation[standard_key] = {
                        'category': category,
                        'files': files,
                        'files_exist': files_exist,
                        'available': all(files_exist),
                        'missing_files': [f for f, exists in zip(files, files_exist) if not exists]
                    }
                
                return jsonify({
                    'success': True,
                    'standards': standards_result.get('standards', {}),
                    'metadata': standards_result.get('metadata', {}),
                    'file_validation': file_validation,
                    'system_info': {
                        'standards_directory_status': standards_status,
                        'missing_files': missing_files,
                        'total_missing': len(missing_files)
                    },
                    'enhanced_features': {
                        'adaptive_selection': True,
                        'confidence_weighted_analysis': True,
                        'multi_jurisdiction_support': True,
                        'persistent_context': True,
                        'fixed_qa_integration': True
                    }
                })
            else:
                logger.error(f"Standards retrieval failed: {standards_result.get('error')}")
                return jsonify({
                    'success': False,
                    'error': standards_result.get('error', 'Unknown error'),
                    'fallback_info': {
                        'file_system_status': standards_status,
                        'available_categories': list(standards_status.keys())
                    }
                })
            
        except Exception as coordinator_error:
            logger.error(f"Enhanced coordinator standards error: {str(coordinator_error)}")
            logger.error(traceback.format_exc())
            
            return jsonify({
                'success': False,
                'error': str(coordinator_error),
                'fallback_standards': {
                    'Global': ['GDPR', 'NIST'],
                    'Nasional': ['UU_PDP', 'POJK', 'BSSN']
                },
                'file_system_status': standards_status,
                'recommendation': 'Check system logs and ensure all PDF files are present in standards directory'
            })
        
    except Exception as e:
        logger.error(f"Enhanced standards endpoint error: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': f'Error dalam mendapatkan standar: {str(e)}'
        }), 500

@app.route('/api/sessions/<session_id>/status')
def get_session_status(session_id):
    """Enhanced session status with detailed information - FIXED VERSION"""
    try:
        logger.info(f"📊 Enhanced session status request: {session_id}")
        
        uploaded_files = []
        try:
            uploaded_files = [f for f in os.listdir(UPLOAD_FOLDER) if f.startswith(session_id)]
        except Exception as e:
            logger.warning(f"Could not check upload folder: {str(e)}")
        
        reports = []
        try:
            import glob
            patterns = [
                f"*{session_id}*.pdf",
                f"*{session_id}*.docx"
            ]
            
            for pattern in patterns:
                matching_reports = glob.glob(os.path.join(REPORTS_FOLDER, pattern))
                reports.extend([os.path.basename(r) for r in matching_reports])
        except Exception as e:
            logger.warning(f"Could not check reports folder: {str(e)}")
        
        coordinator_info = {}
        try:
            coordinator = get_coordinator()
            coordinator_info = coordinator.get_session_info(session_id)
            logger.info(f"📋 Coordinator info retrieved: exists={coordinator_info.get('exists')}, qa_available={coordinator_info.get('qa_available')}")
        except Exception as e:
            logger.warning(f"Could not get coordinator info: {str(e)}")
            coordinator_info = {'error': str(e)}
        
        qa_info = {}
        try:
            coordinator = get_coordinator()
            if coordinator.qa_agent.has_session_context(session_id):
                qa_info = coordinator.qa_agent.get_session_summary(session_id)
                logger.info(f"🤖 QA info retrieved: exists={qa_info.get('exists')}")
            else:
                qa_info = {'exists': False, 'message': 'No QA context found'}
        except Exception as e:
            logger.warning(f"Could not get QA info: {str(e)}")
            qa_info = {'error': str(e)}
        
        status = {
            'session_id': session_id,
            'has_uploaded_file': len(uploaded_files) > 0,
            'uploaded_files': uploaded_files,
            'has_reports': len(reports) > 0,
            'available_reports': reports,
            'coordinator_info': coordinator_info,
            'qa_info': qa_info,
            'timestamp': datetime.now().isoformat(),
            'enhanced_status': {
                'analysis_completed': coordinator_info.get('exists', False) and bool(coordinator_info.get('analysis')),
                'qa_available': coordinator_info.get('qa_available', False),
                'qa_context_stored': qa_info.get('exists', False),
                'conversation_count': qa_info.get('conversation_count', 0),
                'compliance_score': coordinator_info.get('compliance_score', 0),
                'document_type': 'Available' if uploaded_files else 'Not found',
                'session_source': coordinator_info.get('source', 'unknown'),
                'qa_ready_for_questions': coordinator_info.get('qa_available', False) and qa_info.get('exists', False)
            }
        }
        
        logger.info(f"✅ Enhanced session status compiled: {session_id}")
        logger.info(f"   📊 Analysis: {status['enhanced_status']['analysis_completed']}")
        logger.info(f"   🤖 QA Ready: {status['enhanced_status']['qa_ready_for_questions']}")
        
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"Enhanced session status error: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'session_id': session_id,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/sessions/<session_id>/conversation')
def get_conversation_history(session_id):
    """Get conversation history for a session"""
    try:
        logger.info(f"📜 Conversation history request: {session_id}")
        
        coordinator = get_coordinator()
        conversation_history = coordinator.qa_agent.get_conversation_history(session_id)
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'conversation_history': conversation_history,
            'total_messages': len(conversation_history),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Conversation history error: {str(e)}")
        return jsonify({
            'success': False,
            'session_id': session_id,
            'error': str(e),
            'conversation_history': []
        }), 500

@app.route('/api/system/status')
def get_system_status():
    """Enhanced system status endpoint"""
    try:
        coordinator_status = {}
        try:
            coordinator = get_coordinator()
            coordinator_status = coordinator.get_agent_status()
        except Exception as e:
            coordinator_status = {'error': str(e), 'status': 'failed'}
        
        system_metrics = {
            'uptime': datetime.now().isoformat(),
            'version': 'ReguBot Enhanced v2.1 - FIXED',
            'components': {
                'groq_api': 'available' if groq_api_key else 'missing',
                'standards_files': f"{len([f for status in standards_status.values() for f in status.get('files', [])])} files",
                'missing_standards': len(missing_files),
                'upload_directory': 'ready' if os.path.exists(UPLOAD_FOLDER) else 'missing',
                'reports_directory': 'ready' if os.path.exists(REPORTS_FOLDER) else 'missing'
            },
            'coordinator_status': coordinator_status,
            'features': {
                'adaptive_analysis': True,
                'confidence_scoring': True,
                'enhanced_reporting': True,
                'multi_standard_support': True,
                'context_aware_qa': True,
                'persistent_sessions': True,
                'session_management': True,
                'fixed_qa_processing': True,
                'improved_error_handling': True
            }
        }
        
        return jsonify({
            'success': True,
            'system_status': 'healthy' if groq_api_key and len(missing_files) < 3 else 'degraded',
            'metrics': system_metrics,
            'recommendations': [
                'Ensure all standard PDF files are present' if missing_files else None,
                'Verify GROQ API key is valid' if not groq_api_key else None
            ]
        })
        
    except Exception as e:
        logger.error(f"System status error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'system_status': 'error'
        }), 500

@app.route('/api/system/cleanup', methods=['POST'])
def cleanup_system():
    """Cleanup old sessions and temporary files"""
    try:
        data = request.json or {}
        days_old = data.get('days_old', 7)
        
        logger.info(f"🧹 System cleanup request: days_old={days_old}")
        
        coordinator = get_coordinator()
        cleanup_result = coordinator.cleanup_old_sessions(days_old)
        
        return jsonify({
            'success': True,
            'cleanup_result': cleanup_result,
            'message': f'Cleanup completed. Removed {cleanup_result.get("total_cleaned", 0)} old sessions.',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Cleanup error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/chat', methods=['POST'])
def chat_with_bot():
    """Enhanced chat with improved session context handling - FIXED VERSION"""
    try:
        data = request.json
        session_id = data.get('session_id')
        question = data.get('question')
        
        logger.info(f"💬 Enhanced chat request: session={session_id}, question_length={len(question) if question else 0}")
        
        if not session_id or not question:
            logger.warning("Chat failed: Missing session ID or question")
            return jsonify({'error': 'Session ID dan pertanyaan diperlukan'}), 400
        
        if len(question.strip()) < 3:
            logger.warning("Chat failed: Question too short")
            return jsonify({'error': 'Pertanyaan terlalu pendek (minimal 3 karakter)'}), 400
        
        # FIXED: Enhanced session validation and context checking
        coordinator = get_coordinator()
        
        # Check coordinator session
        coordinator_has_session = session_id in coordinator.sessions
        coordinator_session_info = coordinator.get_session_info(session_id)
        
        # Check QA agent context
        qa_has_context = coordinator.qa_agent.has_session_context(session_id)
        
        logger.info(f"🔍 Enhanced session validation:")
        logger.info(f"   📦 Coordinator session: {coordinator_has_session}")
        logger.info(f"   📊 Session info exists: {coordinator_session_info.get('exists', False)}")
        logger.info(f"   🤖 QA context: {qa_has_context}")
        
        # FIXED: Improved context validation logic
        if not coordinator_session_info.get('exists') and not qa_has_context:
            # Try to find uploaded files
            upload_folder = 'uploads'
            uploaded_files = []
            
            if os.path.exists(upload_folder):
                try:
                    uploaded_files = [f for f in os.listdir(upload_folder) if f.startswith(session_id)]
                except Exception as e:
                    logger.error(f"Error checking uploaded files: {str(e)}")
            
            if uploaded_files:
                logger.warning(f"Files found but no analysis context for {session_id}")
                return jsonify({
                    'error': 'File dokumen ditemukan namun belum dianalisis. Silakan lakukan analisis compliance terlebih dahulu.',
                    'session_id': session_id,
                    'files_found': uploaded_files,
                    'suggestion': 'Klik tombol "Analyze" untuk menganalisis dokumen yang sudah diupload',
                    'action_required': 'analysis_needed',
                    'debug_info': {
                        'coordinator_session': coordinator_has_session,
                        'session_info_exists': coordinator_session_info.get('exists', False),
                        'qa_context': qa_has_context,
                        'files_count': len(uploaded_files)
                    }
                }), 404
            else:
                logger.error(f"No session or files found for {session_id}")
                return jsonify({
                    'error': 'Session tidak ditemukan. Silakan upload dokumen dan lakukan analisis terlebih dahulu.',
                    'session_id': session_id,
                    'suggestion': 'Upload dokumen baru untuk memulai analisis',
                    'action_required': 'upload_and_analyze',
                    'debug_info': {
                        'coordinator_session': coordinator_has_session,
                        'session_info_exists': coordinator_session_info.get('exists', False),
                        'qa_context': qa_has_context,
                        'upload_folder_exists': os.path.exists(upload_folder)
                    }
                }), 404
        
        # FIXED: If session exists but QA context is missing, try to restore
        if coordinator_session_info.get('exists') and not qa_has_context:
            logger.info(f"🔄 Restoring QA context for session {session_id}")
            try:
                # Get session data from coordinator
                session_data = coordinator.sessions.get(session_id, {})
                
                # Restore QA context
                restoration_success = coordinator.qa_agent.store_analysis_context(
                    session_id=session_id,
                    analysis_result=session_data.get('analysis', {}),
                    document_text=session_data.get('document_text', ''),
                    selected_standards=session_data.get('selected_standards', [])
                )
                
                if restoration_success:
                    logger.info(f"✅ QA context restored for session {session_id}")
                    qa_has_context = True
                else:
                    logger.error(f"❌ Failed to restore QA context for session {session_id}")
                    return jsonify({
                        'error': 'Gagal memulihkan konteks QA. Silakan lakukan analisis ulang.',
                        'session_id': session_id,
                        'suggestion': 'Lakukan analisis ulang untuk memulihkan konteks'
                    }), 500
                    
            except Exception as restore_error:
                logger.error(f"QA context restoration error: {str(restore_error)}")
                return jsonify({
                    'error': f'Error memulihkan konteks: {str(restore_error)}',
                    'session_id': session_id
                }), 500
        
        # FIXED: Process question with valid context
        try:
            logger.info(f"🤖 Processing question with QA agent for session {session_id}")
            # Process question through coordinator (which handles context properly)
            answer = coordinator.process_question(session_id, question)
            logger.info(f"✅ Chat response generated successfully for session {session_id}")
            logger.info(f"   📝 Raw answer: {repr(answer)}")
            if not answer or not isinstance(answer, str) or answer.strip() == "":
                logger.warning(f"⚠️ QA answer is empty or invalid for session {session_id}, using fallback.")
                answer = "🤖 Maaf, tidak ada jawaban yang tersedia. Silakan cek hasil analisis atau tanyakan hal lain."
            logger.info(f"   📝 Final answer length: {len(answer)} characters")
            return jsonify({
                'success': True,
                'session_id': session_id,
                'question': question,
                'response': answer,
                'timestamp': datetime.now().isoformat(),
                'debug_info': {
                    'qa_context_available': qa_has_context,
                    'coordinator_session': coordinator_has_session,
                    'processing_method': 'enhanced_fixed_version'
                }
            })
        except Exception as chat_error:
            logger.error(f"Chat processing error: {str(chat_error)}")
            logger.error(traceback.format_exc())
            return jsonify({
                'success': False,
                'session_id': session_id,
                'error': f'Error processing chat: {str(chat_error)}',
                'suggestion': 'Coba lagi atau lakukan analisis ulang jika masalah berlanjut'
            }), 500
        
    except Exception as e:
        logger.error(f"Enhanced chat error: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': f'Error dalam chat request: {str(e)}',
            'session_id': data.get('session_id') if 'data' in locals() else None
        }), 500

# Enhanced error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint tidak ditemukan',
        'available_endpoints': [
            '/api/health',
            '/api/upload',
            '/api/analyze',
            '/api/chat',
            '/api/download/<session_id>/<format>',
            '/api/standards',
            '/api/sessions/<session_id>/status',
            '/api/sessions/<session_id>/conversation',
            '/api/system/status',
            '/api/system/cleanup'
        ]
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'error': 'Method tidak diizinkan untuk endpoint ini',
        'suggestion': 'Periksa HTTP method yang digunakan'
    }), 405

@app.errorhandler(413)
def file_too_large(error):
    return jsonify({
        'error': 'File terlalu besar',
        'max_size': '15MB',
        'suggestion': 'Kompres atau gunakan file yang lebih kecil'
    }), 413

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        'error': 'Internal server error',
        'suggestion': 'Periksa log server untuk detail lengkap',
        'support': 'Hubungi administrator sistem jika masalah berlanjut'
    }), 500

if __name__ == '__main__':
    print("🤖 ReguBot Enhanced - AI Compliance Checker v2.1 - FIXED VERSION")
    print("=" * 70)
    print("📍 Server: http://localhost:5000")
    print("🔒 Processing: Fully local and offline")
    print("🚀 Features: Adaptive Analysis + Confidence Scoring + Session Management + QA FIXED")
    print("=" * 70)
    
    print("📁 Directories:")
    print(f"   📤 Upload: {UPLOAD_FOLDER}")
    print(f"   📄 Reports: {REPORTS_FOLDER}")
    print(f"   📚 Standards: {STANDARDS_FOLDER}")
    
    print("\n📊 Standards Status:")
    for category, status in standards_status.items():
        if status['exists']:
            print(f"   ✅ {category}: {status['count']} files")
            for file in status['files'][:3]:
                print(f"      - {file}")
            if status['count'] > 3:
                print(f"      - ... and {status['count'] - 3} more")
        else:
            print(f"   ❌ {category}: Directory not found")
    
    if missing_files:
        print(f"\n⚠️  Missing Files ({len(missing_files)}):")
        for file in missing_files[:5]:
            print(f"   - {file}")
        if len(missing_files) > 5:
            print(f"   - ... and {len(missing_files) - 5} more")
    
    print("\n🆕 Enhanced Features - FIXED VERSION:")
    print("   🎯 Adaptive Compliance Analysis")
    print("   📊 Confidence-Weighted Scoring")
    print("   📋 Enhanced Report Generation")
    print("   💬 Context-Aware Q&A with Persistent Memory - FIXED")
    print("   🔍 Multi-Standard Support")
    print("   ⚡ Improved Error Handling")
    print("   💾 Session Management & Persistence - FIXED")
    print("   🔄 Automatic Context Recovery - FIXED")
    print("   🚀 QA Agent Integration - COMPLETELY FIXED")
    
    print(f"\n🔑 GROQ API: {'✅ Ready' if groq_api_key else '❌ Missing'}")
    
    print("\n🔧 FIXES IMPLEMENTED:")
    print("   ✅ Added missing get_session_summary() method")
    print("   ✅ Fixed QA context storage logic")
    print("   ✅ Enhanced session validation and recovery")
    print("   ✅ Improved error handling and logging")
    print("   ✅ Fixed coordinator-QA agent communication")
    print("   ✅ Added comprehensive fallback mechanisms")
    
    print("\n🚀 Starting Enhanced Flask Application - FIXED VERSION...")
    
    try:
        app.run(host="0.0.0.0", port=5000, debug=True)
    except KeyboardInterrupt:
        print("\n👋 Enhanced server stopped by user")
        try:
            coordinator = get_coordinator()
            logger.info("Performing cleanup on exit...")
            coordinator.cleanup_old_sessions(days_old=0)  # Immediate cleanup
        except Exception as e:
            logger.error(f"Cleanup on exit failed: {str(e)}")
    except Exception as e:
        print(f"\n💥 Enhanced server error: {str(e)}")
        logger.error(f"Server startup error: {str(e)}")
        logger.error(traceback.format_exc())
    finally:
        print("\n🛑 Server shutdown complete")