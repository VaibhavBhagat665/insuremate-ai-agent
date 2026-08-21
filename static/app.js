/**
 * InsureMate AI — Frontend Application
 * Handles file upload, question management, API calls, and results display
 */

(function () {
    'use strict';

    // ── State ──────────────────────────────────────────
    const state = {
        file: null,
        questions: [],
        isProcessing: false,
    };

    // ── DOM References ─────────────────────────────────
    const $ = (sel) => document.querySelector(sel);
    const $$ = (sel) => document.querySelectorAll(sel);

    const els = {
        // Upload
        uploadZone: $('#uploadZone'),
        fileInput: $('#fileInput'),
        uploadContent: $('#uploadContent'),
        uploadSuccess: $('#uploadSuccess'),
        fileName: $('#fileName'),
        fileSize: $('#fileSize'),
        fileIcon: $('#fileIcon'),
        fileRemove: $('#fileRemove'),

        // Questions
        questionInput: $('#questionInput'),
        addQuestionBtn: $('#addQuestionBtn'),
        questionsList: $('#questionsList'),
        questionsFooter: $('#questionsFooter'),
        questionCount: $('#questionCount'),
        clearAllBtn: $('#clearAllBtn'),

        // Submit
        submitBtn: $('#submitBtn'),
        submitSection: $('#submitSection'),

        // Processing
        processingSection: $('#processingSection'),
        processingTitle: $('#processingTitle'),
        processingSubtitle: $('#processingSubtitle'),
        progressBar: $('#progressBar'),

        // Results
        resultsSection: $('#resultsSection'),
        resultsList: $('#resultsList'),
        resultsMeta: $('#resultsMeta'),
        newQueryBtn: $('#newQueryBtn'),

        // Sections
        workspace: $('#workspace'),
        hero: $('#hero'),
        navStatus: $('#navStatus'),
    };

    // ── File Upload ────────────────────────────────────

    // Click to browse
    els.uploadZone.addEventListener('click', (e) => {
        if (e.target.closest('.file-remove')) return;
        els.fileInput.click();
    });

    // File input change
    els.fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFile(e.target.files[0]);
        }
    });

    // Drag and drop
    els.uploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        els.uploadZone.classList.add('drag-over');
    });

    els.uploadZone.addEventListener('dragleave', (e) => {
        e.preventDefault();
        els.uploadZone.classList.remove('drag-over');
    });

    els.uploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        els.uploadZone.classList.remove('drag-over');
        if (e.dataTransfer.files.length > 0) {
            handleFile(e.dataTransfer.files[0]);
        }
    });

    // Remove file
    els.fileRemove.addEventListener('click', (e) => {
        e.stopPropagation();
        removeFile();
    });

    function handleFile(file) {
        const allowedTypes = ['.pdf', '.docx', '.txt'];
        const ext = '.' + file.name.split('.').pop().toLowerCase();

        if (!allowedTypes.includes(ext)) {
            showToast('Unsupported file type. Please upload PDF, DOCX, or TXT files.', 'error');
            return;
        }

        if (file.size > 500 * 1024 * 1024) {
            showToast('File is too large. Maximum size is 500MB.', 'error');
            return;
        }

        state.file = file;

        // Update UI
        els.uploadContent.style.display = 'none';
        els.uploadSuccess.style.display = 'block';
        els.fileName.textContent = file.name;
        els.fileSize.textContent = formatFileSize(file.size);

        // Set file icon
        const iconMap = { '.pdf': '📕', '.docx': '📘', '.txt': '📄' };
        els.fileIcon.textContent = iconMap[ext] || '📄';

        updateSubmitState();
    }

    function removeFile() {
        state.file = null;
        els.fileInput.value = '';
        els.uploadContent.style.display = '';
        els.uploadSuccess.style.display = 'none';
        updateSubmitState();
    }

    // ── Questions ──────────────────────────────────────

    els.addQuestionBtn.addEventListener('click', addQuestion);

    els.questionInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            addQuestion();
        }
    });

    els.clearAllBtn.addEventListener('click', () => {
        state.questions = [];
        renderQuestions();
        updateSubmitState();
    });

    function addQuestion() {
        const text = els.questionInput.value.trim();
        if (!text) return;
        if (state.questions.length >= 20) {
            showToast('Maximum 20 questions allowed', 'error');
            return;
        }
        if (state.questions.includes(text)) {
            showToast('This question has already been added', 'error');
            return;
        }

        state.questions.push(text);
        els.questionInput.value = '';
        els.questionInput.focus();
        renderQuestions();
        updateSubmitState();
    }

    function removeQuestion(index) {
        state.questions.splice(index, 1);
        renderQuestions();
        updateSubmitState();
    }

    function renderQuestions() {
        els.questionsList.innerHTML = '';

        state.questions.forEach((q, i) => {
            const chip = document.createElement('div');
            chip.className = 'question-chip';
            chip.style.animationDelay = `${i * 0.05}s`;
            chip.innerHTML = `
                <span class="chip-number">${i + 1}</span>
                <span class="chip-text">${escapeHtml(q)}</span>
                <button class="chip-remove" data-index="${i}" title="Remove question">
                    <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                        <path d="M3 3L11 11M11 3L3 11" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                    </svg>
                </button>
            `;
            els.questionsList.appendChild(chip);
        });

        // Show/hide footer
        els.questionsFooter.style.display = state.questions.length > 0 ? 'flex' : 'none';
        els.questionCount.textContent = `${state.questions.length}/20 questions`;

        // Attach remove handlers
        els.questionsList.querySelectorAll('.chip-remove').forEach((btn) => {
            btn.addEventListener('click', () => {
                removeQuestion(parseInt(btn.dataset.index));
            });
        });
    }

    // ── Submit ─────────────────────────────────────────

    function updateSubmitState() {
        els.submitBtn.disabled = !state.file || state.questions.length === 0 || state.isProcessing;
    }

    els.submitBtn.addEventListener('click', submitQuery);

    async function submitQuery() {
        if (state.isProcessing || !state.file || state.questions.length === 0) return;

        state.isProcessing = true;
        updateSubmitState();

        // Hide workspace, show processing
        els.workspace.style.display = 'none';
        els.submitSection.style.display = 'none';
        els.hero.style.display = 'none';
        els.resultsSection.style.display = 'none';
        els.processingSection.style.display = 'block';

        // Scroll to processing
        els.processingSection.scrollIntoView({ behavior: 'smooth', block: 'start' });

        // Animate progress
        animateProcessing();

        try {
            const formData = new FormData();
            formData.append('file', state.file);
            formData.append('questions', JSON.stringify(state.questions));

            const response = await fetch('/api/v1/upload-and-query', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `Server error: ${response.status}`);
            }

            const data = await response.json();
            showResults(data);
        } catch (err) {
            console.error('Query failed:', err);
            showToast(err.message || 'Something went wrong. Please try again.', 'error');
            resetToWorkspace();
        } finally {
            state.isProcessing = false;
            updateSubmitState();
        }
    }

    // ── Processing Animation ───────────────────────────

    function animateProcessing() {
        const steps = ['step1', 'step2', 'step3', 'step4'];
        const titles = [
            'Parsing your document...',
            'Building semantic embeddings...',
            'Processing questions in parallel...',
            'Generating AI-powered answers...',
        ];
        const subtitles = [
            'Extracting text and detecting structure',
            'Creating vector representations for search',
            'Running hybrid semantic + keyword search',
            'Using RAG pipeline with LLM provider',
        ];

        let currentStep = 0;
        let progress = 5;

        // Initial state
        els.progressBar.style.width = '5%';
        els.processingTitle.textContent = titles[0];
        els.processingSubtitle.textContent = subtitles[0];

        const interval = setInterval(() => {
            if (!state.isProcessing) {
                clearInterval(interval);
                return;
            }

            progress = Math.min(progress + Math.random() * 8 + 2, 95);
            els.progressBar.style.width = progress + '%';

            const newStep = Math.min(Math.floor(progress / 25), 3);
            if (newStep !== currentStep) {
                // Mark previous as done
                const prevEl = document.getElementById(steps[currentStep]);
                if (prevEl) {
                    prevEl.classList.remove('active');
                    prevEl.classList.add('done');
                }

                currentStep = newStep;

                // Mark current as active
                const curEl = document.getElementById(steps[currentStep]);
                if (curEl) curEl.classList.add('active');

                els.processingTitle.textContent = titles[currentStep];
                els.processingSubtitle.textContent = subtitles[currentStep];
            }
        }, 600);
    }

    // ── Results Display ────────────────────────────────

    function showResults(data) {
        // Complete progress
        els.progressBar.style.width = '100%';

        // Mark all steps done
        ['step1', 'step2', 'step3', 'step4'].forEach((id) => {
            const el = document.getElementById(id);
            if (el) {
                el.classList.remove('active');
                el.classList.add('done');
            }
        });

        setTimeout(() => {
            els.processingSection.style.display = 'none';
            els.resultsSection.style.display = 'block';
            els.resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });

            // Metadata
            const meta = data.metadata || {};
            const answerCount = data.answers ? data.answers.length : 0;
            const procTime = meta.processing_time ? meta.processing_time + 's' : '';
            const filename = meta.filename || (state.file ? state.file.name : 'document');
            els.resultsMeta.textContent = [
                `${answerCount} answer${answerCount !== 1 ? 's' : ''}`,
                procTime,
                filename,
            ]
                .filter(Boolean)
                .join(' · ');

            // Render answer cards
            els.resultsList.innerHTML = '';

            if (data.answers && data.answers.length > 0) {
                data.answers.forEach((answer, i) => {
                    const question = state.questions[i] || `Question ${i + 1}`;
                    const card = createAnswerCard(i + 1, question, answer);
                    card.style.animationDelay = `${i * 0.1}s`;
                    els.resultsList.appendChild(card);
                });
            }
        }, 800);
    }

    function createAnswerCard(num, question, answer) {
        const card = document.createElement('div');
        card.className = 'answer-card';
        card.innerHTML = `
            <div class="answer-question">
                <span class="answer-q-badge">Q${num}</span>
                <span class="answer-q-text">${escapeHtml(question)}</span>
            </div>
            <div class="answer-body">
                <span class="answer-a-badge">A</span>
                <div class="answer-text">${formatAnswer(answer)}</div>
            </div>
            <div class="answer-actions">
                <button class="copy-btn" data-text="${escapeAttr(answer)}">
                    <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                        <rect x="4" y="4" width="8" height="8" rx="1.5" stroke="currentColor" stroke-width="1.2"/>
                        <path d="M10 4V2.5C10 1.67 9.33 1 8.5 1H2.5C1.67 1 1 1.67 1 2.5V8.5C1 9.33 1.67 10 2.5 10H4" stroke="currentColor" stroke-width="1.2"/>
                    </svg>
                    Copy
                </button>
            </div>
        `;

        // Copy handler
        const copyBtn = card.querySelector('.copy-btn');
        copyBtn.addEventListener('click', () => {
            navigator.clipboard.writeText(answer).then(() => {
                copyBtn.innerHTML = `
                    <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                        <path d="M2 7L5.5 10.5L12 3.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                    Copied!
                `;
                copyBtn.classList.add('copied');
                setTimeout(() => {
                    copyBtn.innerHTML = `
                        <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                            <rect x="4" y="4" width="8" height="8" rx="1.5" stroke="currentColor" stroke-width="1.2"/>
                            <path d="M10 4V2.5C10 1.67 9.33 1 8.5 1H2.5C1.67 1 1 1.67 1 2.5V8.5C1 9.33 1.67 10 2.5 10H4" stroke="currentColor" stroke-width="1.2"/>
                        </svg>
                        Copy
                    `;
                    copyBtn.classList.remove('copied');
                }, 2000);
            });
        });

        return card;
    }

    // ── Reset / New Query ──────────────────────────────

    els.newQueryBtn.addEventListener('click', () => {
        resetToWorkspace();
    });

    function resetToWorkspace() {
        els.processingSection.style.display = 'none';
        els.resultsSection.style.display = 'none';
        els.hero.style.display = '';
        els.workspace.style.display = '';
        els.submitSection.style.display = '';

        // Reset processing steps
        ['step1', 'step2', 'step3', 'step4'].forEach((id) => {
            const el = document.getElementById(id);
            if (el) {
                el.classList.remove('active', 'done');
            }
        });
        const step1 = document.getElementById('step1');
        if (step1) step1.classList.add('active');
        els.progressBar.style.width = '0%';

        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    // ── Utilities ──────────────────────────────────────

    function formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    function escapeAttr(text) {
        return text.replace(/"/g, '&quot;').replace(/'/g, '&#39;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    }

    function formatAnswer(text) {
        // Basic formatting: convert newlines to <br>, bold **text**, etc.
        let formatted = escapeHtml(text);
        formatted = formatted.replace(/\n/g, '<br>');
        formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        return formatted;
    }

    // Toast notification
    function showToast(message, type = 'info') {
        const existing = document.querySelector('.toast');
        if (existing) existing.remove();

        const toast = document.createElement('div');
        toast.className = 'toast';
        toast.style.cssText = `
            position: fixed;
            bottom: 2rem;
            left: 50%;
            transform: translateX(-50%) translateY(20px);
            padding: 0.85rem 1.5rem;
            background: ${type === 'error' ? 'rgba(239, 68, 68, 0.9)' : 'rgba(168, 85, 247, 0.9)'};
            color: white;
            border-radius: 12px;
            font-size: 0.88rem;
            font-family: var(--font-body);
            backdrop-filter: blur(12px);
            z-index: 1000;
            opacity: 0;
            transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
            max-width: 90vw;
            text-align: center;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        `;
        toast.textContent = message;
        document.body.appendChild(toast);

        requestAnimationFrame(() => {
            toast.style.opacity = '1';
            toast.style.transform = 'translateX(-50%) translateY(0)';
        });

        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(-50%) translateY(20px)';
            setTimeout(() => toast.remove(), 300);
        }, 4000);
    }

    // ── Init ───────────────────────────────────────────
    console.log('%c🚀 InsureMate AI — Ready', 'color: #a855f7; font-size: 14px; font-weight: bold;');
})();
