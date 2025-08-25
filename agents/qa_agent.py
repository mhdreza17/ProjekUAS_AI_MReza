import os
import json
from groq import Groq
from .base_agent import BaseAgent
from .standard_retriever import StandardRetrieverAgent
from datetime import datetime
import pickle
import logging

class QAAgent(BaseAgent):
    """Enhanced QA Agent dengan session management yang diperbaiki dan kemampuan analisis mendalam"""
    
    def __init__(self):
        super().__init__("QAAgent")
        self.groq_client = Groq(api_key=os.getenv('GROQ_API_KEY'))
        self.standard_retriever = StandardRetrieverAgent()
        self.conversation_history = {}
        self.analysis_contexts = {}  # Store analysis results by session
        self.document_contexts = {}  # Store original documents by session
        self.logger = logging.getLogger(__name__)
        
        # Create session storage directory
        self.session_storage_dir = "session_storage"
        os.makedirs(self.session_storage_dir, exist_ok=True)
        
        # Load existing sessions from storage
        self._load_existing_sessions()
        
    def _load_existing_sessions(self):
        """Load existing session data from storage"""
        try:
            if not os.path.exists(self.session_storage_dir):
                return
                
            for filename in os.listdir(self.session_storage_dir):
                if filename.endswith('.pkl'):
                    session_id = filename.replace('.pkl', '')
                    filepath = os.path.join(self.session_storage_dir, filename)
                    
                    try:
                        with open(filepath, 'rb') as f:
                            session_data = pickle.load(f)
                            
                        self.analysis_contexts[session_id] = session_data.get('analysis_context', {})
                        self.document_contexts[session_id] = session_data.get('document_context', {})
                        self.conversation_history[session_id] = session_data.get('conversation_history', [])
                        
                        self.log_action("Session loaded", f"Session: {session_id}")
                    except Exception as e:
                        self.logger.error(f"Failed to load session {session_id}: {str(e)}")
                        
        except Exception as e:
            self.log_action("Session loading error", str(e))
    
    def _save_session_data(self, session_id: str):
        """Save session data to persistent storage"""
        try:
            session_data = {
                'analysis_context': self.analysis_contexts.get(session_id, {}),
                'document_context': self.document_contexts.get(session_id, {}),
                'conversation_history': self.conversation_history.get(session_id, []),
                'last_updated': datetime.now().isoformat()
            }
            
            filepath = os.path.join(self.session_storage_dir, f"{session_id}.pkl")
            with open(filepath, 'wb') as f:
                pickle.dump(session_data, f)
                
            self.log_action("Session saved", f"Session: {session_id}")
            
        except Exception as e:
            self.log_action("Session saving error", f"{session_id}: {str(e)}")
    
    def store_analysis_context(self, session_id: str, analysis_result: dict, document_text: str = None, selected_standards: list = None):
        """Store comprehensive analysis context for future QA sessions"""
        try:
            # Store analysis context
            self.analysis_contexts[session_id] = {
                'compliance_score': analysis_result.get('compliance_score', 0),
                'issues': analysis_result.get('issues', []),
                'compliant_items': analysis_result.get('compliant_items', []),
                'recommendations': analysis_result.get('recommendations', []),
                'document_analysis': analysis_result.get('document_analysis', {}),
                'detailed_findings': analysis_result.get('detailed_findings', []),
                'analyzed_standards': selected_standards or analysis_result.get('analyzed_standards', []),
                'aspect_scores': analysis_result.get('aspect_scores', {}),
                'summary': analysis_result.get('summary', {}),
                'timestamp': datetime.now().isoformat()
            }
            
            # Store document context if provided
            if document_text:
                self.document_contexts[session_id] = {
                    'document_text': document_text[:5000],  # Store first 5000 chars for context
                    'full_text_length': len(document_text),
                    'document_type': analysis_result.get('document_analysis', {}).get('document_type', 'Unknown'),
                    'word_count': analysis_result.get('document_analysis', {}).get('word_count', 0),
                    'themes': analysis_result.get('document_analysis', {}).get('themes', []),
                    'selected_standards': selected_standards or []
                }
            
            # Initialize conversation history if not exists
            if session_id not in self.conversation_history:
                self.conversation_history[session_id] = []
            
            # Save to persistent storage
            self._save_session_data(session_id)
            
            self.log_action("Analysis context stored", f"Session: {session_id}, Score: {analysis_result.get('compliance_score', 0)}%")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to store analysis context for {session_id}: {str(e)}")
            return False
    
    def has_session_context(self, session_id: str) -> bool:
        """Check if session has stored context"""
        return session_id in self.analysis_contexts and session_id in self.document_contexts
    
    def get_session_summary(self, session_id: str) -> dict:
        """Get comprehensive session summary - MISSING METHOD FIXED"""
        try:
            if not self.has_session_context(session_id):
                return {
                    'exists': False,
                    'session_id': session_id,
                    'error': 'No context found for this session'
                }
            
            analysis_context = self.analysis_contexts.get(session_id, {})
            document_context = self.document_contexts.get(session_id, {})
            conversation_history = self.conversation_history.get(session_id, [])
            
            return {
                'exists': True,
                'session_id': session_id,
                'has_analysis': bool(analysis_context),
                'has_document': bool(document_context),
                'conversation_count': len(conversation_history),
                'analysis_summary': {
                    'compliance_score': analysis_context.get('compliance_score', 0),
                    'total_issues': len(analysis_context.get('issues', [])),
                    'high_priority_issues': len([i for i in analysis_context.get('issues', []) if i.get('severity') == 'HIGH']),
                    'compliant_items': len(analysis_context.get('compliant_items', [])),
                    'recommendations_count': len(analysis_context.get('recommendations', [])),
                    'analyzed_standards': analysis_context.get('analyzed_standards', []),
                    'timestamp': analysis_context.get('timestamp', 'Unknown')
                },
                'document_summary': {
                    'word_count': document_context.get('word_count', 0),
                    'document_type': document_context.get('document_type', 'Unknown'),
                    'themes': document_context.get('themes', []),
                    'text_preview': document_context.get('document_text', '')[:200] + '...' if document_context.get('document_text') else ''
                },
                'conversation_summary': {
                    'total_questions': len(conversation_history),
                    'last_question_time': conversation_history[-1].get('timestamp') if conversation_history else None,
                    'recent_topics': [q.get('question', '')[:50] + '...' for q in conversation_history[-3:]] if conversation_history else []
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting session summary for {session_id}: {str(e)}")
            return {
                'exists': False,
                'session_id': session_id,
                'error': str(e)
            }
    
    def get_conversation_history(self, session_id: str) -> list:
        """Get conversation history for a session"""
        return self.conversation_history.get(session_id, [])
    
    def get_session_statistics(self) -> dict:
        """Get comprehensive statistics across all sessions"""
        try:
            total_sessions = len(self.analysis_contexts)
            total_conversations = sum(len(conv) for conv in self.conversation_history.values())
            
            active_sessions = [sid for sid, ctx in self.analysis_contexts.items() 
                             if ctx.get('timestamp') and 
                             (datetime.now() - datetime.fromisoformat(ctx['timestamp'])).days < 7]
            
            return {
                'total_sessions': total_sessions,
                'total_conversations': total_conversations,
                'active_sessions': len(active_sessions),
                'sessions_with_conversations': len([s for s in self.conversation_history.values() if s]),
                'average_questions_per_session': total_conversations / max(total_sessions, 1),
                'storage_directory': self.session_storage_dir,
                'storage_files_count': len([f for f in os.listdir(self.session_storage_dir) if f.endswith('.pkl')]) if os.path.exists(self.session_storage_dir) else 0
            }
        except Exception as e:
            self.logger.error(f"Error getting session statistics: {str(e)}")
            return {'error': str(e)}
    
    def process_question(self, session_id: str, question: str, document_text: str = None, analysis_context: dict = None, selected_standards: list = None):
        """
        Process question with comprehensive context handling and fallback mechanisms - ENHANCED
        """
        self.set_status("processing")
        self.log_action("Processing enhanced question", f"Session: {session_id}")
        try:
            # Check if we have stored context
            if not self.has_session_context(session_id):
                # Try to store context if provided
                if analysis_context and document_text:
                    self.logger.info(f"Storing context on demand for session {session_id}")
                    success = self.store_analysis_context(session_id, analysis_context, document_text, selected_standards)
                    if success:
                        self.logger.info(f"✅ Context stored successfully for session {session_id}")
                    else:
                        self.logger.error(f"❌ Failed to store context for session {session_id}")
                        return self._generate_error_response(question, "Failed to store analysis context")
                else:
                    self.logger.error(f"❌ No context available for session {session_id}")
                    return self._generate_no_context_response(session_id, question)

            # Get stored context
            stored_analysis = self.analysis_contexts.get(session_id, {})
            stored_document = self.document_contexts.get(session_id, {})

            # Get relevant standards based on question and analyzed standards
            analyzed_standards = stored_analysis.get('analyzed_standards', [])
            if analyzed_standards:
                relevant_standards = self.standard_retriever.process(
                    question,
                    top_k=3,
                    selected_standards=analyzed_standards
                )
            else:
                relevant_standards = self.standard_retriever.process(question, top_k=3)

            # Detect greetings or simple questions
            greetings = ["halo", "hai", "hello", "hi", "apa kabar", "selamat pagi", "selamat siang", "selamat sore", "selamat malam"]
            q_lower = question.strip().lower()
            if any(greet in q_lower for greet in greetings) or len(q_lower) <= 8:
                answer = "🤖 Halo! Saya ReguBot QA Assistant. Silakan ajukan pertanyaan tentang compliance dokumen Anda, analisis, atau perbaikan."
            else:
                # Generate comprehensive answer only for real compliance/document questions
                answer = self._generate_comprehensive_answer_with_groq(
                    question, relevant_standards, stored_analysis, stored_document, session_id
                )
                # Strict fallback if answer is falsy or not a string
                if not answer or not isinstance(answer, str) or answer.strip() == "":
                    answer = "🤖 Maaf, tidak ada jawaban yang tersedia. Silakan cek hasil analisis atau tanyakan hal lain."

            # Store conversation history
            self.conversation_history[session_id].append({
                'question': question,
                'answer': answer,
                'timestamp': datetime.now().isoformat(),
                'context_used': {
                    'has_analysis': bool(stored_analysis),
                    'has_document': bool(stored_document),
                    'standards_retrieved': len(relevant_standards.get('standards', [])),
                    'compliance_score': stored_analysis.get('compliance_score', 0),
                    'total_issues': len(stored_analysis.get('issues', []))
                }
            })

            # Save updated session
            self._save_session_data(session_id)

            self.set_status("completed")
            self.log_action("Enhanced question answered", f"Length: {len(answer)} chars")

            return answer

        except Exception as e:
            self.set_status("error")
            self.log_action("Enhanced QA error", str(e))
            self.logger.error(f"QA processing error for session {session_id}: {str(e)}")
            return self._generate_error_response(question, str(e))
    
    def _generate_no_context_response(self, session_id: str, question: str) -> str:
        """Generate response when no analysis context is available"""
        return f"""
🤖 **ReguBot QA Assistant**

Maaf, saya tidak menemukan hasil analisis compliance untuk session ini ({session_id}).

📋 **Untuk mendapatkan jawaban yang akurat, silakan:**
1. 📤 Upload dokumen kebijakan/prosedur Anda
2. 🔍 Pilih standar compliance yang sesuai (GDPR, UU PDP, POJK, dll)
3. ⚡ Lakukan analisis compliance terlebih dahulu
4. 💬 Kemudian tanyakan pertanyaan tentang hasil analisis

**Pertanyaan Anda:** "{question[:100]}{"..." if len(question) > 100 else ""}"

💡 **Tip:** Setelah analisis selesai, saya dapat membantu Anda dengan:
- Penjelasan detail tentang skor compliance
- Identifikasi area yang perlu diperbaiki
- Rekomendasi perbaikan dokumen
- Referensi regulasi yang relevan
- Langkah implementasi yang praktis

🔄 **Silakan lakukan analisis dokumen terlebih dahulu untuk mendapatkan bantuan yang maksimal!**
        """
    
    def _generate_error_response(self, question: str, error_message: str) -> str:
        """Generate response when an error occurs"""
        return f"""
🚨 **System Error**

Maaf, terjadi kesalahan dalam memproses pertanyaan Anda.

**Error:** {error_message}

**Pertanyaan:** "{question[:100]}{"..." if len(question) > 100 else ""}"

💡 **Silakan coba:**
1. Pastikan dokumen sudah dianalisis
2. Coba pertanyaan yang lebih sederhana
3. Hubungi administrator jika masalah berlanjut

🔄 **Atau tanyakan hal umum seperti:**
- "Bagaimana cara meningkatkan skor compliance?"
- "Apa saja aspek utama yang dinilai?"
- "Rekomendasi perbaikan apa yang tersedia?"
        """
    
    def _generate_comprehensive_answer_with_groq(self, question: str, relevant_standards: dict, 
                                          analysis_context: dict, document_context: dict, 
                                          session_id: str) -> str:
        """Generate comprehensive answer dengan konteks yang mendalam - ENHANCED"""
        try:
            # Build comprehensive context
            analysis_summary = self._build_detailed_analysis_summary(analysis_context)
            document_summary = self._build_document_summary(document_context)
            standards_context = self._build_standards_context(relevant_standards)
            improvement_roadmap = self._generate_comprehensive_improvement_roadmap(analysis_context)
            
            # Create enhanced prompt for document improvement recommendations
            prompt = f"""
Anda adalah AI Expert Compliance Consultant yang memberikan jawaban mendalam dan actionable berdasarkan hasil analisis dokumen compliance.

PERTANYAAN PENGGUNA: {question}

=== HASIL ANALISIS COMPLIANCE ===
{analysis_summary}

=== KONTEKS DOKUMEN YANG DIANALISIS ===
{document_summary}

=== REFERENSI REGULASI YANG RELEVAN ===
{standards_context}

=== ROADMAP PERBAIKAN YANG DIREKOMENDASIKAN ===
{improvement_roadmap}

=== INSTRUKSI MENJAWAB ===
1. BERIKAN JAWABAN YANG SPESIFIK berdasarkan hasil analisis yang sudah dilakukan
2. ACTIONABLE: Berikan langkah-langkah konkret yang bisa diterapkan
3. PRIORITAS: Urutkan rekomendasi berdasarkan dampak dan urgensi
4. REFERENSI: Sertakan pasal/regulasi yang relevan jika tersedia
5. CONTOH: Berikan contoh praktis implementasi jika memungkinkan
6. BAHASA: Gunakan bahasa Indonesia profesional namun mudah dipahami

=== JENIS RESPONS BERDASARKAN PERTANYAAN ===
- SKOR/RATING: Jelaskan komponen penilaian, faktor yang mempengaruhi, dan cara meningkatkan
- ISSUES/MASALAH: Berikan solusi prioritas, langkah perbaikan, dan timeline implementasi  
- REKOMENDASI: Detail langkah implementasi, resources needed, expected outcomes
- REGULASI: Rujuk pasal spesifik, interpretasi praktis, dan cara compliance
- PERBAIKAN DOKUMEN: Template perbaikan, contoh klausul, dan best practices
- IMPLEMENTASI: Step-by-step guide, checklist, dan monitoring framework

=== FOKUS KHUSUS UNTUK PERBAIKAN DOKUMEN ===
Jika pertanyaan tentang perbaikan dokumen, berikan:
1. Identifikasi spesifik bagian dokumen yang perlu diperbaiki
2. Contoh klausul/paragraf yang harus ditambahkan atau direvisi
3. Template atau format yang sesuai standar compliance
4. Checklist validasi setelah perbaikan
5. Strategi implementasi perubahan dalam organisasi

=== FORMAT JAWABAN ===
- Gunakan struktur yang jelas dengan headers
- Sertakan emoji untuk readability
- Berikan summary dan action items di akhir
- Tambahkan disclaimer professional

Jawab dengan komprehensif dan praktis:
"""

            # Call Groq API
            response = self.groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system", 
                        "content": "Anda adalah Expert Compliance Consultant AI dengan spesialisasi dalam analisis mendalam dokumen compliance dan rekomendasi perbaikan praktis. Berikan jawaban yang actionable, praktis, dan berdasarkan evidence dari hasil analisis."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=1500,
                top_p=0.9
            )
            
            answer = response.choices[0].message.content if response and response.choices and response.choices[0].message.content else ""
            # Strict fallback if answer is falsy or not a string
            if not answer or not isinstance(answer, str) or answer.strip() == "":
                answer = "🤖 Maaf, tidak ada jawaban yang tersedia. Silakan cek hasil analisis atau tanyakan hal lain."
            # Enhance answer with session-specific insights
            answer = self._add_comprehensive_insights(answer, analysis_context, session_id)
            # Add professional disclaimer and next steps
            answer += self._add_professional_disclaimer_and_next_steps(analysis_context)
            return answer
            
        except Exception as e:
            self.log_action("Groq API error", str(e))
            self.logger.error(f"Groq API error: {str(e)}")
            return self._generate_fallback_comprehensive_answer(question, analysis_context, document_context)
    
    def _build_detailed_analysis_summary(self, analysis_context: dict) -> str:
        """Build detailed analysis summary dengan insights mendalam"""
        if not analysis_context:
            return "Tidak ada hasil analisis yang tersedia untuk sesi ini."
        
        compliance_score = analysis_context.get('compliance_score', 0)
        issues = analysis_context.get('issues', [])
        compliant_items = analysis_context.get('compliant_items', [])
        aspect_scores = analysis_context.get('aspect_scores', {})
        recommendations = analysis_context.get('recommendations', [])
        
        # Build compliance status
        if compliance_score >= 80:
            status = "🌟 EXCELLENT - Compliance Tinggi"
            priority = "MAINTENANCE & MONITORING"
        elif compliance_score >= 60:
            status = "✅ GOOD - Perlu Minor Improvements"
            priority = "OPTIMIZATION & ENHANCEMENT"
        elif compliance_score >= 40:
            status = "⚠️ MODERATE - Perlu Perbaikan Substansial"
            priority = "REMEDIATION REQUIRED"
        else:
            status = "🚨 CRITICAL - Perlu Revisi Menyeluruh"
            priority = "URGENT OVERHAUL NEEDED"
        
        summary = f"""
📊 COMPLIANCE SCORE: {compliance_score}% - {status}
🎯 PRIORITAS TINDAKAN: {priority}
🔴 TOTAL ISSUES DITEMUKAN: {len(issues)}
✅ REQUIREMENTS TERPENUHI: {len(compliant_items)}
📋 TOTAL REKOMENDASI: {len(recommendations)}

📈 BREAKDOWN ASPEK COMPLIANCE:"""
        
        for aspect_key, score_data in aspect_scores.items():
            aspect_name = score_data.get('result', {}).get('aspect', aspect_key)
            score = score_data.get('score', 0) * 100
            weight = score_data.get('weight', 0) * 100
            
            if score >= 80:
                status_emoji = "🟢"
            elif score >= 60:
                status_emoji = "🟡"
            elif score >= 40:
                status_emoji = "🟠"
            else:
                status_emoji = "🔴"
            
            summary += f"\n   {status_emoji} {aspect_name}: {score:.1f}% (Bobot: {weight:.1f}%)"
        
        # Add critical issues analysis
        high_priority_issues = [issue for issue in issues if issue.get('severity') == 'HIGH']
        medium_priority_issues = [issue for issue in issues if issue.get('severity') == 'MEDIUM']
        
        if high_priority_issues:
            summary += f"\n\n🚨 CRITICAL ISSUES ({len(high_priority_issues)}):"
            for i, issue in enumerate(high_priority_issues[:3], 1):
                aspect = issue.get('aspect', 'Unknown')
                explanation = issue.get('explanation', 'No explanation')[:150]
                summary += f"\n   {i}. {aspect}: {explanation}..."
        
        if medium_priority_issues:
            summary += f"\n\n⚠️ MEDIUM PRIORITY ISSUES ({len(medium_priority_issues)}):"
            for i, issue in enumerate(medium_priority_issues[:2], 1):
                aspect = issue.get('aspect', 'Unknown')
                explanation = issue.get('explanation', 'No explanation')[:100]
                summary += f"\n   {i}. {aspect}: {explanation}..."
        
        # Add top compliant items
        if compliant_items:
            summary += f"\n\n✅ TOP STRENGTHS ({len(compliant_items)}):"
            for i, item in enumerate(compliant_items[:3], 1):
                aspect = item.get('aspect', 'Unknown')
                explanation = item.get('explanation', 'No explanation')[:100]
                summary += f"\n   {i}. {aspect}: {explanation}..."
        
        return summary
    
    def _build_document_summary(self, document_context: dict) -> str:
        """Build comprehensive document context summary"""
        if not document_context:
            return "Tidak ada konteks dokumen yang tersedia."
        
        analyzed_standards = document_context.get('selected_standards', [])
        standards_text = ", ".join(analyzed_standards) if analyzed_standards else "Tidak ada standar yang dipilih"
        
        return f"""
📄 INFORMASI DOKUMEN YANG DIANALISIS:
   • Jenis: {document_context.get('document_type', 'Unknown')}
   • Jumlah kata: {document_context.get('word_count', 0):,}
   • Panjang teks: {document_context.get('full_text_length', 0):,} karakter
   • Standar yang digunakan: {standards_text}

🏷️ TEMA UTAMA DOKUMEN:
   {', '.join(document_context.get('themes', ['Tidak teridentifikasi'])[:5])}

📋 CUPLIKAN DOKUMEN (Awal):
{document_context.get('document_text', 'Tidak tersedia')[:400]}...
"""
    
    def _build_standards_context(self, relevant_standards: dict) -> str:
        """Build comprehensive standards context"""
        if not relevant_standards.get('success') or not relevant_standards.get('standards'):
            return "Tidak ada referensi regulasi yang ditemukan untuk pertanyaan ini."
        
        context = "REGULASI DAN STANDAR YANG RELEVAN:\n\n"
        
        for i, standard in enumerate(relevant_standards['standards'][:3], 1):
            source = standard.get('source', 'Unknown')
            content = standard.get('content', '')
            ui_standard = standard.get('ui_standard', 'Unknown')
            
            context += f"""
📖 REFERENSI {i} - {ui_standard} ({source}):
{content[:400]}...

🔍 RELEVANSI: Standar ini memberikan panduan untuk compliance dalam aspek yang Anda tanyakan.
{'='*50}"""
        
        return context
    
    def _generate_comprehensive_improvement_roadmap(self, analysis_context: dict) -> str:
        """Generate comprehensive improvement roadmap"""
        if not analysis_context:
            return "Tidak dapat membuat roadmap tanpa hasil analisis."
        
        compliance_score = analysis_context.get('compliance_score', 0)
        issues = analysis_context.get('issues', [])
        recommendations = analysis_context.get('recommendations', [])
        aspect_scores = analysis_context.get('aspect_scores', {})
        
        roadmap = "🗺️ ROADMAP PERBAIKAN COMPLIANCE:\n\n"
        
        # Phase 1: Immediate Actions
        roadmap += "📍 FASE 1 - TINDAKAN SEGERA (0-30 hari):\n"
        high_priority_issues = [issue for issue in issues if issue.get('severity') == 'HIGH']
        if high_priority_issues:
            for i, issue in enumerate(high_priority_issues[:3], 1):
                aspect = issue.get('aspect', 'Unknown')
                recommendations_list = issue.get('recommendations', [])
                roadmap += f"   {i}. {aspect}:\n"
                for rec in recommendations_list[:2]:
                    roadmap += f"      • {rec}\n"
        else:
            roadmap += "   ✅ Tidak ada isu kritis yang memerlukan tindakan segera\n"
        
        # Phase 2: Short-term improvements
        roadmap += "\n📍 FASE 2 - PERBAIKAN JANGKA PENDEK (1-3 bulan):\n"
        medium_priority_issues = [issue for issue in issues if issue.get('severity') == 'MEDIUM']
        if medium_priority_issues:
            for i, issue in enumerate(medium_priority_issues[:3], 1):
                aspect = issue.get('aspect', 'Unknown')
                roadmap += f"   {i}. Perbaiki aspek {aspect}\n"
        
        # Phase 3: Long-term optimization
        roadmap += "\n📍 FASE 3 - OPTIMISASI JANGKA PANJANG (3-6 bulan):\n"
        if compliance_score < 80:
            roadmap += "   • Implementasi sistem monitoring berkelanjutan\n"
            roadmap += "   • Pelatihan tim tentang compliance requirements\n"
            roadmap += "   • Audit internal berkala\n"
        else:
            roadmap += "   • Maintenance dan monitoring tingkat compliance\n"
            roadmap += "   • Continuous improvement process\n"
        
        # Add specific recommendations
        if recommendations:
            roadmap += "\n💡 REKOMENDASI SPESIFIK DARI SISTEM:\n"
            for i, rec in enumerate(recommendations[:5], 1):
                roadmap += f"   {i}. {rec}\n"
        
        # Add success metrics
        roadmap += "\n📊 TARGET KEBERHASILAN:\n"
        target_score = min(compliance_score + 20, 95)
        roadmap += f"   • Target Compliance Score: {target_score}%\n"
        roadmap += f"   • Reduksi Critical Issues: 80-100%\n"
        roadmap += f"   • Implementasi Best Practices: 90%+\n"
        
        return roadmap
    
    def _add_comprehensive_insights(self, answer: str, analysis_context: dict, session_id: str) -> str:
        """Add comprehensive session-specific insights"""
        if not analysis_context:
            return answer
        
        insights = []
        
        # Add conversation context
        conversation_count = len(self.conversation_history.get(session_id, []))
        if conversation_count > 0:
            insights.append(f"\n📊 **Session Context**: Ini adalah pertanyaan ke-{conversation_count + 1} untuk analisis dokumen Anda.")
        
        # Add compliance status insights
        compliance_score = analysis_context.get('compliance_score', 0)
        issues_count = len(analysis_context.get('issues', []))
        
        if compliance_score > 0:
            if compliance_score >= 80:
                insights.append(f"\n🌟 **Status Compliance**: Excellent! Score {compliance_score}% menunjukkan dokumen Anda sudah sangat baik. Focus pada maintenance dan continuous improvement.")
            elif compliance_score >= 60:
                insights.append(f"\n🎯 **Status Compliance**: Good! Score {compliance_score}% menunjukkan dokumen dalam kondisi baik dengan {issues_count} area yang perlu perbaikan.")
            elif compliance_score >= 40:
                insights.append(f"\n⚠️ **Status Compliance**: Moderate. Score {compliance_score}% menunjukkan perlunya perbaikan substansial pada {issues_count} aspek kunci.")
            else:
                insights.append(f"\n🚨 **Status Compliance**: Critical! Score {compliance_score}% menunjukkan dokumen perlu revisi menyeluruh untuk {issues_count} isu yang teridentifikasi.")
        
        # Add specific improvement focus
        high_priority_issues = [issue for issue in analysis_context.get('issues', []) if issue.get('severity') == 'HIGH']
        if high_priority_issues:
            insights.append(f"\n🔥 **Focus Prioritas**: {len(high_priority_issues)} isu kritis memerlukan perhatian segera untuk meningkatkan compliance score secara signifikan.")
        
        return answer + '\n'.join(insights)
    
    def _add_professional_disclaimer_and_next_steps(self, analysis_context: dict) -> str:
        """Add comprehensive disclaimer and actionable next steps"""
        disclaimer = "\n\n" + "="*70 + "\n"
        disclaimer += "💼 **DISCLAIMER PROFESIONAL & LANGKAH SELANJUTNYA**\n\n"
        
        disclaimer += "📋 **Disclaimer:**\n"
        disclaimer += "• Analisis berdasarkan AI dan referensi regulasi resmi\n"
        disclaimer += "• Untuk kepastian hukum, konsultasikan dengan ahli hukum/compliance officer\n"
        disclaimer += "• Implementasi harus disesuaikan dengan konteks organisasi\n"
        disclaimer += "• Review berkala diperlukan mengikuti perubahan regulasi\n\n"
        
        if analysis_context.get('compliance_score', 0) > 0:
            disclaimer += "🎯 **Action Plan:**\n"
            disclaimer += "• Prioritaskan perbaikan berdasarkan severity dan impact\n"
            disclaimer += "• Dokumentasikan semua perubahan yang dilakukan\n"
            disclaimer += "• Lakukan re-analysis setelah implementasi perbaikan\n"
            disclaimer += "• Establish monitoring mechanism untuk sustainability\n\n"
        
        disclaimer += "💡 **Tips Lanjutan:**\n"
        disclaimer += "• Tanyakan aspek spesifik untuk panduan yang lebih detail\n"
        disclaimer += "• Request contoh implementasi untuk area tertentu\n"
        disclaimer += "• Minta prioritization matrix untuk multiple issues\n"
        disclaimer += "• Diskusikan timeline implementasi yang realistis\n\n"
        
        disclaimer += "🔄 **Pertanyaan Lanjutan yang Disarankan:**\n"
        disclaimer += "• \"Bagaimana cara implementasi rekomendasi X?\"\n"
        disclaimer += "• \"Apa template dokumen untuk aspek Y?\"\n"
        disclaimer += "• \"Bagaimana monitoring compliance untuk area Z?\"\n"
        disclaimer += "• \"Apa best practices untuk meningkatkan score?\""
        
        return disclaimer
    
    def _generate_fallback_comprehensive_answer(self, question: str, analysis_context: dict, document_context: dict) -> str:
        """Generate comprehensive fallback answer when Groq API fails"""
        answer = "🤖 **ReguBot QA Assistant - Fallback Mode**\n\n"
        answer += "Maaf, terjadi kendala teknis dengan AI engine, namun saya dapat memberikan informasi berdasarkan data analisis:\n\n"
        
        if analysis_context:
            score = analysis_context.get('compliance_score', 0)
            issues = analysis_context.get('issues', [])
            compliant_items = analysis_context.get('compliant_items', [])
            recommendations = analysis_context.get('recommendations', [])
            
            answer += f"📊 **Hasil Analisis Dokumen Anda:**\n"
            answer += f"• Skor Compliance: {score}%\n"
            answer += f"• Total Issues: {len(issues)}\n"
            answer += f"• Items Compliant: {len(compliant_items)}\n"
            answer += f"• Rekomendasi Tersedia: {len(recommendations)}\n\n"
            
            if issues:
                answer += "🔍 **Top Issues Ditemukan:**\n"
                for i, issue in enumerate(issues[:3], 1):
                    severity = issue.get('severity', 'MEDIUM')
                    aspect = issue.get('aspect', 'Unknown')
                    answer += f"{i}. [{severity}] {aspect}\n"
                answer += "\n"
            
            if recommendations:
                answer += "💡 **Rekomendasi Sistem:**\n"
                for i, rec in enumerate(recommendations[:5], 1):
                    answer += f"{i}. {rec}\n"
                answer += "\n"
            
            # Provide general guidance based on score
            if score < 30:
                answer += "🚨 **Panduan Umum:** Dokumen memerlukan revisi menyeluruh. Fokus pada requirement dasar compliance terlebih dahulu.\n"
            elif score < 60:
                answer += "⚠️ **Panduan Umum:** Perbaiki isu-isu kritis dan medium priority secara bertahap.\n"
            elif score < 80:
                answer += "🎯 **Panduan Umum:** Lakukan fine-tuning dan optimisasi aspek yang masih kurang.\n"
            else:
                answer += "🌟 **Panduan Umum:** Pertahankan kualitas tinggi dan implementasikan monitoring berkelanjutan.\n"
        
        # Add fallback next steps
        answer += "\n🔄 **Langkah Selanjutnya:**\n"
        answer += "1. Periksa kembali dokumen yang diunggah\n"
        answer += "2. Pastikan semua standar yang relevan telah dipilih\n"
        answer += "3. Lakukan analisis ulang jika perlu\n"
        answer += "4. Hubungi tim support jika masalah berlanjut\n"
        
        return answer.strip()
    
    def cleanup_old_sessions(self, days_old: int = 7) -> dict:
        """Cleanup old sessions with comprehensive statistics"""
        try:
            from datetime import timedelta
            cutoff_date = datetime.now() - timedelta(days=days_old)
            
            cleanup_stats = {
                'sessions_removed': 0,
                'files_removed': 0,
                'conversations_removed': 0,
                'errors': []
            }
            
            sessions_to_remove = []
            
            # Find sessions to remove
            for session_id, context in list(self.analysis_contexts.items()):
                try:
                    timestamp_str = context.get('timestamp')
                    if timestamp_str:
                        session_timestamp = datetime.fromisoformat(timestamp_str)
                        if session_timestamp < cutoff_date:
                            sessions_to_remove.append(session_id)
                    else:
                        # Remove sessions without timestamp (corrupted)
                        sessions_to_remove.append(session_id)
                        
                except Exception as e:
                    cleanup_stats['errors'].append(f"Session {session_id} timestamp check: {str(e)}")
            
            # Remove old sessions
            for session_id in sessions_to_remove:
                try:
                    # Count conversations before removal
                    conversations_count = len(self.conversation_history.get(session_id, []))
                    cleanup_stats['conversations_removed'] += conversations_count
                    
                    # Remove from memory
                    if session_id in self.analysis_contexts:
                        del self.analysis_contexts[session_id]
                        cleanup_stats['sessions_removed'] += 1
                    
                    if session_id in self.document_contexts:
                        del self.document_contexts[session_id]
                    
                    if session_id in self.conversation_history:
                        del self.conversation_history[session_id]
                    
                    # Remove from storage
                    storage_file = os.path.join(self.session_storage_dir, f"{session_id}.pkl")
                    if os.path.exists(storage_file):
                        os.remove(storage_file)
                        cleanup_stats['files_removed'] += 1
                        
                except Exception as e:
                    cleanup_stats['errors'].append(f"Remove session {session_id}: {str(e)}")
            
            self.logger.info(f"QA Agent cleanup completed: {cleanup_stats['sessions_removed']} sessions, {cleanup_stats['files_removed']} files removed")
            
            return cleanup_stats
            
        except Exception as e:
            self.logger.error(f"QA cleanup error: {str(e)}")
            return {
                'sessions_removed': 0,
                'files_removed': 0,
                'conversations_removed': 0,
                'errors': [str(e)]
            }
    
    def get_status(self) -> dict:
        """Get current status of QA Agent"""
        try:
            return {
                'status': 'active',
                'total_sessions': len(self.analysis_contexts),
                'total_conversations': sum(len(conv) for conv in self.conversation_history.values()),
                'storage_directory': self.session_storage_dir,
                'storage_available': os.path.exists(self.session_storage_dir),
                'groq_api_available': bool(os.getenv('GROQ_API_KEY')),
                'last_activity': max(
                    [datetime.fromisoformat(ctx.get('timestamp', '1970-01-01T00:00:00')) 
                     for ctx in self.analysis_contexts.values()],
                    default=datetime.now()
                ).isoformat()
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }