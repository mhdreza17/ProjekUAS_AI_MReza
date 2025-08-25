import os
import time
import re
from groq import Groq
from .base_agent import BaseAgent
from .standard_retriever import StandardRetrieverAgent

class ComplianceCheckerAgent(BaseAgent):
    """Enhanced Agent untuk mengecek compliance dokumen dengan analisis adaptif"""
    
    def __init__(self):
        super().__init__("ComplianceChecker")
        self.groq_client = Groq(api_key=os.getenv('GROQ_API_KEY'))
        self.standard_retriever = StandardRetrieverAgent()
        self.last_api_call = 0
        self.min_delay = 3  # Increased to 3 seconds to avoid rate limiting
        
        # Flexible compliance framework - akan disesuaikan berdasarkan dokumen
        self.base_compliance_aspects = {
            "data_collection_basis": {
                "name": "Dasar Hukum Pengumpulan Data",
                "keywords": ["dasar hukum", "legal basis", "persetujuan", "consent", "legitimate interest", "lawful basis"],
                "weight": 0.15
            },
            "user_data_rights": {
                "name": "Hak Pengguna atas Data", 
                "keywords": ["hak pengguna", "user rights", "hak akses", "right to access", "hak hapus", "right to delete", "portabilitas"],
                "weight": 0.15
            },
            "data_storage_location": {
                "name": "Lokasi Penyimpanan Data",
                "keywords": ["lokasi", "location", "server", "penyimpanan", "storage", "indonesia", "data center", "cloud"],
                "weight": 0.10
            },
            "data_retention": {
                "name": "Periode Retensi Data",
                "keywords": ["retensi", "retention", "periode", "period", "penyimpanan", "storage duration", "penghapusan"],
                "weight": 0.12
            },
            "data_security": {
                "name": "Keamanan Data",
                "keywords": ["keamanan", "security", "enkripsi", "encryption", "proteksi", "protection", "cybersecurity", "ssl", "tls"],
                "weight": 0.15
            },
            "data_access_correction": {
                "name": "Akses dan Koreksi Data",
                "keywords": ["akses", "access", "koreksi", "correction", "update", "modify", "rectification"],
                "weight": 0.10
            },
            "data_transfer": {
                "name": "Transfer Data",
                "keywords": ["transfer", "sharing", "berbagi", "pengalihan", "third party", "pihak ketiga"],
                "weight": 0.10
            },
            "privacy_policy": {
                "name": "Kebijakan Privasi",
                "keywords": ["privacy policy", "kebijakan privasi", "privacy notice", "pemberitahuan privasi"],
                "weight": 0.08
            },
            "cookies_tracking": {
                "name": "Cookies dan Tracking",
                "keywords": ["cookies", "cookie", "tracking", "pelacakan", "analytics", "beacons"],
                "weight": 0.05
            }
        }
        
    def process(self, document_text: str, selected_standards):
        """Enhanced analysis compliance dokumen dengan pendekatan adaptif"""
        self.set_status("analyzing")
        # Pastikan selected_standards selalu list
        if not isinstance(selected_standards, list) or selected_standards is None:
            self.log_action("WARNING: Invalid standards input, fallback to empty list", f"Value: {selected_standards}")
            selected_standards = []
        self.log_action("Starting adaptive compliance analysis", f"Standards: {selected_standards}")

        if not document_text or len(document_text.strip()) < 50:
            return {'success': False, 'error': 'Document text is empty or too short'}

        try:
            # Step 1: Analyze document structure and content
            document_analysis = self._analyze_document_structure(document_text)
            self.log_action("Document structure analyzed", f"Type: {document_analysis['document_type']}")

            # Step 2: Determine relevant compliance aspects based on document content
            relevant_aspects = self._determine_relevant_aspects(document_text, document_analysis)
            self.log_action("Relevant aspects determined", f"Count: {len(relevant_aspects)}")

            # Step 3: Load and prepare standards
            self.standard_retriever.load_selected_standards(selected_standards)

            # Step 4: Analyze each relevant aspect
            analysis_results = {
                'compliance_score': 0,
                'issues': [],
                'compliant_items': [],
                'recommendations': [],
                'analyzed_standards': selected_standards,
                'document_text': document_text,
                'document_analysis': document_analysis,
                'detailed_findings': [],
                'aspect_scores': {}
            }

            total_weight = 0
            weighted_score = 0

            for aspect_key, aspect_info in relevant_aspects.items():
                self.log_action("Analyzing relevant aspect", aspect_info['name'])

                # Get relevant standards for this aspect
                relevant_standards = self.standard_retriever.process(
                    f"{aspect_info['name']} {' '.join(aspect_info['keywords'])}",
                    top_k=3,
                    selected_standards=selected_standards
                )

                # Only use requirements if found in standards
                requirements = []
                for std in relevant_standards.get('standards', []):
                    req_text = std.get('content', '')
                    if req_text and len(req_text) > 30:
                        requirements.append({
                            'requirement': req_text,
                            'reference': std.get('article', std.get('source', '')),
                            'source': std.get('source', ''),
                            'full_name': std.get('full_name', '')
                        })

                # Analyze compliance for this aspect
                compliance_result = self._analyze_aspect_with_context(
                    document_text, aspect_key, aspect_info,
                    relevant_standards.get('standards', []),
                    document_analysis
                )

                if compliance_result:
                    weight = aspect_info.get('weight', 0.1)
                    total_weight += weight

                    # Compliance/non-compliance logic
                    if compliance_result.get('is_compliant') and compliance_result.get('confidence_score', 0) >= 0.5:
                        compliance_result['requirements'] = requirements
                        analysis_results['compliant_items'].append(compliance_result)
                        weighted_score += weight * compliance_result.get('confidence_score', 1.0)
                    else:
                        compliance_result['requirements'] = requirements
                        analysis_results['issues'].append(compliance_result)
                        weighted_score += weight * compliance_result.get('confidence_score', 0.0)

                    analysis_results['aspect_scores'][aspect_key] = {
                        'score': compliance_result.get('confidence_score', 0),
                        'weight': weight,
                        'weighted_contribution': weight * compliance_result.get('confidence_score', 0)
                    }

                    # Only add findings if requirements/evidence exist
                    if requirements or compliance_result.get('document_evidence'):
                        analysis_results['detailed_findings'].append({
                            'aspect': aspect_info['name'],
                            'aspect_key': aspect_key,
                            'weight': weight,
                            'result': compliance_result,
                            'document_excerpts': self._extract_relevant_excerpts_enhanced(document_text, aspect_info),
                            'standards_applied': relevant_standards.get('standards', [])[:2]
                        })

            # Calculate final score
            if total_weight > 0:
                analysis_results['compliance_score'] = round((weighted_score / total_weight) * 100, 1)
            else:
                analysis_results['compliance_score'] = 0.0

            # Generate enhanced recommendations
            analysis_results['recommendations'] = self._generate_smart_recommendations(
                analysis_results['issues'],
                analysis_results['compliant_items'],
                document_analysis,
                selected_standards
            )

            self.set_status("completed")
            self.log_action("Adaptive analysis completed",
                          f"Score: {analysis_results['compliance_score']}% | Aspects: {len(relevant_aspects)}")

            return {'success': True, 'analysis': analysis_results}

        except Exception as e:
            self.set_status("error")
            self.log_action("Analysis error", str(e))
            return {'success': False, 'error': str(e)}

    def _analyze_document_structure(self, document_text: str) -> dict:
        """Analyze document structure and type to understand context"""
        lines = document_text.split('\n')
        words = document_text.split()
        text_lower = document_text.lower()
        
        # Enhanced document type detection
        doc_patterns = {
            'Privacy Policy': ['privacy policy', 'kebijakan privasi', 'data protection policy', 'perlindungan data'],
            'Terms of Service': ['terms of service', 'syarat ketentuan', 'terms and conditions', 'ketentuan layanan'],
            'Cookie Policy': ['cookie policy', 'kebijakan cookie', 'penggunaan cookie'],
            'Data Processing Agreement': ['data processing', 'pengolahan data', 'dpa', 'agreement'],
            'Security Policy': ['security policy', 'kebijakan keamanan', 'information security'],
            'User Agreement': ['user agreement', 'perjanjian pengguna', 'kesepakatan pengguna'],
            'Website Policy': ['website policy', 'kebijakan website', 'situs web']
        }
        
        detected_type = 'General Document'
        confidence = 0.0
        
        for doc_type, patterns in doc_patterns.items():
            matches = sum(1 for pattern in patterns if pattern in text_lower)
            current_confidence = matches / len(patterns)
            if current_confidence > confidence:
                confidence = current_confidence
                detected_type = doc_type
        
        # Analyze content themes
        themes = self._extract_content_themes(text_lower)
        
        # Extract sections
        sections = self._extract_document_sections(document_text)
        
        # Detect language with higher accuracy
        language = self._detect_language_enhanced(document_text)
        
        return {
            'document_type': detected_type,
            'confidence': confidence,
            'word_count': len(words),
            'line_count': len(lines),
            'character_count': len(document_text),
            'sections': list(sections.keys()),
            'themes': themes,
            'language': language,
            'complexity_score': self._calculate_complexity_score(document_text)
        }
    
    def _extract_content_themes(self, text_lower: str) -> list:
        """Extract main content themes from document"""
        theme_keywords = {
            'Data Privacy': ['data pribadi', 'personal data', 'privacy', 'privasi', 'informasi pribadi'],
            'Security': ['keamanan', 'security', 'proteksi', 'protection', 'aman', 'secure'],
            'User Rights': ['hak pengguna', 'user rights', 'hak user', 'rights'],
            'Data Processing': ['pengolahan data', 'data processing', 'pemrosesan', 'proses data'],
            'Consent': ['persetujuan', 'consent', 'izin', 'approval'],
            'Sharing': ['berbagi', 'sharing', 'share', 'pembagian'],
            'Storage': ['penyimpanan', 'storage', 'simpan', 'store'],
            'Cookies': ['cookies', 'cookie', 'kue', 'tracking'],
            'Third Party': ['pihak ketiga', 'third party', 'partner'],
            'Legal': ['hukum', 'legal', 'law', 'peraturan', 'regulasi']
        }
        
        detected_themes = []
        for theme, keywords in theme_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                # Calculate theme relevance
                count = sum(text_lower.count(keyword) for keyword in keywords)
                detected_themes.append({'theme': theme, 'relevance': count})
        
        # Sort by relevance and return top themes
        detected_themes.sort(key=lambda x: x['relevance'], reverse=True)
        return [theme['theme'] for theme in detected_themes[:5]]
    
    def _determine_relevant_aspects(self, document_text: str, document_analysis: dict) -> dict:
        """Determine which compliance aspects are relevant based on document content"""
        relevant_aspects = {}
        text_lower = document_text.lower()
        themes = document_analysis.get('themes', [])
        
        for aspect_key, aspect_info in self.base_compliance_aspects.items():
            # Check keyword presence
            keyword_matches = sum(1 for keyword in aspect_info['keywords'] if keyword in text_lower)
            keyword_relevance = keyword_matches / len(aspect_info['keywords'])
            
            # Check theme alignment
            theme_relevance = 0
            aspect_themes = {
                'data_collection_basis': ['Data Privacy', 'Legal'],
                'user_data_rights': ['User Rights', 'Data Privacy'],
                'data_storage_location': ['Storage', 'Security'],
                'data_retention': ['Storage', 'Data Processing'],
                'data_security': ['Security', 'Data Privacy'],
                'data_access_correction': ['User Rights', 'Data Processing'],
                'data_transfer': ['Sharing', 'Third Party'],
                'privacy_policy': ['Data Privacy', 'Legal'],
                'cookies_tracking': ['Cookies', 'Third Party']
            }
            
            if aspect_key in aspect_themes:
                theme_matches = sum(1 for theme in aspect_themes[aspect_key] if theme in themes)
                theme_relevance = theme_matches / len(aspect_themes[aspect_key]) if aspect_themes[aspect_key] else 0
            
            # Combined relevance score
            relevance_score = (keyword_relevance * 0.7) + (theme_relevance * 0.3)
            
            # Include aspect if relevance is above threshold or if it's high priority
            high_priority_aspects = ['data_collection_basis', 'user_data_rights', 'data_security']
            if relevance_score > 0.1 or aspect_key in high_priority_aspects:
                # Adjust weight based on relevance
                adjusted_weight = aspect_info['weight'] * (1 + relevance_score)
                
                relevant_aspects[aspect_key] = {
                    **aspect_info,
                    'weight': adjusted_weight,
                    'relevance_score': relevance_score,
                    'keyword_matches': keyword_matches
                }
                
        # Ensure we have at least 3 aspects
        if len(relevant_aspects) < 3:
            # Add most important aspects if not already included
            for aspect_key in ['data_collection_basis', 'user_data_rights', 'data_security']:
                if aspect_key not in relevant_aspects:
                    relevant_aspects[aspect_key] = self.base_compliance_aspects[aspect_key]
        
        # Normalize weights
        total_weight = sum(aspect['weight'] for aspect in relevant_aspects.values())
        if total_weight > 0:
            for aspect_key in relevant_aspects:
                relevant_aspects[aspect_key]['weight'] = relevant_aspects[aspect_key]['weight'] / total_weight
        
        return relevant_aspects
    
    def _analyze_aspect_with_context(self, document_text: str, aspect_key: str, aspect_info: dict, 
                                   relevant_standards: list, document_analysis: dict):
        """Enhanced analysis dengan konteks dokumen yang lebih baik"""
        try:
            # Rate limiting with exponential backoff
            current_time = time.time()
            time_since_last_call = current_time - self.last_api_call
            if time_since_last_call < self.min_delay:
                sleep_time = self.min_delay - time_since_last_call
                time.sleep(sleep_time)

            # Extract relevant excerpts with better context
            relevant_excerpts = self._extract_relevant_excerpts_enhanced(document_text, aspect_info)
            
            # Create focused analysis prompt
            standards_context = ""
            if relevant_standards:
                standards_context = "\n".join([
                    f"STANDAR {i+1}: {std.get('source', 'Unknown')} | {std.get('article', std.get('section', ''))} | {std.get('title', '')}:\n{std.get('content', '')[:400]}"
                    for i, std in enumerate(relevant_standards[:2])
                ])

            # Build context-aware prompt
            prompt = f"""Analisis dokumen untuk aspek: {aspect_info['name']}

KONTEKS DOKUMEN:
- Jenis: {document_analysis.get('document_type', 'Unknown')}
- Bahasa: {document_analysis.get('language', 'Unknown')}
- Tema utama: {', '.join(document_analysis.get('themes', []))}

DOKUMEN (excerpt):
{document_text[:1500]}

BAGIAN RELEVAN YANG DITEMUKAN:
{chr(10).join([f"- {excerpt['text'][:200]}..." for excerpt in relevant_excerpts[:3]]) if relevant_excerpts else "Tidak ada bagian spesifik ditemukan"}

STANDAR REFERENSI:
{standards_context if standards_context else "Menggunakan best practice umum"}

INSTRUKSI:
1. Cari bukti konkret dalam dokumen untuk aspek: {aspect_info['name']}.
2. Jika ada bukti parsial, beri skor sesuai kelengkapan.
3. Berikan confidence score 0.0-1.0 berdasarkan kekuatan bukti.
4. WAJIB sebutkan reference pasal/artikel dan nama dokumen standar (misal "GDPR Article 6", "UU PDP Pasal 26") di field 'reference'.
5. Evidence harus berupa kutipan konkret dari dokumen.

Berikan HANYA JSON response:
{{"is_compliant": true/false, "confidence_score": 0.0-1.0, "explanation": "penjelasan detail", "document_evidence": "kutipan konkret atau 'TIDAK DITEMUKAN'", "found_elements": ["elemen yang ditemukan"], "missing_elements": ["elemen yang hilang"], "recommendations": ["rekomendasi spesifik"], "severity": "LOW/MEDIUM/HIGH", "reference": "GDPR Article 6"}}"""

            try:
                response = self.groq_client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {
                            "role": "system",
                            "content": "Anda adalah ahli compliance yang objektif. Berikan analisis berdasarkan bukti konkret. Gunakan confidence score untuk menunjukkan tingkat keyakinan."
                        },
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.2,
                    max_tokens=1000
                )
                
                self.last_api_call = time.time()
                
            except Exception as api_error:
                if "429" in str(api_error):
                    self.log_action("Rate limit hit, using longer delay", "10 seconds")
                    time.sleep(10)
                    self.min_delay = min(self.min_delay + 1, 10)  # Adaptive delay
                raise api_error
            
            response_text = response.choices[0].message.content.strip()
            
            # Parse JSON response with better error handling
            try:
                import json

                # Clean response
                if response_text.startswith('```json'):
                    response_text = response_text[7:]
                if response_text.endswith('```'):
                    response_text = response_text[:-3]

                start_brace = response_text.find('{')
                end_brace = response_text.rfind('}')

                if start_brace != -1 and end_brace != -1:
                    response_text = response_text[start_brace:end_brace+1]

                result = json.loads(response_text)

                # Validate and enhance result
                result.setdefault('is_compliant', False)
                result.setdefault('confidence_score', 0.0)
                result.setdefault('aspect', aspect_info['name'])
                result.setdefault('aspect_key', aspect_key)
                result.setdefault('found_elements', [])
                result.setdefault('missing_elements', [])
                result.setdefault('recommendations', [])
                result.setdefault('severity', 'MEDIUM')
                result.setdefault('reference', '')

                # Ensure confidence score is in valid range
                confidence = float(result.get('confidence_score', 0.0))
                result['confidence_score'] = max(0.0, min(1.0, confidence))

                # Add metadata
                result['keywords_found'] = len([k for k in aspect_info['keywords'] if k.lower() in document_text.lower()])
                result['excerpt_count'] = len(relevant_excerpts)
                result['standards_used'] = [std.get('source', 'Unknown') for std in relevant_standards[:2]]

                # Pastikan reference detail
                if not result['reference'] and relevant_standards:
                    ref_std = relevant_standards[0]
                    result['reference'] = f"{ref_std.get('source', '')} {ref_std.get('article', ref_std.get('section', ''))}".strip()

                return result

            except json.JSONDecodeError as parse_error:
                self.log_action("JSON parse failed, using fallback", str(parse_error))
                return self._create_fallback_result(aspect_key, aspect_info, relevant_excerpts)
                
        except Exception as e:
            self.log_action("Analysis error", f"{aspect_key}: {str(e)}")
            return self._create_fallback_result(aspect_key, aspect_info, [])
    
    def _create_fallback_result(self, aspect_key: str, aspect_info: dict, excerpts: list):
        """Create fallback result when API analysis fails"""
        # Simple keyword-based analysis as fallback
        has_evidence = len(excerpts) > 0
        confidence = 0.3 if has_evidence else 0.0
        
        return {
            "is_compliant": has_evidence,
            "confidence_score": confidence,
            "aspect": aspect_info['name'],
            "aspect_key": aspect_key,
            "explanation": f"Analisis fallback untuk {aspect_info['name']}. Ditemukan {len(excerpts)} bagian relevan.",
            "document_evidence": excerpts[0]['text'][:200] + "..." if excerpts else "TIDAK DITEMUKAN",
            "found_elements": ["Bukti parsial ditemukan"] if has_evidence else [],
            "missing_elements": ["Detail implementasi", "Spesifikasi lengkap"],
            "recommendations": [f"Perjelas dan lengkapi bagian {aspect_info['name']}"],
            "severity": "MEDIUM",
            "keywords_found": 0,
            "excerpt_count": len(excerpts),
            "standards_used": []
        }
    
    def _extract_relevant_excerpts_enhanced(self, document_text: str, aspect_info: dict) -> list:
        """Enhanced extraction with better context and scoring"""
        excerpts = []
        paragraphs = [p.strip() for p in document_text.split('\n\n') if len(p.strip()) > 30]
        keywords = [k.lower() for k in aspect_info['keywords']]
        
        for i, paragraph in enumerate(paragraphs):
            para_lower = paragraph.lower()
            
            # Calculate relevance score
            keyword_matches = sum(1 for keyword in keywords if keyword in para_lower)
            if keyword_matches > 0:
                # Context score based on surrounding content
                context_score = keyword_matches / len(keywords)
                
                # Length bonus for substantial paragraphs
                length_score = min(len(paragraph) / 500, 1.0)
                
                # Position score (early paragraphs might be more important)
                position_score = 1.0 - (i / len(paragraphs) * 0.3)
                
                total_score = context_score * 0.5 + length_score * 0.3 + position_score * 0.2
                
                excerpts.append({
                    'text': paragraph,
                    'score': total_score,
                    'keyword_matches': keyword_matches,
                    'paragraph_index': i
                })
        
        # Sort by score and return top excerpts
        excerpts.sort(key=lambda x: x['score'], reverse=True)
        return excerpts[:5]
    
    def _extract_document_sections(self, document_text: str) -> dict:
        """Extract document sections with improved patterns"""
        sections = {}
        lines = document_text.split('\n')
        current_section = None
        
        # Enhanced section patterns
        section_patterns = [
            r'^\d+\.?\s+([A-Z][^.!?]*)',  # Numbered sections
            r'^([A-Z][A-Z\s]{2,20}):?\s*$',  # ALL CAPS sections
            r'^([A-Za-z][^.!?]{5,50}):\s*$',  # Colon-terminated headers
            r'^#+\s+(.+)',  # Markdown headers
            r'^\*\*([^*]+)\*\*',  # Bold sections
        ]
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            for pattern in section_patterns:
                match = re.match(pattern, line)
                if match and len(line) < 100:  # Likely a header
                    current_section = match.group(1).strip()
                    sections[current_section] = []
                    break
            else:
                if current_section and len(line) > 10:
                    sections.setdefault(current_section, []).append(line)
        
        return sections
    
    def _detect_language_enhanced(self, text: str) -> str:
        """Enhanced language detection"""
        indonesian_words = ['dan', 'atau', 'yang', 'dengan', 'untuk', 'dari', 'dalam', 'pada', 'adalah', 'tidak', 
                           'akan', 'dapat', 'kami', 'anda', 'jika', 'setiap', 'seperti', 'hanya']
        english_words = ['the', 'and', 'or', 'with', 'for', 'from', 'in', 'on', 'is', 'not', 
                        'will', 'can', 'we', 'you', 'if', 'each', 'like', 'only']
        
        text_words = text.lower().split()
        id_count = sum(1 for word in indonesian_words if word in text_words)
        en_count = sum(1 for word in english_words if word in text_words)
        
        total_words = len(text_words)
        if total_words == 0:
            return 'Unknown'
        
        id_ratio = id_count / total_words
        en_ratio = en_count / total_words
        
        if id_ratio > en_ratio and id_ratio > 0.02:
            return 'Indonesian'
        elif en_ratio > id_ratio and en_ratio > 0.02:
            return 'English'
        else:
            return 'Mixed'
    
    def _calculate_complexity_score(self, document_text: str) -> float:
        """Calculate document complexity score"""
        words = document_text.split()
        sentences = re.split(r'[.!?]+', document_text)
        
        if not words or not sentences:
            return 0.0
        
        avg_word_length = sum(len(word) for word in words) / len(words)
        avg_sentence_length = len(words) / len(sentences)
        
        # Normalize scores
        word_complexity = min(avg_word_length / 8, 1.0)
        sentence_complexity = min(avg_sentence_length / 20, 1.0)
        
        return (word_complexity + sentence_complexity) / 2
    
    def _generate_smart_recommendations(self, issues: list, compliant_items: list, 
                                      document_analysis: dict, selected_standards: list) -> list:
        """Generate smart, contextual recommendations"""
        recommendations = []
        
        # Priority-based recommendations
        high_priority_issues = [issue for issue in issues if issue.get('severity') == 'HIGH']
        medium_priority_issues = [issue for issue in issues if issue.get('severity') == 'MEDIUM']
        
        if high_priority_issues:
            recommendations.append("🚨 PRIORITAS TINGGI:")
            for issue in high_priority_issues[:3]:
                if issue.get('recommendations'):
                    recommendations.extend([f"• {rec}" for rec in issue['recommendations'][:2]])
        
        if medium_priority_issues:
            recommendations.append("⚠️ PRIORITAS MENENGAH:")
            for issue in medium_priority_issues[:3]:
                if issue.get('recommendations'):
                    recommendations.extend([f"• {rec}" for rec in issue['recommendations'][:1]])
        
        # Document-type specific recommendations
        doc_type = document_analysis.get('document_type', '')
        if 'Privacy Policy' in doc_type:
            recommendations.extend([
                "📋 KHUSUS PRIVACY POLICY:",
                "• Pastikan informasi kontak Data Protection Officer tersedia",
                "• Sertakan prosedur untuk penarikan consent",
                "• Jelaskan mekanisme complaint dan dispute resolution"
            ])
        elif 'Terms of Service' in doc_type:
            recommendations.extend([
                "📋 KHUSUS TERMS OF SERVICE:",
                "• Pastikan klausul liability limitation sesuai hukum yang berlaku",
                "• Sertakan prosedur dispute resolution",
                "• Jelaskan hak dan kewajiban pengguna dengan jelas"
            ])
        
        # Standard-specific recommendations
        standard_recommendations = {
            'GDPR': [
                "🇪🇺 GDPR COMPLIANCE:",
                "• Implementasikan Privacy by Design principles",
                "• Pastikan legal basis untuk setiap data processing activity",
                "• Sediakan data portability mechanism"
            ],
            'UU_PDP': [
                "🇮🇩 UU PDP COMPLIANCE:",
                "• Pastikan data disimpan di Indonesia sesuai Pasal 17",
                "• Implementasikan notifikasi breach dalam 3x24 jam",
                "• Sediakan mekanisme consent yang mudah diakses"
            ],
            'BSSN': [
                "🛡️ KEAMANAN SIBER:",
                "• Implementasikan multi-factor authentication",
                "• Lakukan penetration testing berkala",
                "• Siapkan incident response plan yang comprehensive"
            ]
        }
        
        for standard in selected_standards:
            if standard in standard_recommendations:
                recommendations.extend(standard_recommendations[standard])
        
        # Performance-based recommendations
        compliant_ratio = len(compliant_items) / (len(compliant_items) + len(issues)) if (compliant_items or issues) else 0
        
        if compliant_ratio < 0.3:
            recommendations.extend([
                "🔧 PERBAIKAN MENYELURUH:",
                "• Lakukan review komprehensif terhadap seluruh dokumen",
                "• Konsultasi dengan legal expert untuk compliance gaps",
                "• Implementasikan document version control system"
            ])
        elif compliant_ratio > 0.8:
            recommendations.extend([
                "✨ OPTIMISASI LANJUTAN:",
                "• Lakukan audit internal berkala (quarterly)",
                "• Implementasikan continuous compliance monitoring",
                "• Siapkan compliance training untuk tim"
            ])
        
        # Add general best practices if few recommendations
        if len(recommendations) < 5:
            recommendations.extend([
                "💡 REKOMENDASI UMUM:",
                "• Lakukan review dan update dokumen secara berkala (minimal 6 bulan)",
                "• Dokumentasikan semua perubahan kebijakan dengan proper versioning",
                "• Siapkan komunikasi perubahan kebijakan kepada pengguna",
                "• Implementasikan feedback mechanism untuk user concerns"
            ])
        
        return recommendations