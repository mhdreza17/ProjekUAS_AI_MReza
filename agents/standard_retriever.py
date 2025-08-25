import os
import json
import chromadb
from sentence_transformers import SentenceTransformer
import fitz  # PyMuPDF
import shutil
import tempfile
import uuid
import re
from .base_agent import BaseAgent

os.environ['ANONYMIZED_TELEMETRY'] = 'False'
os.environ['CHROMA_CLIENT_AUTH_PROVIDER'] = ''
os.environ['CHROMA_SERVER_NOFILE'] = '1'
os.environ['CHROMA_SERVER_CORS_ALLOW_ORIGINS'] = '[]'

class StandardRetrieverAgent(BaseAgent):
    def process(self, query, top_k=3, selected_standards=None):
        """Process query and return standards, fallback to default if none found"""
        try:
            # ...existing code...
            # Simulate retrieval logic (replace with actual retrieval)
            standards = {'success': True, 'standards': []}  # Replace with actual retrieval
            # ...existing code...
            if not standards['standards']:
                return {
                    'success': True,
                    'standards': [],
                    'message': 'Tidak ada standar yang relevan ditemukan untuk pertanyaan ini. Silakan cek hasil analisis atau tanyakan hal lain.'
                }
            return standards
        except Exception as e:
            return {
                'success': False,
                'standards': [],
                'error': str(e),
                'message': 'Terjadi kesalahan saat mengambil standar. Silakan coba lagi.'
            }
    """Enhanced Agent untuk mengelola dan mengambil standar regulasi dengan akurasi tinggi"""
    
    def __init__(self):
        super().__init__("StandardRetriever")
        
        self.instance_id = str(uuid.uuid4())[:8]
        self.client = None
        self.collection = None
        self.embedding_model = None
        self._standards_loaded = False
        
        # Enhanced standards mapping dengan metadata lengkap
        self.standards_mapping = {
            'GDPR': {
                'files': ['GDPR.pdf'],
                'category': 'Global',
                'full_name': 'General Data Protection Regulation',
                'jurisdiction': 'European Union',
                'focus_areas': ['data protection', 'privacy rights', 'consent', 'data processing']
            },
            'NIST': {
                'files': ['NIST.pdf'], 
                'category': 'Global',
                'full_name': 'NIST Cybersecurity Framework',
                'jurisdiction': 'United States',
                'focus_areas': ['cybersecurity', 'risk management', 'security controls', 'incident response']
            },
            'UU_PDP': {
                'files': ['UU_PDP.pdf'],
                'category': 'Nasional', 
                'full_name': 'Undang-Undang Perlindungan Data Pribadi',
                'jurisdiction': 'Indonesia',
                'focus_areas': ['data pribadi', 'perlindungan data', 'hak subjek data', 'pengolahan data']
            },
            'POJK': {
                'files': ['POJK.pdf'],
                'category': 'Nasional',
                'full_name': 'Peraturan OJK Perlindungan Konsumen',
                'jurisdiction': 'Indonesia', 
                'focus_areas': ['perlindungan konsumen', 'layanan keuangan', 'transparansi', 'keluhan konsumen']
            },
            'BSSN': {
                'files': ['BSSN_A.pdf', 'BSSN_B.pdf', 'BSSN_C.pdf'],
                'category': 'Nasional',
                'full_name': 'Peraturan BSSN Keamanan Siber', 
                'jurisdiction': 'Indonesia',
                'focus_areas': ['keamanan siber', 'sistem elektronik', 'insiden siber', 'audit keamanan']
            }
        }
        
        self._initialize_components()
        
    def _initialize_components(self):
        """Initialize ChromaDB and embedding model dengan error handling yang lebih baik"""
        try:
            # Disable telemetry
            try:
                import chromadb.config
                import chromadb.telemetry.product.posthog
                chromadb.telemetry.product.posthog.Posthog = lambda *args, **kwargs: None
            except:
                pass
            
            # Initialize ChromaDB client
            self.client = chromadb.EphemeralClient(
                settings=chromadb.config.Settings(
                    anonymized_telemetry=False,
                    allow_reset=True,
                    is_persistent=False
                )
            )
            
            # Initialize embedding model with error handling
            try:
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
                self.log_action("Embedding model loaded", "all-MiniLM-L6-v2")
            except Exception as e:
                self.log_action("Embedding model load failed", str(e))
                raise e
            
            # Create collection with enhanced metadata
            collection_name = f"enhanced_standards_{self.instance_id}"
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={
                    "description": f"Enhanced standards collection for instance {self.instance_id}",
                    "version": "2.0",
                    "created_at": str(uuid.uuid4())
                }
            )
            
            self.log_action("Enhanced components initialized", f"Instance: {self.instance_id}")
            
        except Exception as e:
            self.log_action("Initialization error, using fallback", str(e))
            self._create_enhanced_fallback_storage()
    
    def _create_enhanced_fallback_storage(self):
        """Create enhanced fallback storage with better organization"""
        self.fallback_storage = {
            'documents': [],
            'embeddings': [],
            'metadatas': [],
            'ids': [],
            'standards_index': {},  # Index by standard type for faster lookup
            'keyword_index': {}     # Keyword index for better search
        }
        self.client = None
        self.collection = None
        self.log_action("Enhanced fallback storage created", "Using improved in-memory storage")
    
    def load_selected_standards(self, selected_standards: list):
        """Enhanced loading dengan processing yang lebih baik"""
        self.set_status("loading_selected_standards")
        self.log_action("Loading enhanced standards", f"Standards: {selected_standards}")
        # Validation: standards must be a non-empty list
        if not selected_standards or not isinstance(selected_standards, list):
            self.log_action("ERROR: Invalid standards input", f"Value: {selected_standards}")
            return 0
        try:
            loaded_count = 0
            processing_errors = []
            standards_dir = "standards"
            if not os.path.exists(standards_dir):
                self.log_action("ERROR: Standards directory not found", f"Path: {os.path.abspath(standards_dir)}")
                return 0
            self.log_action("Standards directory found", f"Path: {os.path.abspath(standards_dir)}")
            for standard in selected_standards:
                if standard in self.standards_mapping:
                    standard_info = self.standards_mapping[standard]
                    pdf_files = standard_info['files']
                    category = standard_info['category']
                    for pdf_file in pdf_files:
                        filepath = os.path.join(standards_dir, category, pdf_file)
                        if os.path.exists(filepath):
                            try:
                                success = self._load_pdf_standard_enhanced(
                                    filepath, category, pdf_file, standard, standard_info
                                )
                                if success:
                                    loaded_count += 1
                                    self.log_action("SUCCESS: Enhanced PDF loaded", f"{pdf_file} for {standard}")
                                else:
                                    processing_errors.append(f"Failed to process {pdf_file}")
                            except Exception as e:
                                error_msg = f"{pdf_file}: {str(e)}"
                                processing_errors.append(error_msg)
                                self.log_action("ERROR: Enhanced PDF load failed", error_msg)
                        else:
                            # Try alternative paths
                            alt_paths = [
                                os.path.join(standards_dir, pdf_file),
                                pdf_file
                            ]
                            found = False
                            for alt_path in alt_paths:
                                if os.path.exists(alt_path):
                                    try:
                                        success = self._load_pdf_standard_enhanced(
                                            alt_path, category, pdf_file, standard, standard_info
                                        )
                                        if success:
                                            loaded_count += 1
                                            found = True
                                            break
                                    except Exception as e:
                                        processing_errors.append(f"Alternative path {alt_path}: {str(e)}")
                            
                            if not found:
                                processing_errors.append(f"File not found: {filepath}")
                                self.log_action("ERROR: PDF not found", filepath)
                else:
                    processing_errors.append(f"Unknown standard: {standard}")
                    self.log_action("ERROR: Unknown standard", standard)
            
            self._standards_loaded = True
            self._build_enhanced_indexes()  # Build indexes for better search
            
            # Verification
            total_items = 0
            if self.collection is not None:
                try:
                    all_items = self.collection.get()
                    total_items = len(all_items['ids']) if all_items['ids'] else 0
                except Exception as e:
                    self.log_action("ChromaDB verification failed", str(e))
            elif hasattr(self, 'fallback_storage'):
                total_items = len(self.fallback_storage['documents'])
            
            self.log_action("Enhanced standards loading completed", 
                          f"Loaded: {loaded_count} files, Total items: {total_items}, Errors: {len(processing_errors)}")
            
            if processing_errors:
                self.log_action("Processing errors encountered", "; ".join(processing_errors[:5]))
            
            return loaded_count
            
        except Exception as e:
            self.log_action("CRITICAL ERROR: Enhanced loading failed", str(e))
            return 0
    
    def _load_pdf_standard_enhanced(self, filepath: str, category: str, filename: str, ui_standard: str, standard_info: dict) -> bool:
        """Enhanced PDF loading dengan better text processing"""
        try:
            doc = fitz.open(filepath)
            chunks_created = 0
            # Process more pages for better coverage
            max_pages = min(doc.page_count, 15)
            for page_num in range(max_pages):
                page = doc[page_num]
                text = page.get_text()
                # Enhanced text cleaning
                cleaned_text = self._clean_extracted_text(text)
                if len(cleaned_text.strip()) > 100:
                    # Smart chunking based on content structure
                    chunks = self._create_smart_chunks(cleaned_text, standard_info)
                    for i, chunk in enumerate(chunks):
                        if len(chunk.strip()) > 50:  # Only meaningful chunks
                            chunk_id = f"{filename}_p{page_num+1}_c{i+1}_{self.instance_id}"
                            # Enhanced metadata
                            # Extract article/section from chunk
                            article_match = None
                            # English: Article/Section
                            match = re.search(r'(Article|Section)\s*(\d+[A-Za-z]*)', chunk, re.IGNORECASE)
                            if match:
                                article_match = f"{match.group(1).capitalize()} {match.group(2)}"
                            # Indonesian: Pasal
                            match_id = re.search(r'(Pasal)\s*(\d+[A-Za-z]*)', chunk, re.IGNORECASE)
                            if match_id:
                                article_match = f"{match_id.group(1).capitalize()} {match_id.group(2)}"
                            # If not found, fallback to page
                            if not article_match:
                                article_match = f"Page {page_num+1}"
                            metadata = {
                                'source': filename,
                                'category': category,
                                'page': page_num + 1,
                                'chunk': i + 1,
                                'standard_type': self._identify_standard_type(filename),
                                'ui_standard': ui_standard,
                                'full_name': standard_info.get('full_name', ''),
                                'jurisdiction': standard_info.get('jurisdiction', ''),
                                'focus_areas': ','.join(standard_info.get('focus_areas', [])),
                                'text_length': len(chunk),
                                'keywords': self._extract_keywords_from_chunk(chunk),
                                'section_type': self._identify_section_type(chunk),
                                'article': article_match
                            }
                            # Store in ChromaDB or fallback
                            if self.collection is not None:
                                try:
                                    embedding = self.embedding_model.encode([chunk]).tolist()[0]
                                    self.collection.add(
                                        embeddings=[embedding],
                                        documents=[chunk],
                                        metadatas=[metadata],
                                        ids=[chunk_id]
                                    )
                                    chunks_created += 1
                                except Exception as e:
                                    if "already exists" not in str(e).lower():
                                        self.log_action("ChromaDB add error", f"{chunk_id}: {str(e)}")
                            else:
                                # Enhanced fallback storage
                                if not hasattr(self, 'fallback_storage'):
                                    self._create_enhanced_fallback_storage()
                                self.fallback_storage['documents'].append(chunk)
                                self.fallback_storage['metadatas'].append(metadata)
                                self.fallback_storage['ids'].append(chunk_id)
                                # Update indexes
                                if ui_standard not in self.fallback_storage['standards_index']:
                                    self.fallback_storage['standards_index'][ui_standard] = []
                                self.fallback_storage['standards_index'][ui_standard].append(len(self.fallback_storage['documents']) - 1)
                                chunks_created += 1
            doc.close()
            self.log_action("Enhanced PDF processed", f"{filename}: {chunks_created} chunks created")
            return True
        except Exception as e:
            self.log_action("PDF load error", f"{filename}: {str(e)}")
            return False
        
    def _extract_keywords_from_chunk(self, chunk: str) -> str:
        """Extract relevant keywords from chunk for better indexing"""
        # Common compliance and regulatory keywords
        important_keywords = [
            'data', 'pribadi', 'personal', 'consent', 'persetujuan', 'processing', 'pengolahan',
            'security', 'keamanan', 'privacy', 'privasi', 'rights', 'hak', 'protection', 'perlindungan',
            'breach', 'pelanggaran', 'controller', 'pengendali', 'processor', 'pemroses',
            'transfer', 'storage', 'penyimpanan', 'retention', 'retensi', 'deletion', 'penghapusan',
            'audit', 'compliance', 'kepatuhan', 'regulation', 'regulasi', 'law', 'hukum'
        ]
        
        chunk_lower = chunk.lower()
        found_keywords = [kw for kw in important_keywords if kw in chunk_lower]
        
        return ','.join(found_keywords[:10])  # Limit to 10 keywords
    
    def _identify_section_type(self, chunk: str) -> str:
        """Identify the type of section based on content patterns"""
        chunk_lower = chunk.lower()
        
        section_patterns = {
            'definition': ['definition', 'definisi', 'means', 'berarti', 'refers to', 'mengacu'],
            'obligation': ['shall', 'must', 'wajib', 'harus', 'required', 'diwajibkan'],
            'prohibition': ['shall not', 'must not', 'tidak boleh', 'dilarang', 'prohibited'],
            'procedure': ['procedure', 'prosedur', 'process', 'proses', 'steps', 'langkah'],
            'penalty': ['penalty', 'sanksi', 'fine', 'denda', 'punishment', 'hukuman'],
            'right': ['right', 'hak', 'entitle', 'berhak', 'may request', 'dapat meminta']
        }
        
        for section_type, patterns in section_patterns.items():
            if any(pattern in chunk_lower for pattern in patterns):
                return section_type
        
        return 'general'
    
    def _build_enhanced_indexes(self):
        """Build enhanced indexes for better search performance"""
        if hasattr(self, 'fallback_storage') and self.fallback_storage['documents']:
            # Build keyword index
            for i, metadata in enumerate(self.fallback_storage['metadatas']):
                keywords = metadata.get('keywords', '').split(',')
                for keyword in keywords:
                    keyword = keyword.strip()
                    if keyword:
                        if keyword not in self.fallback_storage['keyword_index']:
                            self.fallback_storage['keyword_index'][keyword] = []
                        self.fallback_storage['keyword_index'][keyword].append(i)
        
        self.log_action("Enhanced indexes built", f"Keywords: {len(self.fallback_storage.get('keyword_index', {}))}")
    
    def process(self, query: str, top_k: int = 5, selected_standards: list = None):
        """Enhanced processing dengan better search algorithm"""
        self.set_status("retrieving")
        self.log_action("Enhanced retrieval process started", f"Query: {query[:100]}...")
        
        try:
            if selected_standards:
                if not self._standards_loaded:
                    loaded_count = self.load_selected_standards(selected_standards)
                    self.log_action("Standards loaded on demand", f"Loaded {loaded_count} files")
            elif not self._standards_loaded:
                self._load_standards_if_needed()
            
            # Enhanced search
            if self.collection is not None:
                result = self._enhanced_chromadb_query(query, top_k, selected_standards)
            else:
                result = self._enhanced_fallback_query(query, top_k, selected_standards)
            
            standards_count = len(result.get('standards', []))
            self.log_action("Enhanced retrieval completed", f"Found {standards_count} standards")
            
            return result
                
        except Exception as e:
            self.set_status("error")
            self.log_action("Enhanced retrieval error", str(e))
            return {
                'success': True,
                'standards': [],
                'query': query,
                'error': str(e)
            }
    
    def _enhanced_chromadb_query(self, query: str, top_k: int, selected_standards: list = None):
        """Enhanced ChromaDB query dengan filtering"""
        try:
            query_embedding = self.embedding_model.encode([query]).tolist()
            
            # Build where clause for filtering
            where_clause = None
            if selected_standards:
                where_clause = {"ui_standard": {"$in": selected_standards}}
            
            results = self.collection.query(
                query_embeddings=query_embedding,
                n_results=min(top_k * 2, 20),  # Get more results for better filtering
                include=['documents', 'metadatas', 'distances'],
                where=where_clause
            )
            
            retrieved_standards = []
            seen_articles = set()
            if results['documents'] and results['documents'][0]:
                # Enhanced result processing
                for i, (doc, metadata, distance) in enumerate(zip(
                    results['documents'][0], 
                    results['metadatas'][0], 
                    results['distances'][0]
                )):
                    # Calculate enhanced relevance score
                    relevance_score = self._calculate_enhanced_relevance(
                        query, doc, metadata, 1 - distance
                    )
                    article_id = metadata.get('article', f"Page {metadata.get('page', 'N/A')}")
                    # Only add if not duplicate and has valid article/section
                    if article_id and article_id not in seen_articles and len(doc.strip()) > 30:
                        seen_articles.add(article_id)
                        retrieved_standards.append({
                            'rank': len(retrieved_standards) + 1,
                            'content': doc,
                            'source': metadata.get('source', 'Unknown'),
                            'article': article_id,
                            'standard_type': metadata.get('standard_type', 'Unknown'),
                            'ui_standard': metadata.get('ui_standard', 'Unknown'),
                            'full_name': metadata.get('full_name', ''),
                            'section_type': metadata.get('section_type', 'general'),
                            'relevance_score': relevance_score,
                            'semantic_similarity': 1 - distance,
                            'keywords_matched': self._count_keyword_matches(query, metadata.get('keywords', '')),
                            'text_length': metadata.get('text_length', 0)
                        })
            # Sort by enhanced relevance score
            retrieved_standards.sort(key=lambda x: x['relevance_score'], reverse=True)
            # Return top_k results
            retrieved_standards = retrieved_standards[:top_k]
            
            self.set_status("completed")
            self.log_action("Enhanced ChromaDB query completed", f"Found {len(retrieved_standards)} items")
            
            return {
                'success': True,
                'standards': retrieved_standards,
                'query': query,
                'method': 'enhanced_chromadb'
            }
            
        except Exception as e:
            self.log_action("Enhanced ChromaDB query error", str(e))
            return self._enhanced_fallback_query(query, top_k, selected_standards)
    
    def _enhanced_fallback_query(self, query: str, top_k: int, selected_standards: list = None):
        """Enhanced fallback query dengan better matching"""
        try:
            if not hasattr(self, 'fallback_storage') or not self.fallback_storage['documents']:
                return {
                    'success': True,
                    'standards': [],
                    'query': query,
                    'message': 'No standards available'
                }
            
            query_lower = query.lower()
            query_words = set(query_lower.split())
            matches = []
            
            for i, (doc, metadata) in enumerate(zip(
                self.fallback_storage['documents'],
                self.fallback_storage['metadatas']
            )):
                # Filter by selected standards if specified
                if selected_standards and metadata.get('ui_standard') not in selected_standards:
                    continue
                
                # Enhanced matching algorithm
                relevance_score = self._calculate_enhanced_relevance(
                    query, doc, metadata, base_score=0.5
                )
                
                if relevance_score > 0.1:  # Threshold for inclusion
                    matches.append({
                        'rank': len(matches) + 1,
                        'content': doc,
                        'source': metadata.get('source', 'Unknown'),
                        'article': metadata.get('article', f"Page {metadata.get('page', 'N/A')}"),
                        'standard_type': metadata.get('standard_type', 'Unknown'),
                        'ui_standard': metadata.get('ui_standard', 'Unknown'),
                        'full_name': metadata.get('full_name', ''),
                        'section_type': metadata.get('section_type', 'general'),
                        'relevance_score': relevance_score,
                        'keywords_matched': self._count_keyword_matches(query, metadata.get('keywords', '')),
                        'text_length': metadata.get('text_length', 0)
                    })
            
            # Sort by relevance score
            matches.sort(key=lambda x: x['relevance_score'], reverse=True)
            
            # Return top results
            matches = matches[:top_k]
            
            self.set_status("completed")
            self.log_action("Enhanced fallback query completed", f"Found {len(matches)} matches")
            
            return {
                'success': True,
                'standards': matches,
                'query': query,
                'method': 'enhanced_fallback'
            }
            
        except Exception as e:
            self.log_action("Enhanced fallback query error", str(e))
            return {
                'success': True,
                'standards': [],
                'query': query,
                'error': str(e)
            }
    
    def _calculate_enhanced_relevance(self, query: str, document: str, metadata: dict, base_score: float = 0.5) -> float:
        """Calculate enhanced relevance score using multiple factors"""
        query_lower = query.lower()
        doc_lower = document.lower()
        
        # Factor 1: Direct keyword matches (40% weight)
        query_words = set(query_lower.split())
        doc_words = set(doc_lower.split())
        keyword_overlap = len(query_words.intersection(doc_words)) / len(query_words) if query_words else 0
        keyword_score = keyword_overlap * 0.4
        
        # Factor 2: Metadata keyword matches (20% weight)
        metadata_keywords = metadata.get('keywords', '').lower().split(',')
        metadata_matches = sum(1 for word in query_words if any(word in kw for kw in metadata_keywords))
        metadata_score = (metadata_matches / len(query_words)) * 0.2 if query_words else 0
        
        # Factor 3: Section type relevance (15% weight)
        section_type = metadata.get('section_type', 'general')
        section_bonus = 0.15 if section_type in ['obligation', 'procedure', 'right'] else 0.05
        
        # Factor 4: Text quality (10% weight)
        text_length = metadata.get('text_length', 0)
        length_score = min(text_length / 500, 1.0) * 0.1  # Optimal around 500 chars
        
        # Factor 5: Base semantic score (15% weight)
        semantic_score = base_score * 0.15
        
        # Combine all factors
        total_score = keyword_score + metadata_score + section_bonus + length_score + semantic_score
        
        return min(total_score, 1.0)  # Cap at 1.0
    
    def _count_keyword_matches(self, query: str, keywords_str: str) -> int:
        """Count how many query words match the stored keywords"""
        if not keywords_str:
            return 0
        
        query_words = set(query.lower().split())
        keywords = set(keywords_str.lower().split(','))
        
        matches = 0
        for query_word in query_words:
            if any(query_word in keyword for keyword in keywords):
                matches += 1
        
        return matches
    
    def _load_standards_if_needed(self):
        """Load standards if directory exists and not already loaded"""
        if self._standards_loaded:
            return
            
        standards_dir = "standards"
        if os.path.exists(standards_dir):
            self.load_standards_from_directory(standards_dir)
        else:
            self.log_action("Standards directory not found", "Skipping auto-load")
            self._standards_loaded = True
    
    def load_standards_from_directory(self, standards_dir: str):
        """Load all available standards from directory"""
        if self._standards_loaded:
            self.log_action("Standards already loaded", "Skipping reload")
            return 0
            
        self.set_status("loading_standards")
        self.log_action("Loading all standards", f"Directory: {standards_dir}")
        
        try:
            loaded_count = 0
            
            for category in ['Global', 'Nasional']:
                category_path = os.path.join(standards_dir, category)
                if not os.path.exists(category_path):
                    continue
                
                for filename in os.listdir(category_path):
                    if filename.endswith('.pdf'):
                        filepath = os.path.join(category_path, filename)
                        try:
                            ui_standard = self._get_ui_standard_from_filename(filename)
                            standard_info = self.standards_mapping.get(ui_standard, {
                                'full_name': filename.replace('.pdf', ''),
                                'jurisdiction': 'Unknown',
                                'focus_areas': []
                            })
                            
                            success = self._load_pdf_standard_enhanced(
                                filepath, category, filename, ui_standard, standard_info
                            )
                            if success:
                                loaded_count += 1
                        except Exception as e:
                            self.log_action("PDF load error", f"{filename}: {str(e)}")
            
            self._standards_loaded = True
            self._build_enhanced_indexes()
            self.log_action("All standards loaded", f"Total: {loaded_count} files")
            return loaded_count
            
        except Exception as e:
            self.log_action("Loading error", str(e))
            self._standards_loaded = True
            return 0
    
    def _get_ui_standard_from_filename(self, filename: str) -> str:
        """Get UI standard name from PDF filename with better matching"""
        filename_lower = filename.lower()
        
        # Direct mapping check
        for ui_standard, standard_info in self.standards_mapping.items():
            if any(pdf_file.lower() == filename_lower for pdf_file in standard_info['files']):
                return ui_standard
        
        # Fuzzy matching for common variations
        if 'gdpr' in filename_lower:
            return 'GDPR'
        elif 'nist' in filename_lower:
            return 'NIST'
        elif 'pdp' in filename_lower or 'perlindungan_data' in filename_lower:
            return 'UU_PDP'
        elif 'pojk' in filename_lower or 'ojk' in filename_lower:
            return 'POJK'
        elif 'bssn' in filename_lower:
            return 'BSSN'
        
        return 'Unknown'
    
    def _identify_standard_type(self, filename: str) -> str:
        """Identify standard type from filename"""
        return self._get_ui_standard_from_filename(filename)
    
    def get_available_standards(self):
        """Get list of available standards with enhanced metadata"""
        try:
            # Always load standards if not loaded
            if not self._standards_loaded:
                self._load_standards_if_needed()
            standards = {}
            if self.collection is not None:
                all_items = self.collection.get(include=['metadatas'])
                for metadata in all_items['metadatas']:
                    std_type = metadata.get('ui_standard', 'Unknown')
                    category = metadata.get('category', 'Unknown')
                    if category not in standards:
                        standards[category] = {}
                    if std_type not in standards[category]:
                        standards[category][std_type] = {
                            'full_name': metadata.get('full_name', std_type),
                            'jurisdiction': metadata.get('jurisdiction', 'Unknown'),
                            'focus_areas': metadata.get('focus_areas', '').split(',') if metadata.get('focus_areas') else [],
                            'chunk_count': 0
                        }
                    standards[category][std_type]['chunk_count'] += 1
            elif hasattr(self, 'fallback_storage'):
                for metadata in self.fallback_storage['metadatas']:
                    std_type = metadata.get('ui_standard', 'Unknown')
                    category = metadata.get('category', 'Unknown')
                    if category not in standards:
                        standards[category] = {}
                    if std_type not in standards[category]:
                        standards[category][std_type] = {
                            'full_name': metadata.get('full_name', std_type),
                            'jurisdiction': metadata.get('jurisdiction', 'Unknown'),
                            'focus_areas': metadata.get('focus_areas', '').split(',') if metadata.get('focus_areas') else [],
                            'chunk_count': 0
                        }
                    standards[category][std_type]['chunk_count'] += 1
            return standards
        except Exception as e:
            self.log_action("Get enhanced standards error", str(e))
            return {}
    
    def _clean_extracted_text(self, text: str) -> str:
        """Enhanced text cleaning untuk hasil yang lebih baik"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove page numbers and headers/footers patterns
        text = re.sub(r'\n\s*\d+\s*\n', '\n', text)
        text = re.sub(r'\n\s*Page\s+\d+.*?\n', '\n', text, flags=re.IGNORECASE)
        
        # Remove URLs and email patterns that might be noise
        text = re.sub(r'http[s]?://\S+', '', text)
        text = re.sub(r'\S+@\S+', '', text)
        
        # Clean up punctuation
        text = re.sub(r'([.!?])\1+', r'\1', text)  # Remove repeated punctuation
        
        # Normalize quotes
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")
        
        return text.strip()
    
    def _create_smart_chunks(self, text: str, standard_info: dict, chunk_size: int = 600) -> list:
        """Create smart chunks based on content structure"""
        # Try to split by natural boundaries first
        paragraphs = [p.strip() for p in text.split('\n\n') if len(p.strip()) > 20]
        
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            # If adding this paragraph would exceed chunk size
            if len(current_chunk) + len(paragraph) > chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = paragraph
            else:
                current_chunk = current_chunk + "\n\n" + paragraph if current_chunk else paragraph
        
        # Add the last chunk
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        # If no natural paragraphs, fall back to word-based chunking
        if not chunks or len(chunks) == 1 and len(chunks[0]) > chunk_size * 2:
            words = text.split()
            chunks = []
            for i in range(0, len(words), chunk_size // 8):  # Approximate words per chunk
                chunk = ' '.join(words[i:i + chunk_size // 8])
                if len(chunk.strip()) > 50:
                    chunks.append(chunk)
        
        return chunks