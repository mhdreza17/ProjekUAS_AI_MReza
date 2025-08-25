# agent_coordinator.py - Enhanced version with comprehensive session management - FIXED

import os
import logging
from datetime import datetime
from .document_collector import DocumentCollectorAgent
from .compliance_checker import ComplianceCheckerAgent
from .standard_retriever import StandardRetrieverAgent
from .report_generator import ReportGeneratorAgent
from .qa_agent import QAAgent

class AgentCoordinator:
    """Enhanced Agent Coordinator with robust session management and QA integration - FIXED"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.sessions = {}  # Track active sessions
        self.agents = {
            'document_collector': None,
            'compliance_checker': None,
            'standard_retriever': None,
            'report_generator': None,
            'qa_agent': None
        }
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize all agents with enhanced error handling"""
        try:
            self.logger.info("Initializing Enhanced Agent System...")
            
            self.agents['document_collector'] = DocumentCollectorAgent()
            self.logger.info("✅ DocumentCollectorAgent initialized")
            
            self.agents['compliance_checker'] = ComplianceCheckerAgent()
            self.logger.info("✅ ComplianceCheckerAgent initialized")
            
            self.agents['standard_retriever'] = StandardRetrieverAgent()
            self.logger.info("✅ StandardRetrieverAgent initialized")
            
            self.agents['report_generator'] = ReportGeneratorAgent()
            self.logger.info("✅ ReportGeneratorAgent initialized")
            
            self.agents['qa_agent'] = QAAgent()
            self.logger.info("✅ QAAgent initialized")
            
            self.logger.info("🚀 All Enhanced Agents initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Agent initialization error: {str(e)}")
            raise
    
    def validate_standards_selection(self, standards):
        """Enhanced validation of selected standards"""
        valid_standards = ['GDPR', 'UU_PDP', 'POJK', 'BSSN', 'NIST']
        invalid = [s for s in standards if s not in valid_standards]
        if invalid:
            return {
                'valid': False,
                'error': f'Standar tidak valid: {", ".join(invalid)}',
                'invalid_standards': invalid,
                'valid_standards': valid_standards,
                'recommendations': [
                    'Periksa penulisan standar yang dipilih',
                    'Pastikan menggunakan nama standar yang sesuai',
                    f'Standar yang tersedia: {", ".join(valid_standards)}'
                ]
            }
        # Additional validation for standard availability
        missing_files = []
        try:
            standards_dict = self.agents['standard_retriever'].get_available_standards()
            # standards_dict is a dict of categories -> standards
            found_standards = set()
            for category, stds in standards_dict.items():
                found_standards.update(stds.keys())
            missing_files = [s for s in standards if s not in found_standards]
            if missing_files:
                return {
                    'valid': False,
                    'error': f'Tidak ditemukan file standar: {", ".join(missing_files)}',
                    'invalid_standards': missing_files,
                    'recommendations': ['Periksa ketersediaan file PDF standar di direktori standards/']
                }
        except Exception as e:
            self.logger.warning(f"Standards availability check failed: {str(e)}")
        return {
            'valid': True,
            'invalid_standards': [],
            'valid_standards': standards,
            'recommendations': []
        }
    
    def process_compliance_analysis(self, session_id: str, selected_standards: list):
        """Enhanced compliance analysis dengan QA context sync yang diperbaiki - FIXED VERSION"""
        try:
            self.logger.info(f"🔍 Starting Enhanced Compliance Analysis for session {session_id}")
            self.logger.info(f"📋 Selected Standards: {selected_standards}")

            # Step 1: Validate and find uploaded file
            upload_folder = 'uploads'
            if not os.path.exists(upload_folder):
                return {
                    'success': False,
                    'error': 'Upload directory tidak ditemukan',
                    'step': 'directory_validation'
                }
            
            uploaded_files = [f for f in os.listdir(upload_folder) if f.startswith(session_id)]
            if not uploaded_files:
                return {
                    'success': False,
                    'error': f"Tidak ada file yang diupload untuk session {session_id}",
                    'step': 'file_validation',
                    'available_files': os.listdir(upload_folder)[:5]  # Show some available files for debugging
                }
            
            filepath = os.path.join(upload_folder, uploaded_files[0])
            self.logger.info(f"📁 Processing file: {uploaded_files[0]} ({os.path.getsize(filepath)} bytes)")

            # Step 2: Enhanced standards validation
            validation_result = self.validate_standards_selection(selected_standards)
            if not validation_result.get('valid'):
                self.logger.error(f"❌ Standards validation failed: {validation_result.get('error')}")
                return {
                    'success': False,
                    'error': validation_result.get('error'),
                    'step': 'standards_validation',
                    'recommendations': validation_result.get('recommendations', [])
                }

            # Step 3: Document collection and processing
            self.logger.info("📄 Processing document...")
            document_result = self.agents['document_collector'].process(filepath)
            
            if not document_result.get('success'):
                self.logger.error(f"❌ Document processing failed: {document_result.get('error')}")
                return {
                    'success': False,
                    'error': f"Gagal memproses dokumen: {document_result.get('error', 'Unknown error')}",
                    'step': 'document_processing'
                }
            
            document_text = document_result.get('text', '')
            if not document_text or len(document_text.strip()) < 100:
                self.logger.error("❌ Document text too short or empty")
                return {
                    'success': False,
                    'error': 'Teks dokumen terlalu pendek atau kosong. Pastikan dokumen berisi konten yang cukup untuk dianalisis.',
                    'step': 'document_content_validation',
                    'document_length': len(document_text)
                }
            
            self.logger.info(f"✅ Document processed: {len(document_text):,} characters")

            # Step 4: Load and validate standards
            self.logger.info("📚 Loading selected standards...")
            try:
                standards_loaded = self.agents['standard_retriever'].load_selected_standards(selected_standards)
                self.logger.info(f"✅ Standards loaded: {standards_loaded} chunks")
                
                if standards_loaded == 0:
                    self.logger.warning("⚠️ No standards chunks loaded - proceeding with general analysis")
                
            except Exception as standards_error:
                self.logger.error(f"❌ Standards loading error: {str(standards_error)}")
                return {
                    'success': False,
                    'error': f"Gagal memuat standar: {str(standards_error)}",
                    'step': 'standards_loading'
                }

            # Step 5: Perform comprehensive compliance analysis
            self.logger.info("🔍 Performing compliance analysis...")
            compliance_result = self.agents['compliance_checker'].process(document_text, selected_standards)
            
            if not compliance_result.get('success'):
                self.logger.error(f"❌ Compliance analysis failed: {compliance_result.get('error')}")
                return {
                    'success': False,
                    'error': f"Analisis compliance gagal: {compliance_result.get('error', 'Unknown error')}",
                    'step': 'compliance_analysis'
                }
            
            analysis = compliance_result.get('analysis', {})
            compliance_score = analysis.get('compliance_score', 0)
            issues_count = len(analysis.get('issues', []))
            compliant_count = len(analysis.get('compliant_items', []))
            
            self.logger.info(f"✅ Compliance analysis completed:")
            self.logger.info(f"   📊 Score: {compliance_score}%")
            self.logger.info(f"   ⚠️ Issues: {issues_count}")
            self.logger.info(f"   ✅ Compliant: {compliant_count}")

            # Step 6: CRITICAL FIX - Store QA context immediately and properly
            self.logger.info("💾 Storing QA context - FIXED VERSION...")
            qa_store_success = False
            try:
                # FIXED: Ensure we pass all required parameters correctly
                qa_store_success = self.agents['qa_agent'].store_analysis_context(
                    session_id=session_id,
                    analysis_result=analysis,
                    document_text=document_text,
                    selected_standards=selected_standards
                )
                
                if qa_store_success:
                    self.logger.info(f"✅ QA context stored successfully for session {session_id}")
                else:
                    self.logger.error(f"❌ Failed to store QA context for session {session_id}")
                    
            except Exception as qa_error:
                self.logger.error(f"❌ QA context storage error: {str(qa_error)}")
                import traceback
                self.logger.error(traceback.format_exc())
                qa_store_success = False

            # Step 7: Generate comprehensive report
            report_result = None
            report_success = False
            try:
                self.logger.info("📄 Generating comprehensive report...")
                report_result = self.agents['report_generator'].process(analysis, session_id)
                
                if report_result and report_result.get('success'):
                    report_success = True
                    self.logger.info(f"✅ Report generated successfully:")
                    self.logger.info(f"   📑 DOCX: {os.path.basename(report_result.get('docx_path', 'Unknown'))}")
                    self.logger.info(f"   📄 PDF: {os.path.basename(report_result.get('pdf_path', 'Unknown'))}")
                else:
                    self.logger.warning(f"⚠️ Report generation failed: {report_result.get('error') if report_result else 'Unknown error'}")
                    
            except Exception as report_error:
                self.logger.error(f"❌ Report generation error: {str(report_error)}")
                import traceback
                self.logger.error(traceback.format_exc())

            # Step 8: Store comprehensive session data - FIXED VERSION
            self.sessions[session_id] = {
                'document_text': document_text,
                'document_filename': uploaded_files[0],
                'selected_standards': selected_standards,
                'analysis': analysis,
                'qa_context_stored': qa_store_success,  # FIXED: Use the actual result
                'report_generated': report_success,     # FIXED: Use the actual result
                'timestamp': datetime.now(),
                'file_info': {
                    'size': len(document_text),
                    'word_count': analysis.get('document_analysis', {}).get('word_count', 0),
                    'type': analysis.get('document_analysis', {}).get('document_type', 'Unknown')
                }
            }

            # FIXED: Log the session storage result
            self.logger.info(f"📦 Session data stored in coordinator:")
            self.logger.info(f"   QA Context: {'✅' if qa_store_success else '❌'}")
            self.logger.info(f"   Report Generated: {'✅' if report_success else '❌'}")
            self.logger.info(f"   Document Size: {len(document_text):,} chars")

            # Step 9: Prepare comprehensive response
            response = {
                'success': True,
                'analysis': analysis,
                'session_id': session_id,
                'qa_ready': qa_store_success,  # FIXED: Use actual result
                'report_generated': report_success,  # FIXED: Use actual result
                'timestamp': datetime.now().isoformat(),
                'summary': {
                    'compliance_score': compliance_score,
                    'total_issues': issues_count,
                    'compliant_items': compliant_count,
                    'high_priority_issues': len([i for i in analysis.get('issues', []) if i.get('severity') == 'HIGH']),
                    'analyzed_standards': selected_standards,
                    'document_word_count': analysis.get('document_analysis', {}).get('word_count', 0)
                }
            }
            
            # Add report paths if available
            if report_result and report_result.get('success'):
                response['docx_path'] = report_result.get('docx_path')
                response['pdf_path'] = report_result.get('pdf_path')
            
            self.logger.info(f"🎉 Enhanced compliance analysis completed successfully for session {session_id}")
            return response

        except Exception as e:
            self.logger.error(f"💥 Coordination error for session {session_id}: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            
            return {
                'success': False,
                'error': f'Error dalam koordinasi analisis: {str(e)}',
                'step': 'coordination_error',
                'session_id': session_id
            }
    
    def process_question(self, session_id: str, question: str):
        """Enhanced question processing dengan fallback dan recovery mechanisms - FIXED VERSION"""
        try:
            self.logger.info(f"💬 Processing question for session {session_id}")
            self.logger.info(f"❓ Question: {question[:100]}{'...' if len(question) > 100 else ''}")
            
            # FIXED: First check coordinator session storage
            coordinator_has_session = session_id in self.sessions
            qa_has_context = self.agents['qa_agent'].has_session_context(session_id)
            
            self.logger.info(f"🔍 Session check - Coordinator: {coordinator_has_session}, QA: {qa_has_context}")
            
            # FIXED: If coordinator has session but QA doesn't, restore QA context
            if coordinator_has_session and not qa_has_context:
                self.logger.info("🔄 Restoring QA context from coordinator session...")
                session_data = self.sessions[session_id]
                
                # Restore QA context from coordinator data
                recovery_success = self.agents['qa_agent'].store_analysis_context(
                    session_id=session_id,
                    analysis_result=session_data.get('analysis', {}),
                    document_text=session_data.get('document_text', ''),
                    selected_standards=session_data.get('selected_standards', [])
                )
                
                if recovery_success:
                    self.logger.info("✅ QA context restored successfully from coordinator")
                    qa_has_context = True
                else:
                    self.logger.error("❌ Failed to restore QA context from coordinator")
            
            # FIXED: If neither has context, try to recover from files
            if not coordinator_has_session and not qa_has_context:
                self.logger.warning(f"⚠️ No session context found for {session_id}")
                
                # Try to recover from uploaded file
                upload_folder = 'uploads'
                if os.path.exists(upload_folder):
                    uploaded_files = [f for f in os.listdir(upload_folder) if f.startswith(session_id)]
                    
                    if uploaded_files:
                        self.logger.info(f"📁 Found uploaded file: {uploaded_files[0]} - suggesting re-analysis")
                        return self._generate_reanalysis_required_response(session_id, question, uploaded_files)
                    else:
                        self.logger.error(f"❌ No uploaded files found for session {session_id}")
                        return self._generate_no_session_response(session_id, question)
                else:
                    self.logger.error("❌ Upload directory not found")
                    return self._generate_no_session_response(session_id, question)
            
            # FIXED: Now we should have valid context, process the question
            if qa_has_context:
                # Use QA Agent to process question with proper context passing
                session_data = self.sessions.get(session_id, {})
                
                answer = self.agents['qa_agent'].process_question(
                    session_id=session_id,
                    question=question,
                    document_text=session_data.get('document_text', ''),
                    analysis_context=session_data.get('analysis', {}),
                    selected_standards=session_data.get('selected_standards', [])
                )
                
                self.logger.info(f"✅ Question processed successfully for session {session_id}")
                return answer
            else:
                self.logger.error(f"❌ Unable to establish QA context for session {session_id}")
                return self._generate_context_error_response(session_id, question)
            
        except Exception as e:
            self.logger.error(f"💥 Question processing error for session {session_id}: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            
            return self._generate_error_response(session_id, question, str(e))
    
    def _generate_reanalysis_required_response(self, session_id: str, question: str, uploaded_files: list) -> str:
        """Generate response when files exist but analysis is needed"""
        return f"""
🤖 **ReguBot QA Assistant**

Saya menemukan file dokumen yang sudah diupload untuk session ini, namun **belum dilakukan analisis compliance**.

**📁 File ditemukan:** {uploaded_files[0]}
**❓ Pertanyaan Anda:** "{question[:150]}{'...' if len(question) > 150 else ''}"

🔄 **Untuk dapat menjawab pertanyaan Anda, silakan:**

1. 🔍 **Lakukan Analisis Compliance** terlebih dahulu:
   - Pilih standar compliance yang sesuai (GDPR, UU PDP, POJK, BSSN, NIST)
   - Klik tombol "Analyze" untuk menganalisis dokumen
   - Tunggu hingga analisis selesai dan laporan dihasilkan

2. 💬 **Setelah analisis selesai**, saya dapat membantu Anda dengan:
   - Penjelasan detail tentang skor compliance
   - Identifikasi area yang perlu diperbaiki  
   - Rekomendasi perbaikan dokumen yang spesifik
   - Contoh klausul yang harus ditambahkan/direvisi
   - Template implementasi compliance
   - Referensi regulasi yang relevan
   - Timeline dan prioritas perbaikan

📊 **Setelah analisis, contoh pertanyaan yang bisa dijawab:**
• "Bagaimana cara memperbaiki klausul keamanan data?"
• "Apa template yang tepat untuk consent management?"
• "Bagaimana implementasi data retention policy?"
• "Klausul apa yang harus ditambahkan untuk GDPR compliance?"

⚡ **Lakukan analisis sekarang untuk mendapatkan insight yang komprehensif!**
        """
    
    def _generate_no_session_response(self, session_id: str, question: str) -> str:
        """Generate response when no session is found"""
        return f"""
🤖 **ReguBot QA Assistant**

Maaf, saya tidak menemukan data untuk session **{session_id}**.

**❓ Pertanyaan Anda:** "{question[:150]}{'...' if len(question) > 150 else ''}"

📋 **Untuk mendapatkan jawaban yang akurat, silakan:**

1. 📤 **Upload Dokumen Baru**
   - Upload file dokumen kebijakan/prosedur (.pdf, .docx, .txt)
   - Pastikan dokumen berisi konten yang cukup untuk dianalisis

2. 🔍 **Pilih Standar Compliance**
   - GDPR (General Data Protection Regulation)
   - UU PDP (Undang-Undang Perlindungan Data Pribadi)
   - POJK (Peraturan OJK)
   - BSSN (Badan Siber dan Sandi Negara)
   - NIST (National Institute of Standards and Technology)

3. ⚡ **Lakukan Analisis Compliance**
   - Sistem akan menganalisis dokumen berdasarkan standar yang dipilih
   - Hasilnya berupa skor compliance dan rekomendasi perbaikan detail

4. 💬 **Tanyakan Pertanyaan**
   - Setelah analisis selesai, saya siap memberikan insight mendalam tentang:
   - Cara memperbaiki dokumen Anda
   - Template dan contoh klausul yang tepat
   - Implementasi compliance yang praktis
   - Prioritas perbaikan berdasarkan severity

🚀 **Mari mulai dengan upload dokumen dan analisis compliance!**
        """
    
    def _generate_context_error_response(self, session_id: str, question: str) -> str:
        """Generate response when context establishment fails"""
        return f"""
🚨 **ReguBot QA Assistant - Context Error**

Maaf, terjadi masalah dalam mengakses konteks analisis untuk session ini.

**Session:** {session_id}
**Pertanyaan:** "{question[:100]}{'...' if len(question) > 100 else ''}"

🔧 **Langkah yang dapat dicoba:**

1. **Refresh halaman** dan coba lagi
2. **Lakukan analisis ulang** jika diperlukan
3. **Upload dokumen baru** jika file hilang
4. **Hubungi administrator** jika masalah berlanjut

💡 **Atau coba pertanyaan umum seperti:**
- "Bagaimana cara meningkatkan compliance score?"
- "Apa saja standar compliance yang tersedia?"
- "Bagaimana proses analisis compliance bekerja?"
        """
    
    def _generate_error_response(self, session_id: str, question: str, error_message: str) -> str:
        """Generate response when an error occurs"""
        return f"""
🚨 **System Error**

Maaf, terjadi kesalahan dalam memproses pertanyaan Anda.

**Session:** {session_id}
**Error:** {error_message}
**Pertanyaan:** "{question[:100]}{"..." if len(question) > 100 else ""}"

💡 **Silakan coba:**
1. Pastikan dokumen sudah dianalisis
2. Coba pertanyaan yang lebih sederhana  
3. Refresh halaman dan coba lagi
4. Hubungi administrator jika masalah berlanjut

🔄 **Atau tanyakan hal umum tentang compliance.**
        """
    
    def get_available_standards(self):
        """Get available standards dengan enhanced metadata"""
        try:
            return self.agents['standard_retriever'].get_available_standards()
        except Exception as e:
            self.logger.error(f"Error getting available standards: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'fallback_standards': {
                    'Global': ['GDPR', 'NIST'],
                    'Nasional': ['UU_PDP', 'POJK', 'BSSN']
                }
            }
    
    def get_session_info(self, session_id: str):
        """Get comprehensive information about a session - FIXED VERSION"""
        try:
            # Check coordinator memory first
            session_data = self.sessions.get(session_id)
            qa_has_context = self.agents['qa_agent'].has_session_context(session_id)
            
            # FIXED: Use the corrected method call
            qa_summary = {}
            try:
                qa_summary = self.agents['qa_agent'].get_session_summary(session_id)
            except Exception as qa_error:
                self.logger.warning(f"Could not get QA summary for {session_id}: {str(qa_error)}")
                qa_summary = {'error': str(qa_error)}
            
            if session_data:
                return {
                    'exists': True,
                    'source': 'coordinator_memory',
                    'document_text': session_data.get('document_text', ''),
                    'document_filename': session_data.get('document_filename', ''),
                    'analysis': session_data.get('analysis', {}),
                    'selected_standards': session_data.get('selected_standards', []),
                    'timestamp': session_data.get('timestamp'),
                    'qa_available': qa_has_context,
                    'qa_context_stored': session_data.get('qa_context_stored', False),
                    'report_generated': session_data.get('report_generated', False),
                    'file_info': session_data.get('file_info', {}),
                    'qa_summary': qa_summary,
                    'compliance_score': session_data.get('analysis', {}).get('compliance_score', 0),
                    'recovered': session_data.get('recovered', False)
                }
            
            # Check if QA has context even if coordinator doesn't
            elif qa_has_context:
                return {
                    'exists': True,
                    'source': 'qa_memory_only',
                    'document_text': '',
                    'analysis': {},
                    'selected_standards': [],
                    'timestamp': None,
                    'qa_available': True,
                    'qa_summary': qa_summary,
                    'compliance_score': qa_summary.get('analysis_summary', {}).get('compliance_score', 0) if qa_summary and qa_summary.get('exists') else 0,
                    'note': 'Session data available in QA agent only'
                }
            
            # Try to recover from uploaded file
            else:
                upload_folder = 'uploads'
                if os.path.exists(upload_folder):
                    uploaded_files = [f for f in os.listdir(upload_folder) if f.startswith(session_id)]
                    
                    if uploaded_files:
                        filepath = os.path.join(upload_folder, uploaded_files[0])
                        try:
                            document_result = self.agents['document_collector'].process(filepath)
                            document_text = document_result.get('text', '') if document_result.get('success') else ''
                            
                            return {
                                'exists': False,
                                'source': 'uploaded_file_recovery',
                                'document_text': document_text,
                                'document_filename': uploaded_files[0],
                                'analysis': {},
                                'selected_standards': [],
                                'timestamp': None,
                                'qa_available': False,
                                'file_size': os.path.getsize(filepath),
                                'note': 'File found but not analyzed. Analysis required for QA functionality.'
                            }
                        except Exception as e:
                            self.logger.error(f"Error processing uploaded file for session {session_id}: {str(e)}")
                
                return {
                    'exists': False,
                    'source': 'not_found',
                    'qa_available': False,
                    'note': 'No session data or uploaded file found'
                }
                
        except Exception as e:
            self.logger.error(f"Error getting session info for {session_id}: {str(e)}")
            return {
                'exists': False,
                'error': str(e),
                'qa_available': False
            }
    
    def cleanup_old_sessions(self, days_old: int = 7):
        """Enhanced cleanup with comprehensive statistics"""
        try:
            cleanup_stats = {
                'coordinator_sessions_removed': 0,
                'qa_cleanup_result': {},
                'total_sessions_before': len(self.sessions),
                'errors': []
            }
            
            # Cleanup coordinator sessions
            from datetime import timedelta
            cutoff_date = datetime.now() - timedelta(days=days_old)
            
            sessions_to_remove = []
            for session_id, session_data in list(self.sessions.items()):
                try:
                    session_timestamp = session_data.get('timestamp', datetime.now())
                    if session_timestamp < cutoff_date:
                        sessions_to_remove.append(session_id)
                except Exception as e:
                    cleanup_stats['errors'].append(f"Session {session_id} timestamp check: {str(e)}")
            
            # Remove old coordinator sessions
            for session_id in sessions_to_remove:
                try:
                    del self.sessions[session_id]
                    cleanup_stats['coordinator_sessions_removed'] += 1
                except Exception as e:
                    cleanup_stats['errors'].append(f"Remove session {session_id}: {str(e)}")
            
            # Cleanup QA agent sessions
            try:
                cleanup_stats['qa_cleanup_result'] = self.agents['qa_agent'].cleanup_old_sessions(days_old)
            except Exception as e:
                cleanup_stats['errors'].append(f"QA cleanup error: {str(e)}")
            
            self.logger.info(f"✅ Session cleanup completed:")
            self.logger.info(f"   🗑️ Coordinator sessions removed: {cleanup_stats['coordinator_sessions_removed']}")
            if cleanup_stats.get('qa_cleanup_result'):
                qa_result = cleanup_stats['qa_cleanup_result']
                self.logger.info(f"   🗑️ QA sessions removed: {qa_result.get('sessions_removed', 0)}")
                self.logger.info(f"   🗑️ QA files removed: {qa_result.get('files_removed', 0)}")
            
            return cleanup_stats
            
        except Exception as e:
            self.logger.error(f"Cleanup error: {str(e)}")
            return {
                'coordinator_sessions_removed': 0,
                'qa_cleanup_result': {},
                'errors': [str(e)]
            }
    
    def get_agent_status(self):
        """Get comprehensive status of all agents"""
        try:
            status = {
                'coordinator': {
                    'active_sessions': len(self.sessions),
                    'status': 'healthy'
                }
            }
            
            for agent_name, agent in self.agents.items():
                try:
                    if hasattr(agent, 'get_status'):
                        status[agent_name] = agent.get_status()
                    else:
                        status[agent_name] = {
                            'status': 'active' if agent else 'inactive',
                            'initialized': agent is not None
                        }
                        
                    # Special handling for QA agent
                    if agent_name == 'qa_agent' and agent:
                        try:
                            qa_stats = agent.get_session_statistics()
                            status[agent_name]['statistics'] = qa_stats
                        except Exception as e:
                            status[agent_name]['statistics_error'] = str(e)
                            
                except Exception as e:
                    status[agent_name] = {
                        'status': 'error',
                        'error': str(e)
                    }
            
            return status
            
        except Exception as e:
            self.logger.error(f"Error getting agent status: {str(e)}")
            return {
                'error': str(e),
                'coordinator': {'status': 'error'}
            }
    
    def get_comprehensive_session_report(self, session_id: str):
        """Get comprehensive report about a specific session"""
        try:
            session_info = self.get_session_info(session_id)
            
            if not session_info.get('exists') and not session_info.get('qa_available'):
                return {
                    'session_id': session_id,
                    'found': False,
                    'message': 'Session not found in any system component'
                }
            
            # Gather comprehensive information
            report = {
                'session_id': session_id,
                'found': True,
                'coordinator_data': session_info,
                'qa_data': {},
                'conversation_history': [],
                'file_analysis': {},
                'recommendations': []
            }
            
            # Get QA data
            try:
                if self.agents['qa_agent'].has_session_context(session_id):
                    report['qa_data'] = self.agents['qa_agent'].get_session_summary(session_id)
                    report['conversation_history'] = self.agents['qa_agent'].get_conversation_history(session_id)
            except Exception as e:
                report['qa_data'] = {'error': str(e)}
            
            # Analyze file if available
            if session_info.get('document_filename'):
                try:
                    upload_folder = 'uploads'
                    filepath = os.path.join(upload_folder, session_info['document_filename'])
                    
                    if os.path.exists(filepath):
                        file_stats = os.stat(filepath)
                        report['file_analysis'] = {
                            'filename': session_info['document_filename'],
                            'size_bytes': file_stats.st_size,
                            'size_mb': round(file_stats.st_size / 1024 / 1024, 2),
                            'last_modified': datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
                            'exists': True
                        }
                    else:
                        report['file_analysis'] = {
                            'filename': session_info['document_filename'],
                            'exists': False,
                            'note': 'File may have been moved or deleted'
                        }
                except Exception as e:
                    report['file_analysis'] = {'error': str(e)}
            
            # Generate recommendations
            recommendations = []
            
            if not session_info.get('qa_available'):
                recommendations.append("Lakukan analisis compliance untuk mengaktifkan fitur QA")
            
            if len(report['conversation_history']) == 0:
                recommendations.append("Mulai conversation dengan QA bot untuk mendapatkan insights")
            
            compliance_score = session_info.get('compliance_score', 0)
            if compliance_score > 0:
                if compliance_score < 50:
                    recommendations.append("Skor compliance rendah - fokus pada perbaikan critical issues")
                elif compliance_score < 80:
                    recommendations.append("Skor compliance moderate - implementasikan rekomendasi perbaikan")
                else:
                    recommendations.append("Skor compliance baik - pertahankan dan lakukan monitoring")
            
            report['recommendations'] = recommendations
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating session report for {session_id}: {str(e)}")
            return {
                'session_id': session_id,
                'error': str(e),
                'found': False
            }
    
    @property
    def qa_agent(self):
        """Direct access to QA agent for external use"""
        return self.agents['qa_agent']
    
    def get_system_health(self):
        """Get overall system health status"""
        try:
            health = {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'components': {},
                'metrics': {
                    'total_sessions': len(self.sessions),
                    'qa_sessions': 0,
                    'active_conversations': 0
                },
                'issues': []
            }
            
            # Check each agent
            for agent_name, agent in self.agents.items():
                if agent is None:
                    health['components'][agent_name] = 'missing'
                    health['issues'].append(f"{agent_name} not initialized")
                    health['status'] = 'degraded'
                else:
                    health['components'][agent_name] = 'active'
            
            # Get QA metrics
            try:
                if self.agents['qa_agent']:
                    qa_stats = self.agents['qa_agent'].get_session_statistics()
                    health['metrics']['qa_sessions'] = qa_stats.get('total_sessions', 0)
                    health['metrics']['active_conversations'] = qa_stats.get('total_conversations', 0)
            except Exception as e:
                health['issues'].append(f"QA metrics unavailable: {str(e)}")
            
            # Check critical directories
            critical_dirs = ['uploads', 'reports', 'standards', 'session_storage']
            for dir_name in critical_dirs:
                if not os.path.exists(dir_name):
                    health['issues'].append(f"Directory missing: {dir_name}")
                    health['status'] = 'degraded'
            
            # Overall status determination
            if len(health['issues']) == 0:
                health['status'] = 'healthy'
            elif len(health['issues']) < 3:
                health['status'] = 'degraded'
            else:
                health['status'] = 'critical'
            
            return health
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }