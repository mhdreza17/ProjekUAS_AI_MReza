// ReguBot Frontend JavaScript - FIXED VERSION
class ReguBot {
  constructor() {
    this.sessionId = null
    this.uploadedFile = null
    this.selectedStandards = []
    this.analysisResult = null
    this.isAnalysisComplete = false
    this.init()
  }

  init() {
    this.setupEventListeners()
    this.loadAvailableStandards()
    this.checkSystemStatus()
    console.log("🤖 ReguBot initialized - Enhanced Version")
  }

  setupEventListeners() {
    // File upload
    const uploadArea = document.getElementById("upload-area")
    const fileInput = document.getElementById("file-input")

    if (uploadArea && fileInput) {
      uploadArea.addEventListener("click", () => fileInput.click())
      uploadArea.addEventListener("dragover", (e) => {
        e.preventDefault()
        uploadArea.classList.add("border-blue-400")
      })
      uploadArea.addEventListener("dragleave", () => {
        uploadArea.classList.remove("border-blue-400")
      })
      uploadArea.addEventListener("drop", (e) => {
        e.preventDefault()
        uploadArea.classList.remove("border-blue-400")
        const files = e.dataTransfer.files
        if (files.length > 0) {
          this.handleFileSelect(files[0])
        }
      })

      fileInput.addEventListener("change", (e) => {
        if (e.target.files.length > 0) {
          this.handleFileSelect(e.target.files[0])
        }
      })
    }

    // Remove file
    const removeFileBtn = document.getElementById("remove-file")
    if (removeFileBtn) {
      removeFileBtn.addEventListener("click", () => {
        this.removeFile()
      })
    }

    // Analyze button
    const analyzeBtn = document.getElementById("analyze-btn")
    if (analyzeBtn) {
      analyzeBtn.addEventListener("click", () => {
        this.startAnalysis()
      })
    }

    // Chat functionality
    const sendChatBtn = document.getElementById("send-chat")
    const chatInput = document.getElementById("chat-input")

    if (sendChatBtn) {
      sendChatBtn.addEventListener("click", () => {
        this.sendChatMessage()
      })
    }

    if (chatInput) {
      chatInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
          e.preventDefault()
          this.sendChatMessage()
        }
      })
    }

    // Download buttons
    const downloadPdfBtn = document.getElementById("download-pdf")
    const downloadDocxBtn = document.getElementById("download-docx")

    if (downloadPdfBtn) {
      downloadPdfBtn.addEventListener("click", () => {
        this.downloadReport('pdf')
      })
    }

    if (downloadDocxBtn) {
      downloadDocxBtn.addEventListener("click", () => {
        this.downloadReport('docx')
      })
    }
  }

  async checkSystemStatus() {
    try {
      console.log("🔍 Checking system status...")
      const response = await fetch("/api/health")
      const status = await response.json()

      const indicator = document.getElementById("status-indicator")
      if (indicator) {
        if (status.status === 'healthy') {
          indicator.innerHTML = `
            <div class="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
            <span class="text-sm">Sistem Aktif - Enhanced v2.1</span>
          `
        } else {
          indicator.innerHTML = `
            <div class="w-3 h-3 bg-yellow-400 rounded-full animate-pulse"></div>
            <span class="text-sm">Sistem Terbatas</span>
          `
        }
      }
      console.log("✅ System status checked:", status.status)
    } catch (error) {
      console.error("❌ Error checking system status:", error)
      const indicator = document.getElementById("status-indicator")
      if (indicator) {
        indicator.innerHTML = `
          <div class="w-3 h-3 bg-red-400 rounded-full"></div>
          <span class="text-sm">Sistem Error</span>
        `
      }
    }
  }

  async loadAvailableStandards() {
    try {
      console.log("📚 Loading available standards...")
      const response = await fetch("/api/standards")
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }
      
      const result = await response.json()
      console.log("📊 Standards loaded:", result)

      if (result.success && result.standards) {
        // Handle new API response format
        this.renderStandardsNew(result.standards)
        console.log("✅ Standards rendered successfully")
      } else if (result.Global || result.Nasional) {
        // Handle legacy format
        this.renderStandards("global-standards", result.Global || [])
        this.renderStandards("national-standards", result.Nasional || [])
        console.log("✅ Standards rendered (legacy format)")
      } else {
        console.warn("⚠️ No standards data found")
        this.showStandardsError("Tidak ada standar yang tersedia")
      }
    } catch (error) {
      console.error("❌ Error loading standards:", error)
      this.showStandardsError("Gagal memuat standar: " + error.message)
    }
  }

  renderStandardsNew(standards) {
    // Render Global standards
    const globalContainer = document.getElementById("global-standards")
    const nationalContainer = document.getElementById("national-standards")

    if (globalContainer) {
      globalContainer.innerHTML = ""
      if (standards.Global) {
        Object.entries(standards.Global).forEach(([key, standard]) => {
          this.createStandardCheckbox(globalContainer, key, standard)
        })
      }
    }

    if (nationalContainer) {
      nationalContainer.innerHTML = ""
      if (standards.Nasional) {
        Object.entries(standards.Nasional).forEach(([key, standard]) => {
          this.createStandardCheckbox(nationalContainer, key, standard)
        })
      }
    }
  }

  createStandardCheckbox(container, key, standard) {
    const div = document.createElement("div")
    div.className = "flex items-center space-x-2"
    
    const isAvailable = standard.available || false
    const statusClass = isAvailable ? "text-green-600" : "text-red-600"
    const statusIcon = isAvailable ? "✅" : "❌"
    
    div.innerHTML = `
      <input type="checkbox" id="${key}" value="${key}" class="rounded" ${!isAvailable ? 'disabled' : ''}>
      <label for="${key}" class="text-sm cursor-pointer flex items-center">
        <span class="${statusClass} mr-1">${statusIcon}</span>
        <span>${standard.name || key}</span>
        <span class="text-xs text-gray-500 ml-2">(${standard.description || 'Standard compliance'})</span>
      </label>
    `

    const checkbox = div.querySelector("input")
    if (isAvailable) {
      checkbox.addEventListener("change", (e) => {
        if (e.target.checked) {
          if (!this.selectedStandards.includes(key)) {
            this.selectedStandards.push(key)
          }
        } else {
          this.selectedStandards = this.selectedStandards.filter((s) => s !== key)
        }
        console.log("📋 Selected standards:", this.selectedStandards)
      })
    }

    container.appendChild(div)
  }

  renderStandards(containerId, standards) {
    const container = document.getElementById(containerId)
    if (!container) return

    container.innerHTML = ""

    if (!Array.isArray(standards)) {
      console.warn(`⚠️ Standards for ${containerId} is not an array:`, standards)
      return
    }

    standards.forEach((standard) => {
      this.createStandardCheckbox(container, standard.id, standard)
    })
  }

  showStandardsError(message) {
    const globalContainer = document.getElementById("global-standards")
    const nationalContainer = document.getElementById("national-standards")
    
    const errorHTML = `<div class="text-red-500 text-sm p-2">${message}</div>`
    
    if (globalContainer) globalContainer.innerHTML = errorHTML
    if (nationalContainer) nationalContainer.innerHTML = errorHTML
  }

  handleFileSelect(file) {
    console.log("📁 File selected:", file.name, file.type, file.size)
    
    // Validate file type
    const allowedTypes = [
      "application/pdf",
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      "text/plain",
    ]
    
    if (!allowedTypes.includes(file.type)) {
      alert("❌ Format file tidak didukung. Gunakan PDF, DOCX, atau TXT.")
      return
    }

    // Validate file size (15MB limit)
    const maxSize = 15 * 1024 * 1024
    if (file.size > maxSize) {
      alert("❌ Ukuran file terlalu besar. Maksimal 15MB.")
      return
    }

    this.uploadedFile = file
    this.showFileInfo(file)
    this.uploadFile(file)
  }

  showFileInfo(file) {
    const fileNameEl = document.getElementById("file-name")
    const fileSizeEl = document.getElementById("file-size")
    const fileInfoEl = document.getElementById("file-info")

    if (fileNameEl) fileNameEl.textContent = file.name
    if (fileSizeEl) fileSizeEl.textContent = this.formatFileSize(file.size)
    if (fileInfoEl) fileInfoEl.classList.remove("hidden")

    console.log("📋 File info displayed:", file.name, this.formatFileSize(file.size))
  }

  removeFile() {
    this.uploadedFile = null
    this.sessionId = null
    this.isAnalysisComplete = false
    
    const fileInfoEl = document.getElementById("file-info")
    const fileInput = document.getElementById("file-input")
    const chatSection = document.getElementById("chat-section")
    const resultsSection = document.getElementById("results-section")
    
    if (fileInfoEl) fileInfoEl.classList.add("hidden")
    if (fileInput) fileInput.value = ""
    if (chatSection) chatSection.classList.add("hidden")
    if (resultsSection) resultsSection.classList.add("hidden")
    
    console.log("🗑️ File removed and UI reset")
  }

  async uploadFile(file) {
    const formData = new FormData()
    formData.append("file", file)

    try {
      console.log("📤 Uploading file...")
      const response = await fetch("/api/upload", {
        method: "POST",
        body: formData,
      })

      const result = await response.json()
      console.log("📥 Upload response:", result)

      if (result.success) {
        this.sessionId = result.session_id
        this.uploadedFile.filepath = result.session_id // Store session ID
        console.log("✅ File uploaded successfully. Session ID:", this.sessionId)
        
        // Show success message
        this.showNotification("File berhasil diupload!", "success")
      } else {
        console.error("❌ Upload failed:", result.error)
        alert("❌ Gagal upload file: " + result.error)
      }
    } catch (error) {
      console.error("❌ Upload error:", error)
      alert("❌ Gagal upload file: " + error.message)
    }
  }

  async startAnalysis() {
    console.log("🔍 Starting analysis...")
    console.log("📋 Session ID:", this.sessionId)
    console.log("📋 Selected standards:", this.selectedStandards)

    if (!this.sessionId) {
      alert("❌ Silakan upload dokumen terlebih dahulu")
      return
    }

    if (this.selectedStandards.length === 0) {
      alert("❌ Silakan pilih minimal satu standar compliance")
      return
    }

    // Show progress section
    const progressSection = document.getElementById("progress-section")
    const analyzeBtn = document.getElementById("analyze-btn")
    
    if (progressSection) progressSection.classList.remove("hidden")
    if (analyzeBtn) {
      analyzeBtn.disabled = true
      analyzeBtn.textContent = "Menganalisis..."
    }

    // Start progress simulation
    this.simulateAgentProgress()

    try {
      const response = await fetch("/api/analyze", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          session_id: this.sessionId,
          standards: this.selectedStandards,
        }),
      })

      const result = await response.json()
      console.log("📊 Analysis response:", result)

      if (result.success) {
        this.analysisResult = result
        this.isAnalysisComplete = true
        this.showResults(result)
        this.enableChatSection()
        this.showNotification("Analisis berhasil diselesaikan!", "success")
        console.log("✅ Analysis completed successfully")
      } else {
        console.error("❌ Analysis failed:", result.error)
        alert("❌ Analisis gagal: " + result.error)
        this.showNotification("Analisis gagal: " + result.error, "error")
      }
    } catch (error) {
      console.error("❌ Analysis error:", error)
      alert("❌ Gagal melakukan analisis: " + error.message)
      this.showNotification("Gagal melakukan analisis: " + error.message, "error")
    } finally {
      if (analyzeBtn) {
        analyzeBtn.disabled = false
        analyzeBtn.textContent = "Analyze Document"
      }
      // Keep progress section visible to show completion
    }
  }

  simulateAgentProgress() {
    const agents = [
      { id: 1, name: "Document Collector", duration: 1000 },
      { id: 2, name: "Standard Retriever", duration: 1500 },
      { id: 3, name: "Compliance Checker", duration: 3000 },
      { id: 4, name: "Report Generator", duration: 1500 },
      { id: 5, name: "QA Agent", duration: 1000 },
    ]

    let delay = 0
    agents.forEach((agent, index) => {
      setTimeout(() => {
        this.updateAgentProgress(agent.id, "Memproses...", 30)
        console.log(`🔄 Agent ${agent.name} started`)

        setTimeout(() => {
          this.updateAgentProgress(agent.id, "Selesai", 100)
          console.log(`✅ Agent ${agent.name} completed`)
        }, agent.duration * 0.7)
      }, delay)

      delay += agent.duration * 0.5
    })
  }

  updateAgentProgress(agentId, status, progress) {
    const statusEl = document.getElementById(`agent-${agentId}-status`)
    const progressBar = document.getElementById(`agent-${agentId}-progress`)
    
    if (statusEl) statusEl.textContent = status
    if (progressBar) progressBar.style.width = `${progress}%`
  }

  showResults(result) {
    console.log("📊 Displaying results:", result)
    
    // Show results section
    const resultsSection = document.getElementById("results-section")
    if (resultsSection) resultsSection.classList.remove("hidden")

    // Extract compliance score from different possible locations
    let complianceScore = 0
    if (result.summary && typeof result.summary.compliance_score === 'number') {
      complianceScore = result.summary.compliance_score
    } else if (typeof result.compliance_score === 'number') {
      complianceScore = result.compliance_score
    } else if (result.analysis && typeof result.analysis.compliance_score === 'number') {
      complianceScore = result.analysis.compliance_score
    }

    console.log("📊 Extracted compliance score:", complianceScore)

    // Update compliance score display
    const scoreEl = document.getElementById("compliance-score")
    if (scoreEl) scoreEl.textContent = `${complianceScore.toFixed(1)}%`

    // Update circular progress
    this.updateCircularProgress(complianceScore)

    // Show compliance status with color coding
    this.updateComplianceStatus(complianceScore)

    // Extract and display issues
    const issues = result.issues || result.summary?.issues || result.analysis?.issues || []
    console.log("📋 Extracted issues:", issues)
    this.renderIssues(issues)

    // Extract and display compliant items
    const compliantItems = result.compliant_items || result.summary?.compliant_items || result.analysis?.compliant_items || []
    console.log("📋 Extracted compliant items:", compliantItems)
    this.renderCompliantItems(compliantItems)

    // Show download buttons
    this.showDownloadButtons()
  }

  updateCircularProgress(score) {
    const circle = document.getElementById("compliance-circle")
    if (circle) {
      const radius = 15.9155
      const circumference = 2 * Math.PI * radius
      const offset = circumference - (score / 100) * circumference
      
      circle.style.strokeDasharray = `${circumference}, ${circumference}`
      circle.style.strokeDashoffset = offset

      // Update color based on score
      if (score >= 80) {
        circle.style.stroke = "#10B981" // Green
      } else if (score >= 60) {
        circle.style.stroke = "#F59E0B" // Yellow
      } else if (score >= 40) {
        circle.style.stroke = "#EF4444" // Red
      } else {
        circle.style.stroke = "#DC2626" // Dark Red
      }
    }
  }

  updateComplianceStatus(score) {
    const statusEl = document.getElementById("compliance-status")
    if (statusEl) {
      let status = ""
      let className = ""
      
      if (score >= 80) {
        status = "🌟 Excellent - Compliance Tinggi"
        className = "text-green-600 font-semibold"
      } else if (score >= 60) {
        status = "✅ Good - Perlu Minor Improvements"
        className = "text-yellow-600 font-semibold"
      } else if (score >= 40) {
        status = "⚠️ Moderate - Perlu Perbaikan Substansial"
        className = "text-orange-600 font-semibold"
      } else {
        status = "🚨 Critical - Perlu Revisi Menyeluruh"
        className = "text-red-600 font-semibold"
      }
      
      statusEl.textContent = status
      statusEl.className = className
    }
  }

  renderIssues(issues) {
    const container = document.getElementById("issues-list")
    if (!container) return

    container.innerHTML = ""

    if (!Array.isArray(issues) || issues.length === 0) {
      container.innerHTML = `
        <div class="text-green-600 p-3 text-center">
          ✅ Tidak ada isu compliance yang ditemukan
        </div>
      `
      return
    }

    console.log("🔍 Rendering", issues.length, "issues")

    issues.forEach((issue, index) => {
      const div = document.createElement("div")
      
      // Determine severity color
      const severity = issue.severity || 'MEDIUM'
      let colorClass = ""
      let severityIcon = ""
      
      switch (severity.toUpperCase()) {
        case 'HIGH':
        case 'CRITICAL':
          colorClass = "border-red-500 bg-red-50"
          severityIcon = "🚨"
          break
        case 'MEDIUM':
          colorClass = "border-yellow-500 bg-yellow-50"
          severityIcon = "⚠️"
          break
        case 'LOW':
          colorClass = "border-blue-500 bg-blue-50"
          severityIcon = "ℹ️"
          break
        default:
          colorClass = "border-gray-500 bg-gray-50"
          severityIcon = "📋"
      }

      div.className = `border-l-4 ${colorClass} p-3 rounded mb-3`
      div.innerHTML = `
        <div class="flex items-start justify-between mb-2">
          <h4 class="font-medium text-gray-800 flex items-center">
            <span class="mr-2">${severityIcon}</span>
            ${issue.aspect || issue.title || `Issue ${index + 1}`}
          </h4>
          <span class="text-xs px-2 py-1 rounded ${severity.toUpperCase() === 'HIGH' ? 'bg-red-200 text-red-800' : 
            severity.toUpperCase() === 'MEDIUM' ? 'bg-yellow-200 text-yellow-800' : 'bg-blue-200 text-blue-800'}">
            ${severity.toUpperCase()}
          </span>
        </div>
        <p class="text-sm text-gray-600 mb-2">${issue.explanation || issue.description || 'No description available'}</p>
        ${issue.recommendations && Array.isArray(issue.recommendations) ? `
          <div class="text-xs text-gray-500 mt-2">
            <strong>Rekomendasi:</strong>
            <ul class="list-disc list-inside mt-1">
              ${issue.recommendations.slice(0, 2).map(rec => `<li>${rec}</li>`).join('')}
            </ul>
          </div>
        ` : ''}
        ${issue.reference ? `<p class="text-xs text-gray-400 mt-2">Referensi: ${issue.reference}</p>` : ''}
      `
      container.appendChild(div)
    })
  }

  renderCompliantItems(items) {
    const container = document.getElementById("compliant-list")
    if (!container) return

    container.innerHTML = ""

    if (!Array.isArray(items) || items.length === 0) {
      container.innerHTML = `
        <div class="text-gray-500 p-3 text-center">
          📝 Tidak ada item compliant yang ditemukan
        </div>
      `
      return
    }

    console.log("✅ Rendering", items.length, "compliant items")

    items.forEach((item, index) => {
      const div = document.createElement("div")
      div.className = "border-l-4 border-green-500 bg-green-50 p-3 rounded mb-3"
      div.innerHTML = `
        <h4 class="font-medium text-green-800 flex items-center">
          <span class="mr-2">✅</span>
          ${item.aspect || item.title || `Compliant Item ${index + 1}`}
        </h4>
        <p class="text-sm text-green-600 mt-1">${item.explanation || item.description || 'Item ini sudah sesuai dengan standar compliance'}</p>
        ${item.reference ? `<p class="text-xs text-green-500 mt-2">Referensi: ${item.reference}</p>` : ''}
      `
      container.appendChild(div)
    })
  }

  showDownloadButtons() {
    const downloadSection = document.getElementById("download-section")
    if (downloadSection) {
      downloadSection.classList.remove("hidden")
    }
  }

  enableChatSection() {
    const chatSection = document.getElementById("chat-section")
    if (chatSection) {
      chatSection.classList.remove("hidden")
      this.addInitialChatMessage()
      console.log("💬 Chat section enabled")
    }
  }

  addInitialChatMessage() {
    const welcomeMessage = `
🤖 **Halo! Saya ReguBot QA Assistant**

Analisis compliance dokumen Anda telah selesai! Sekarang saya siap menjawab pertanyaan Anda tentang:

📊 **Hasil Analisis:**
• Penjelasan skor compliance
• Detail tentang isu yang ditemukan
• Area yang perlu diperbaiki

🔧 **Rekomendasi Perbaikan:**
• Saran spesifik untuk meningkatkan compliance
• Template klausul yang diperlukan
• Langkah implementasi

📋 **Contoh Pertanyaan:**
• "Bagaimana cara meningkatkan skor compliance saya?"
• "Apa saja isu critical yang harus segera diperbaiki?"
• "Berikan contoh klausul untuk GDPR Article 25"
• "Bagaimana implementasi data retention policy?"

Silakan tanyakan apa saja tentang hasil analisis atau perbaikan dokumen Anda! 🚀
    `
    
    this.addChatMessage(welcomeMessage, "bot")
  }

  async sendChatMessage() {
    const input = document.getElementById("chat-input")
    if (!input) return

    const question = input.value.trim()
    if (!question) {
      alert("❌ Silakan masukkan pertanyaan terlebih dahulu")
      return
    }

    if (!this.sessionId) {
      alert("❌ Session tidak valid. Silakan lakukan analisis ulang.")
      return
    }

    if (!this.isAnalysisComplete) {
      alert("❌ Silakan selesaikan analisis terlebih dahulu")
      return
    }

    console.log("💬 Sending chat message:", question)

    // Add user message to chat
    this.addChatMessage(question, "user")
    input.value = ""

    // Show typing indicator
    const typingId = this.addTypingIndicator()

    let result = null;
    let botResponse = "";
    let errorMsg = "";
    let response = null;
    try {
      response = await fetch("/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          session_id: this.sessionId,
          question: question,
        }),
      });

      if (!response.ok) {
        errorMsg = `HTTP ${response.status}: ${response.statusText}`;
        throw new Error(errorMsg);
      }

  result = await response.json();
  console.log("💬 FULL Chat response object:", JSON.stringify(result));
  console.log("🟢 result.response:", result?.response);
  console.log("🟡 result.answer:", result?.answer);

      if (result.success) {
        // Prefer the longest valid string from response or answer
        let candidates = [];
        if (typeof result.response === "string" && result.response.trim() !== "") {
          candidates.push(result.response.trim());
        }
        if (typeof result.answer === "string" && result.answer.trim() !== "") {
          candidates.push(result.answer.trim());
        }
        // If both exist, pick the longer one
        if (candidates.length > 0) {
          botResponse = candidates.reduce((a, b) => (b.length > a.length ? b : a), "");
        } else {
          // Try any other string field
          for (const key in result) {
            if (typeof result[key] === "string" && result[key].trim() !== "") {
              botResponse = result[key].trim();
              break;
            }
          }
        }
        // Final fallback: hardcoded message
        if (!botResponse || typeof botResponse !== "string" || botResponse.trim() === "") {
          botResponse = "🤖 Jawaban tidak tersedia. Silakan cek hasil analisis atau coba pertanyaan lain.";
        }
        if (botResponse.length > 2000) {
          botResponse = botResponse.slice(0, 2000) + "...\n(Jawaban dipotong, lihat detail di laporan atau download report)";
        }
        try {
          console.log("🟣 Final botResponse to render:", botResponse);
          this.addChatMessage(botResponse, "bot");
          console.log("✅ Chat message processed successfully");
        } catch (e) {
          this.addChatMessage("❌ Error menampilkan jawaban bot: " + (e.message || e), "bot");
          console.error("❌ Error rendering bot message:", e);
        }
      } else {
        errorMsg = result.error || "Terjadi kesalahan dalam memproses pertanyaan";
        this.addChatMessage(`❌ **Error**: ${errorMsg}`, "bot");
        console.error("❌ Chat error:", result);
      }
    } catch (error) {
      errorMsg = errorMsg || (error && error.message) || "Terjadi kesalahan teknis";
      this.addChatMessage(
        "❌ **Maaf, terjadi kesalahan teknis.** Silakan coba lagi atau lakukan analisis ulang jika masalah berlanjut.\n" + errorMsg,
        "bot"
      );
      console.error("❌ Chat request error:", error);
    } finally {
      this.removeTypingIndicator(typingId);
    }
  }

  addTypingIndicator() {
    const container = document.getElementById("chat-messages")
    const typingId = 'typing-' + Date.now()
    const div = document.createElement("div")
    div.id = typingId
    div.className = "flex items-start space-x-3 mb-4"
    div.innerHTML = `
      <div class="w-8 h-8 bg-purple-600 rounded-full flex items-center justify-center">
        <i class="fas fa-robot text-white text-sm"></i>
      </div>
      <div class="bg-gray-100 rounded-lg p-3">
        <div class="flex space-x-1">
          <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
          <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
          <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
        </div>
      </div>
    `
    
    if (container) {
      container.appendChild(div)
      container.scrollTop = container.scrollHeight
    }
    
    return typingId
  }

  removeTypingIndicator(typingId) {
    const typingElement = document.getElementById(typingId)
    if (typingElement) {
      typingElement.remove()
    }
  }

  addChatMessage(message, sender) {
    const container = document.getElementById("chat-messages")
    if (!container) return

    const div = document.createElement("div")
    div.className = "mb-4"

    if (sender === "user") {
      div.className += " flex items-start space-x-3 justify-end"
      div.innerHTML = `
        <div class="bg-blue-600 text-white rounded-lg p-3 max-w-md lg:max-w-lg">
          <p class="text-sm whitespace-pre-wrap">${this.escapeHtml(message)}</p>
        </div>
        <div class="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center flex-shrink-0">
          <i class="fas fa-user text-white text-sm"></i>
        </div>
      `
    } else {
      div.className += " flex items-start space-x-3"
      div.innerHTML = `
        <div class="w-8 h-8 bg-purple-600 rounded-full flex items-center justify-center flex-shrink-0">
          <i class="fas fa-robot text-white text-sm"></i>
        </div>
        <div class="bg-gray-100 rounded-lg p-3 max-w-md lg:max-w-2xl">
          <div class="text-sm whitespace-pre-wrap prose prose-sm max-w-none">${this.formatBotMessage(message)}</div>
        </div>
      `
    }

    container.appendChild(div)
    container.scrollTop = container.scrollHeight
  }

  formatBotMessage(message) {
    // Convert markdown-like formatting to HTML
    try {
      let formatted = this.escapeHtml(message)
      // Convert **bold** to <strong>
      formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      // Convert bullet points
      formatted = formatted.replace(/^• /gm, '• ')
      // Convert numbered lists
      formatted = formatted.replace(/^(\d+)\. /gm, '$1. ')
      // Convert line breaks
      formatted = formatted.replace(/\n/g, '<br>')
      // Convert emojis and special characters (keep as is)
      return formatted
    } catch (err) {
      console.error("❌ Error formatting bot message:", err, message);
      return typeof message === "string" ? message : JSON.stringify(message);
    }
  }

  escapeHtml(text) {
    const div = document.createElement('div')
    div.textContent = text
    return div.innerHTML
  }

  async downloadReport(format) {
    if (!this.sessionId) {
      alert("❌ Session tidak valid. Silakan lakukan analisis ulang.")
      return
    }

    try {
      console.log(`📥 Downloading ${format} report for session:`, this.sessionId)
      
      const response = await fetch(`/api/download/${this.sessionId}/${format}`)
      
      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.error || `HTTP ${response.status}`)
      }

      // Get filename from response headers or create default
      const contentDisposition = response.headers.get('Content-Disposition')
      let filename = `compliance_report_${this.sessionId}.${format}`
      
      if (contentDisposition) {
        const matches = contentDisposition.match(/filename="?([^";]+)"?/)
        if (matches && matches[1]) {
          filename = matches[1]
        }
      }

      // Download file
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = filename
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)

      this.showNotification(`Report ${format.toUpperCase()} berhasil didownload!`, "success")
      console.log(`✅ ${format} report downloaded successfully`)
    } catch (error) {
      console.error(`❌ Download ${format} error:`, error)
      alert(`❌ Gagal download report ${format.toUpperCase()}: ${error.message}`)
    }
  }

  showNotification(message, type = "info") {
    // Create notification element
    const notification = document.createElement('div')
    notification.className = `fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg transition-all duration-300 transform translate-x-full`
    
    const colors = {
      success: 'bg-green-500 text-white',
      error: 'bg-red-500 text-white',
      warning: 'bg-yellow-500 text-black',
      info: 'bg-blue-500 text-white'
    }
    
    notification.className += ` ${colors[type] || colors.info}`
    notification.innerHTML = `
      <div class="flex items-center justify-between">
        <span class="text-sm font-medium">${message}</span>
        <button class="ml-4 text-current opacity-70 hover:opacity-100" onclick="this.parentElement.parentElement.remove()">
          <i class="fas fa-times"></i>
        </button>
      </div>
    `
    
    document.body.appendChild(notification)
    
    // Animate in
    setTimeout(() => {
      notification.classList.remove('translate-x-full')
    }, 100)
    
    // Auto remove after 5 seconds
    setTimeout(() => {
      if (document.body.contains(notification)) {
        notification.classList.add('translate-x-full')
        setTimeout(() => {
          if (document.body.contains(notification)) {
            notification.remove()
          }
        }, 300)
      }
    }, 5000)
  }

  formatFileSize(bytes) {
    if (bytes === 0) return "0 Bytes"
    const k = 1024
    const sizes = ["Bytes", "KB", "MB", "GB"]
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Number.parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i]
  }

  // Debug helper methods
  getDebugInfo() {
    return {
      sessionId: this.sessionId,
      hasUploadedFile: !!this.uploadedFile,
      selectedStandards: this.selectedStandards,
      isAnalysisComplete: this.isAnalysisComplete,
      hasAnalysisResult: !!this.analysisResult
    }
  }

  logDebugInfo() {
    console.log("🔍 ReguBot Debug Info:", this.getDebugInfo())
  }
}

// Initialize ReguBot when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
  console.log("🚀 DOM loaded, initializing ReguBot...")
  window.reguBot = new ReguBot()
  
  // Add global debug helper
  window.debugReguBot = () => {
    if (window.reguBot) {
      window.reguBot.logDebugInfo()
    } else {
      console.log("❌ ReguBot not initialized")
    }
  }
  
  console.log("✅ ReguBot initialized successfully")
  console.log("💡 Use debugReguBot() in console for debug info")
})