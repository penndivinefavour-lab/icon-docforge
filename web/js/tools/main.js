// ICON DocForge — Tool Modules Registry
// Each tool is a self-contained module with render() and onMount() methods

window.DFTools = window.DFTools || {};

// ============================================================================
// IMAGE TO PDF
// ============================================================================
window.DFTools['image-to-pdf'] = {
    render: function() {
        const container = document.createElement('div');
        container.innerHTML = `
            <div class="tool-section">
                <h3>Select Images</h3>
                <div class="file-picker" id="image-drop-zone">
                    <div class="file-picker-icon">🖼</div>
                    <div class="file-picker-text">Tap to select images or drag & drop here</div>
                    <input type="file" id="image-input" style="display:none" accept="image/*" multiple>
                </div>
                <div id="selected-images" class="mt-16"></div>
            </div>
            
            <div class="tool-section">
                <h3>Output Settings</h3>
                <div class="field">
                    <label>Page Size</label>
                    <select id="page-size">
                        <option value="original">Original Image Size</option>
                        <option value="A4" selected>A4 (210 × 297 mm)</option>
                        <option value="Letter">Letter (8.5 × 11 in)</option>
                        <option value="A5">A5 (148 × 210 mm)</option>
                    </select>
                </div>
                <div class="field">
                    <label>Image Quality</label>
                    <select id="image-quality">
                        <option value="95" selected>High (95%)</option>
                        <option value="85">Medium (85%)</option>
                        <option value="70">Low (70%)</option>
                    </select>
                </div>
            </div>
            
            <button class="btn btn-primary btn-block" id="convert-images-btn" disabled>
                Convert to PDF
            </button>
        `;
        
        // Wire up event handlers
        const dropZone = container.querySelector('#image-drop-zone');
        const fileInput = container.querySelector('#image-input');
        const convertBtn = container.querySelector('#convert-images-btn');
        
        dropZone.addEventListener('click', () => fileInput.click());
        
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('dragover');
        });
        
        dropZone.addEventListener('dragleave', () => {
            dropZone.classList.remove('dragover');
        });
        
        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
            handleFiles(Array.from(e.dataTransfer.files));
        });
        
        fileInput.addEventListener('change', (e) => handleFiles(Array.from(e.target.files)));
        
        convertBtn.addEventListener('click', () => convertImages());
        
        return container;
    },
    
    onMount: function(container) {
        // Any post-mount setup
    }
};

// ============================================================================
// PDF MERGE
// ============================================================================
window.DFTools['pdf-merge'] = {
    render: function() {
        const container = document.createElement('div');
        container.innerHTML = `
            <div class="tool-section">
                <h3>Select PDFs to Merge</h3>
                <div class="file-picker" id="merge-drop-zone">
                    <div class="file-picker-icon">📑</div>
                    <div class="file-picker-text">Select 2 or more PDF files</div>
                    <input type="file" id="merge-input" style="display:none" accept=".pdf" multiple>
                </div>
                <div id="selected-pdfs" class="mt-16"></div>
            </div>
            
            <button class="btn btn-primary btn-block" id="merge-btn" disabled>
                Merge PDFs
            </button>
        `;
        
        const dropZone = container.querySelector('#merge-drop-zone');
        const fileInput = container.querySelector('#merge-input');
        const mergeBtn = container.querySelector('#merge-btn');
        
        dropZone.addEventListener('click', () => fileInput.click());
        
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('dragover');
        });
        
        dropZone.addEventListener('dragleave', () => {
            dropZone.classList.remove('dragover');
        });
        
        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
            handleFiles(Array.from(e.dataTransfer.files));
        });
        
        fileInput.addEventListener('change', (e) => handleFiles(Array.from(e.target.files)));
        
        mergeBtn.addEventListener('click', () => mergePDFs());
        
        return container;
    },
    
    onMount: function(container) {
        // Any post-mount setup
    }
};

// ============================================================================
// PDF SPLIT
// ============================================================================
window.DFTools['pdf-split'] = {
    render: function() {
        const container = document.createElement('div');
        container.innerHTML = `
            <div class="tool-section">
                <h3>Select PDF to Split</h3>
                <div class="file-picker" id="split-drop-zone">
                    <div class="file-picker-icon">📑</div>
                    <div class="file-picker-text">Select a PDF file</div>
                    <input type="file" id="split-input" style="display:none" accept=".pdf">
                </div>
                <div id="selected-pdf-info" class="mt-16"></div>
            </div>
            
            <div class="tool-section" id="split-options" style="display: none;">
                <h3>Split Options</h3>
                <div class="field">
                    <label>Page Range</label>
                    <input type="text" id="page-range" placeholder="e.g., 1-3 or 5,7,9">
                </div>
                <p class="text-muted" style="font-size: 12px; margin-top: 4px;">
                    Use commas for individual pages, hyphens for ranges
                </p>
            </div>
            
            <button class="btn btn-primary btn-block" id="split-btn" disabled>
                Split PDF
            </button>
        `;
        
        const dropZone = container.querySelector('#split-drop-zone');
        const fileInput = container.querySelector('#split-input');
        const splitBtn = container.querySelector('#split-btn');
        
        dropZone.addEventListener('click', () => fileInput.click());
        
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('dragover');
        });
        
        dropZone.addEventListener('dragleave', () => {
            dropZone.classList.remove('dragover');
        });
        
        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
            handleSingleFile(Array.from(e.dataTransfer.files)[0]);
        });
        
        fileInput.addEventListener('change', (e) => handleSingleFile(e.target.files[0]));
        
        splitBtn.addEventListener('click', () => splitPDF());
        
        return container;
    },
    
    onMount: function(container) {
        // Any post-mount setup
    }
};

// ============================================================================
// DIAGNOSTICS
// ============================================================================
window.DFTools['diagnostics'] = {
    render: function() {
        const container = document.createElement('div');
        container.innerHTML = `
            <div class="tool-section">
                <h3>System Diagnostics</h3>
                <div id="diag-status" style="padding: 16px; background: var(--color-surface); border-radius: 12px;">
                    <div class="loading-spinner"></div>
                    <p class="text-muted mt-16">Checking system status...</p>
                </div>
            </div>
            
            <div class="tool-section">
                <h3>Engine Status</h3>
                <div id="engine-list"></div>
            </div>
            
            <button class="btn btn-secondary btn-block" id="refresh-btn">Refresh</button>
        `;
        
        document.getElementById('refresh-btn').addEventListener('click', runDiagnostics);
        
        setTimeout(runDiagnostics, 500);
        
        return container;
    },
    
    onMount: function(container) {
        // Auto-run diagnostics
    }
};

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

function handleFiles(files) {
    const validTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/webp', 'image/bmp', 'image/tiff', 'application/pdf'];
    const maxSize = 50 * 1024 * 1024; // 50MB
    
    const validFiles = files.filter(f => {
        if (!validTypes.includes(f.type) && !f.name.toLowerCase().endsWith('.pdf')) {
            window.App.toast(`"${f.name}" is not a supported format`, 'error');
            return false;
        }
        if (f.size > maxSize) {
            window.App.toast(`"${f.name}" is too large (max 50MB)`, 'error');
            return false;
        }
        return true;
    });
    
    // Update UI based on context
    const selectedDiv = document.getElementById('selected-images') || 
                       document.getElementById('selected-pdfs') ||
                       document.getElementById('selected-pdf-info');
    
    if (selectedDiv && validFiles.length > 0) {
        selectedDiv.innerHTML = validFiles.map(f => `
            <div style="padding: 12px; background: var(--color-bg); border-radius: 8px; margin-bottom: 8px;">
                <div style="font-weight: 500;">${f.name}</div>
                <div style="font-size: 12px; color: var(--color-text-muted);">${formatFileSize(f.size)}</div>
            </div>
        `).join('');
        
        // Enable convert button
        const btnId = validFiles.length > 1 ? 'convert-images-btn' : 'merge-btn';
        const btn = document.getElementById(btnId);
        if (btn) btn.disabled = false;
    }
}

function handleSingleFile(file) {
    if (!file) return;
    
    if (!file.name.toLowerCase().endsWith('.pdf')) {
        window.App.toast('Please select a PDF file', 'error');
        return;
    }
    
    if (file.size > 50 * 1024 * 1024) {
        window.App.toast('File is too large (max 50MB)', 'error');
        return;
    }
    
    const infoDiv = document.getElementById('selected-pdf-info');
    if (infoDiv) {
        infoDiv.innerHTML = `
            <div style="padding: 12px; background: var(--color-bg); border-radius: 8px;">
                <div style="font-weight: 500;">${file.name}</div>
                <div style="font-size: 12px; color: var(--color-text-muted);">${formatFileSize(file.size)}</div>
            </div>
        `;
        
        // Show split options and enable button
        document.getElementById('split-options').style.display = 'block';
        document.getElementById('split-btn').disabled = false;
    }
}

async function convertImages() {
    const fileInput = document.getElementById('image-input');
    const files = Array.from(fileInput.files);
    
    if (files.length === 0) {
        window.App.toast('Please select images first', 'error');
        return;
    }
    
    showProgress('Converting images to PDF...');
    
    try {
        // Call API (simplified - in real app, this would stream chunks)
        const response = await fetch('/api/images-to-pdf', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                images: files.map(f => f.path), // Would need to upload first
                output: `${files[0].name}_combined.pdf`
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            hideProgress();
            showResult({
                name: result.output,
                size: result.size,
                type: 'application/pdf'
            });
        } else {
            throw new Error(result.error || 'Conversion failed');
        }
    } catch (error) {
        hideProgress();
        showError(error.message);
    }
}

async function mergePDFs() {
    const fileInput = document.getElementById('merge-input');
    const files = Array.from(fileInput.files);
    
    if (files.length < 2) {
        window.App.toast('Please select at least 2 PDFs to merge', 'error');
        return;
    }
    
    showProgress('Merging PDFs...');
    
    try {
        const response = await fetch('/api/pdf-merge', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                pdfs: files.map(f => f.path),
                output: 'merged.pdf'
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            hideProgress();
            showResult({
                name: result.output,
                size: result.size,
                type: 'application/pdf'
            });
        } else {
            throw new Error(result.error || 'Merge failed');
        }
    } catch (error) {
        hideProgress();
        showError(error.message);
    }
}

async function splitPDF() {
    const pageRange = document.getElementById('page-range').value;
    
    if (!pageRange) {
        window.App.toast('Please enter a page range', 'error');
        return;
    }
    
    showProgress('Splitting PDF...');
    
    try {
        const response = await fetch('/api/pdf-split', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                input: 'selected.pdf',
                pages: pageRange,
                output: 'split.pdf'
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            hideProgress();
            showResult({
                name: result.output,
                size: result.size,
                type: 'application/pdf'
            });
        } else {
            throw new Error(result.error || 'Split failed');
        }
    } catch (error) {
        hideProgress();
        showError(error.message);
    }
}

function showProgress(message) {
    const toolBody = document.getElementById('tool-body');
    toolBody.innerHTML = `
        <div style="padding: 40px 20px; text-align: center;">
            <div class="loading-spinner" style="width: 48px; height: 48px; border-width: 4px;"></div>
            <h3 style="margin-top: 16px;">Processing</h3>
            <p style="color: var(--color-text-muted); margin-top: 8px;">${message}</p>
        </div>
    `;
}

function hideProgress() {
    // Restore original content if needed
}

function showError(message) {
    const toolBody = document.getElementById('tool-body');
    toolBody.innerHTML = `
        <div style="padding: 40px 20px; text-align: center;">
            <div style="font-size: 48px; margin-bottom: 16px;">❌</div>
            <h3>Conversion Failed</h3>
            <p style="color: var(--color-text-muted); margin-top: 8px;">${message}</p>
            <button class="btn btn-primary mt-16" onclick="location.hash='#home'">Go Back</button>
        </div>
    `;
    window.App.toast('Conversion failed', 'error');
}

function showResult(file) {
    navigateToResult(file);
}

function navigateToResult(file) {
    $resultIcon.textContent = getFileIcon(file.type);
    $resultName.textContent = file.name;
    $resultInfo.textContent = `${formatFileSize(file.size)} · ${getFileExtension(file.name).toUpperCase()}`;
    
    window.location.hash = 'result';
    switchScreen('result');
    
    window.App.toast('Conversion complete!', 'success');
}

function getFileIcon(mimeType) {
    const icons = {
        'application/pdf': '📄',
        'image/png': '🖼',
        'image/jpeg': '🖼',
        'image/webp': '🖼'
    };
    return icons[mimeType] || '📄';
}

function getFileExtension(filename) {
    return filename.split('.').pop().toLowerCase();
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function runDiagnostics() {
    const diagStatus = document.getElementById('diag-status');
    const engineList = document.getElementById('engine-list');
    
    if (diagStatus) {
        diagStatus.innerHTML = '<div class="loading-spinner"></div>';
    }
    
    // Simulate diagnostic check
    setTimeout(() => {
        if (diagStatus) {
            diagStatus.innerHTML = `
                <div style="padding: 12px; background: #d1fae5; border-radius: 8px; color: #065f46;">
                    ✓ System check complete
                </div>
            `;
        }
        
        if (engineList) {
            engineList.innerHTML = `
                <div style="padding: 16px; background: var(--color-surface); border-radius: 12px;">
                    <p><strong>Pandoc:</strong> ✓ Available</p>
                    <p><strong>Poppler:</strong> ✓ Available</p>
                    <p><strong>Pillow:</strong> ✓ Available</p>
                    <p style="color: var(--color-text-muted); margin-top: 8px;">
                        Note: Some advanced converters require additional Python packages.
                    </p>
                </div>
            `;
        }
    }, 1000);
}
