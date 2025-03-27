// Utility function to clear select options except the first one
function clearSelectOptions(selectElement) {
    while (selectElement.options.length > 1) {
        selectElement.remove(1);
    }
}

// Utility function to add an option to a select element
function addOptionToSelect(selectElement, value, text) {
    const option = document.createElement('option');
    option.value = value;
    option.textContent = text;
    selectElement.appendChild(option);
}

// Function to display error popup
function showErrorPopup(message, details, stack) {
    // Create error popup container if it doesn't exist
    let errorPopup = document.getElementById('errorPopup');
    if (!errorPopup) {
        errorPopup = document.createElement('div');
        errorPopup.id = 'errorPopup';
        errorPopup.className = 'error-popup';
        document.body.appendChild(errorPopup);
    }

    // Set error message
    errorPopup.innerHTML = `
        <div class="error-popup-header">
            <strong>Error</strong>
            <button class="error-popup-close" onclick="this.parentElement.parentElement.style.display='none'">&times;</button>
        </div>
        <div class="error-popup-message">${message?message:''}</div>
        <details>
            <summary>${details?details:'Details'}</summary>
            <textarea class="error-popup-stack" readonly>${stack?stack:''}</textarea>
        </details>
    `;
    
    // Show the popup
    errorPopup.style.display = 'block';
    errorPopup.style.opacity = '1';
}

// Utility function for standardized error handling
function handleError(errorMessage, errorDetails, stackTrace) {
    // Always log the error to console
    console.error(`message: ${errorMessage}\nerror details: ${errorDetails}\nstacktrace: ${stackTrace}`);
    
    // Show error popup
    showErrorPopup(errorMessage, errorDetails, stackTrace);
    
    return;
}

// Logs functionality
let lastLogId = 0;
let logsRefreshInterval = null;

// Function to fetch and display logs
async function fetchLogs() {
    try {
        const response = await fetch(`/logs?id=${lastLogId}`);
        if (!response.ok) {
            const errorData = await response.json();
            handleError('Error fetching logs', errorData.errorDetails, errorData.stackTrace);
            return;
        }
        
        const logs = await response.json();
        if (logs.length > 0) {
            const logsContent = document.getElementById('logsContent');
            
            logs.forEach(log => {
                const logEntry = document.createElement('div');
                logEntry.className = `log-entry log-${log.log_type.toLowerCase()}`;
                logEntry.innerHTML = `<strong>[${log.created_at}] [${log.log_type}]:</strong> ${log.log}`;
                logsContent.appendChild(logEntry);
                
                // Update the last log ID
                lastLogId = Math.max(lastLogId, log.id);
            });
            
            // Auto-scroll to the bottom
            logsContent.scrollTop = logsContent.scrollHeight;
        }
    } catch (error) {
        handleError('Error fetching logs', error.message, error.stack);
    }
}

// Function to start logs refresh interval
function startLogsRefresh() {
    // Clear any existing interval
    if (logsRefreshInterval) {
        clearInterval(logsRefreshInterval);
    }
    
    // Fetch logs immediately
    fetchLogs();
    
    // Set up interval to refresh logs every 2 seconds
    logsRefreshInterval = setInterval(fetchLogs, 2000);
}

// Function to stop logs refresh interval
function stopLogsRefresh() {
    if (logsRefreshInterval) {
        clearInterval(logsRefreshInterval);
        logsRefreshInterval = null;
    }
}

// Cache DOM elements
const domElements = {
    // Logs section
    logsButton: document.getElementById('logsButton'),
    logsModal: document.getElementById('logsModal'),
    logsClose: document.querySelector('.logs-close'),
    logsContent: document.getElementById('logsContent'),
    
    // Fetch section
    docUrl: document.getElementById('docUrl'),
    reaper: document.getElementById('reaper'),
    fetchBtn: document.getElementById('fetchBtn'),
    fetchStatus: document.getElementById('fetchStatus'),
    
    // Display scanned URL section
    scanSelectorForDisplay: document.getElementById('scanSelectorForDisplay'),
    scannedUrlSelectorForDisplay: document.getElementById('scannedUrlSelectorForDisplay'),
    scannedUrlDisplay: document.getElementById('scannedUrlDisplay'),
    displayScannedUrlBtn: document.getElementById('displayScannedUrlBtn'),
    
    // Chunk section
    scanSelectorForChunk: document.getElementById('scanSelectorForChunk'),
    chunkBtn: document.getElementById('chunkBtn'),
    chunkStatus: document.getElementById('chunkStatus'),
    
    // View Chunks section
    scanSelectorForViewChunk: document.getElementById('scanSelectorForViewChunk'),
    chunkSetSelectorForViewChunk: document.getElementById('chunkSetSelectorForViewChunk'),
    scannedUrlSelectorForViewChunk: document.getElementById('scannedUrlSelectorForViewChunk'),
    chunkSelectorForViewChunk: document.getElementById('chunkSelectorForViewChunk'),
    chunkDisplay: document.getElementById('chunkDisplay'),
    
    // Embed section
    scanSelectorForEmbedding: document.getElementById('scanSelectorForEmbedding'),
    chunkSetSelectorForEmbedding: document.getElementById('chunkSetSelectorForEmbedding'),
    embeddingModelSelector: document.getElementById('embeddingModelSelector'),
    embdedBtn: document.getElementById('embedBtn'),
    embedStatus: document.getElementById('embedStatus'),
    
    // View Embeddings section
    scanSelectorForViewEmbeddings: document.getElementById('scanSelectorForViewEmbeddings'),
    chunkSetSelectorForViewEmbeddings: document.getElementById('chunkSetSelectorForViewEmbeddings'),
    embeddingSetSelectorForViewEmbeddings: document.getElementById('embeddingSetSelectorForViewEmbeddings'),
    embeddingDisplay: document.getElementById('viewEmbeddings'),
    
    // Query section
    scanSelectorForQuestionAnswering: document.getElementById('scanSelectorForQuestionAnswering'),
    chunkSetSelectorForQuestionAnswering: document.getElementById('chunkSetSelectorForQuestionAnswering'),
    embeddingSetForSelectorForQuestionAnswering: document.getElementById('embeddingSetForSelectorForQuestionAnswering'),
    question: document.getElementById('question'),
    submitBtn: document.getElementById('submitBtn'),
    loading: document.getElementById('loading'),
    response: document.getElementById('response')
};

// Event listeners for logs modal
domElements.logsButton.addEventListener('click', () => {
    domElements.logsModal.style.display = 'block';
    startLogsRefresh();
});

domElements.logsClose.addEventListener('click', () => {
    domElements.logsModal.style.display = 'none';
    stopLogsRefresh();
});

// Close modal when clicking outside of it
window.addEventListener('click', (event) => {
    if (event.target === domElements.logsModal) {
        domElements.logsModal.style.display = 'none';
        stopLogsRefresh();
    }
});

async function populateScannedUrlSelector(scanSelector, scannedUrlSelector) {
    const scan_id = scanSelector.value;

    // Clear existing options except the default one
    clearSelectOptions(scannedUrlSelector);

    if (scan_id == 0) {
        return;
    }

    try {
        const response = await fetch(`/scanned_urls?scan_id=${scan_id}`);
        if (!response.ok) {
            const errorData = await response.json();
            handleError('Error fetching scanned URLs', errorData.errorDetails, errorData.stackTrace);
            return;
        }
        const scans = await response.json();
        scans.sort((a, b) => a.url.localeCompare(b.url));
        scans.forEach(scan => {
            // Add to scanned URLs selector
            addOptionToSelect(scannedUrlSelector, scan.id, scan.url);
        });

    } catch (error) {
        handleError('Error fetching scanned URLs', error.message, error.stack);
    }
}

async function populateChunkSetSelector(scanSelector, chunkSetSelector) {

    // Clear existing options except the default one
    clearSelectOptions(chunkSetSelector);
    
    const scan_id = scanSelector.value;
    if (scan_id == 0) {
        return;
    }

    try {
        const response = await fetch(`/chunk_sets?scan_id=${scan_id}`);
        if (!response.ok) {
            const errorData = await response.json();
            handleError('Error fetching chunk sets', errorData.errorDetails, errorData.stackTrace);
            return;
        }
        const chunkSets = await response.json();
        chunkSets.forEach(chunkSet => {
            // Add to chunk set selector
            addOptionToSelect(chunkSetSelector, chunkSet.id, `Chunk Set ${chunkSet.id} - ${chunkSet.chunker_description} - ${chunkSet.created_at}`);
        });
    } catch (error) {
        handleError('Error fetching chunk sets', error.message, error.stack);
    }
}

async function populateChunkSelector(scannedUrlSelector, chunkSetSelector, chunkSelector) {

    // Clear existing options except the default one
    clearSelectOptions(chunkSelector);

    const chunkSetId = chunkSetSelector.value;
    if (chunkSetId == 0) {
        return;
    }

    const scannedUrlId = scannedUrlSelector.value;
    if (scannedUrlId == 0) {
        return;
    }
    
    try {
        const response = await fetch(`/chunks?scanned_url_id=${scannedUrlId}&chunk_set_id=${chunkSetId}`);
        if (!response.ok) {
            const errorData = await response.json();
            handleError('Error fetching chunks for view chunks', errorData.errorDetails, errorData.stackTrace);
            return;
        }
        const chunks = await response.json();
        chunks.forEach(chunk => {
            // Add to chunk selector
            addOptionToSelect(chunkSelector, chunk, `Chunk ${chunk}`);
        });
    } catch (error) {
        handleError('Error fetching chunks for view chunks', error.message, error.stack);
    }
}

async function populateEmbeddingSetSelector(chunkSetSelector, embeddingSetSelector) {

    const chunkSetId = chunkSetSelector.value;
    if (chunkSetId == 0) {
        return;
    }

    clearSelectOptions(embeddingSetSelector);
    try {
        const response = await fetch(`/embedding_sets?chunk_set_id=${chunkSetId}`);
        if (!response.ok) {
            const errorData = await response.json();
            handleError('Error fetching embedding sets', errorData.errorDetails, errorData.stackTrace);
            return;
        }
        const embeddingSets = await response.json();
        embeddingSets.forEach(embeddingSet => {
            // Add to embedding set selector
            addOptionToSelect(embeddingSetSelector, embeddingSet.id, `Embedding Set ${embeddingSet.id} - ${embeddingSet.embedder_description} - ${embeddingSet.created_at}`);
        });
    } catch (error) {
        handleError('Error fetching embedding sets', error.message, error.stack);
    }
}

domElements.fetchBtn.addEventListener('click', async () => {
    const docUrl = domElements.docUrl.value.trim();
    const reaper = domElements.reaper.value;
    
    if (!docUrl) {
        domElements.fetchStatus.textContent = 'Please enter a documentation URL';
        return;
    }

    domElements.fetchBtn.disabled = true;
    domElements.fetchStatus.textContent = 'fetching documentation…';

    try {
        const response = await fetch(`/perform_fetch?root_url=${encodeURIComponent(docUrl)}&reaper=${reaper}`, {
            method: 'POST'
        });
        if (!response.ok) {
            const data = await response.json();
            handleError('Error fetching documentation', data.errorDetails, data.stackTrace);
            return;
        }
        const data = await response.json();
        domElements.fetchStatus.textContent = data.message;
        // Refresh the scan selectors after fetching
        populateScanSelectors();
    } catch (error) {
        handleError('Error fetching documentation', error.message, error.stack);
    } finally {
        domElements.fetchBtn.disabled = false;
    }
});

// load scans into all scan selectors
async function populateScanSelectors() {
    // Clear existing options except the default one
    clearSelectOptions(domElements.scanSelectorForChunk);
    clearSelectOptions(domElements.scanSelectorForDisplay);
    clearSelectOptions(domElements.scanSelectorForViewChunk);
    clearSelectOptions(domElements.scanSelectorForEmbedding);
    clearSelectOptions(domElements.scanSelectorForViewEmbeddings);
    clearSelectOptions(domElements.scanSelectorForQuestionAnswering);
    
    try {
        const response = await fetch('/scans');
        if (!response.ok) {
            const errorData = await response.json();
            handleError('Error fetching scans', errorData.errorDetails, errorData.stackTrace);
            return;
        }
        const scans = await response.json();
        scans.forEach(scan => {
            const value = scan.id;
            const textContent = scan.root_url + " - " + scan.reaper_type + " - " + scan.created_at;

            // Add to all selectors
            addOptionToSelect(domElements.scanSelectorForChunk, value, textContent);
            addOptionToSelect(domElements.scanSelectorForDisplay, value, textContent);
            addOptionToSelect(domElements.scanSelectorForViewChunk, value, textContent);
            addOptionToSelect(domElements.scanSelectorForEmbedding, value, textContent);
            addOptionToSelect(domElements.scanSelectorForViewEmbeddings, value, textContent);
            addOptionToSelect(domElements.scanSelectorForQuestionAnswering, value, textContent);
        });
    } catch (error) {
        handleError('Error fetching scans', error.message, error.stack);
    }
}

// load scans when the page loads
document.addEventListener('DOMContentLoaded', () => {
    populateScanSelectors();
    populateEmbeddingModelSelector();
});

domElements.scanSelectorForDisplay.addEventListener('input', async () => {
    populateScannedUrlSelector(domElements.scanSelectorForDisplay, domElements.scannedUrlSelectorForDisplay);
    domElements.fetchBtn.disabled = false;
})

// display content of scanned URL
domElements.scannedUrlSelectorForDisplay.addEventListener('input', async () => {
    const scanned_url_id = domElements.scannedUrlSelectorForDisplay.value;
    domElements.scannedUrlSelectorForDisplay.value = scanned_url_id;
    const displayedDocumentation = domElements.scannedUrlDisplay;

    if (scanned_url_id == 0) {
        displayedDocumentation.textContent = '';
        return;
    }

    try {
        const response = await fetch(`/scanned_url?scanned_url_id=${scanned_url_id}`);
        if (!response.ok) {
            const errorData = await response.json();
            handleError('Error fetching scanned URL content', errorData.errorDetails, errorData.stackTrace);
            return;
        }
        const data = await response.json();
        displayedDocumentation.textContent = data;
    } catch (error) {
        handleError('Error fetching scanned URL content', error.message, error.stack);
    }
})

// open a scanned URL in a new Browser tab
domElements.displayScannedUrlBtn.addEventListener('click', () => {
    const scanned_url_id = domElements.scannedUrlSelectorForDisplay.value;
    const scanned_url = domElements.scannedUrlSelectorForDisplay.options[domElements.scannedUrlSelectorForDisplay.selectedIndex].text;

    if (scanned_url_id == 0) {
        return;
    }

    const newTab = window.open(scanned_url, '_blank');
    if (newTab) {
        newTab.focus();
    } else {
        console.warn('Unable to open new tab. Pop-up blocker might be enabled.');
    }

})

// chunk content of a scan
domElements.chunkBtn.addEventListener('click', async () => {
    const scanId = domElements.scanSelectorForChunk.value;
    
    if (scanId == 0) {
        domElements.chunkStatus.textContent = 'Please select a scan';
        return;
    }
    
    domElements.chunkBtn.disabled = true;
    domElements.chunkStatus.textContent = 'chunking documentation…';
    
    try {
        const response = await fetch(`/perform_chunking?scan_id=${scanId}`, {
            method: 'POST'
        });
        if (!response.ok) {
            const errorData = await response.json();
            handleError('Error chunking documentation', errorData.errorDetails, errorData.stackTrace);
            return;
        }
        const data = await response.json();
        domElements.chunkStatus.textContent = data.message;
    } catch (error) {
        handleError('Error chunking documentation', error.message, error.stack);
    } finally {
        domElements.chunkBtn.disabled = false;
    }
});

// Event listener for the scan selector in the View Chunks section
domElements.scanSelectorForViewChunk.addEventListener('input', async () => {

    populateScannedUrlSelector(domElements.scanSelectorForViewChunk, domElements.scannedUrlSelectorForViewChunk);

    populateChunkSetSelector(domElements.scanSelectorForViewChunk, domElements.chunkSetSelectorForViewChunk);

    // Clear chunk selector and display
    clearSelectOptions(domElements.chunkSelectorForViewChunk);

    domElements.chunkDisplay.textContent = '';
});

async function populateChunkSelectorForDisplay() {
    
    domElements.chunkDisplay.textContent = '';
    populateChunkSelector(domElements.scannedUrlSelectorForViewChunk, domElements.chunkSetSelectorForViewChunk, domElements.chunkSelectorForViewChunk);
}

// Event listener for the chunk set selector in the View Chunks section
domElements.chunkSetSelectorForViewChunk.addEventListener('input', populateChunkSelectorForDisplay);

// Event listener for the scanned URL selector in the View Chunks section
domElements.scannedUrlSelectorForViewChunk.addEventListener('input', populateChunkSelectorForDisplay);

// Event listener for the chunk selector in the View Chunks section
domElements.chunkSelectorForViewChunk.addEventListener('input', async () => {
    const chunkId = domElements.chunkSelectorForViewChunk.value;
    
    if (chunkId == 0) {
        domElements.chunkDisplay.textContent = '';
        return;
    }
    
    try {
        const response = await fetch(`/chunk_content?chunk_id=${chunkId}`);
        if (!response.ok) {
            const errorData = await response.json();
            handleError('Error fetching chunk content', errorData.errorDetails, errorData.stackTrace);
            return;
        }
        const data = await response.json();
        domElements.chunkDisplay.textContent = data.text;
    } catch (error) {
        handleError('Error fetching chunk content', error.message, error.stack);
    }
});

// Event listener for the scan selector in the Embed section
domElements.scanSelectorForEmbedding.addEventListener('input', async () => {
    populateChunkSetSelector(domElements.scanSelectorForEmbedding, domElements.chunkSetSelectorForEmbedding);
});

// Function to populate the embedding model selector
async function populateEmbeddingModelSelector() {
    // Clear existing options except the default one
    clearSelectOptions(domElements.embeddingModelSelector);
    
    try {
        const response = await fetch('/embedding_models');
        if (!response.ok) {
            const errorData = await response.json();
            handleError('Error fetching embedding models', errorData.errorDetails, errorData.stackTrace);
            return;
        }
        
        const models = await response.json();
        
        models.forEach(model => {
            const displayText = `${model.host} - ${model.model}`;
            const value = JSON.stringify({ host: model.host, model: model.model, url: model.url });
            addOptionToSelect(domElements.embeddingModelSelector, value, displayText);
        });
    } catch (error) {
        handleError('Error fetching embedding models', error.message, error.stack);
    }
}

// embed documentation
domElements.embdedBtn.addEventListener('click', async () => {
    const chunkSetId = domElements.chunkSetSelectorForEmbedding.value;
    const embeddingModelValue = domElements.embeddingModelSelector.value;
    
    if (chunkSetId == 0) {
        return;
    }
    
    if (embeddingModelValue == 0) {
        handleError('Error embedding documentation', 'Please select an embedding model', '');
        return;
    }
    
    domElements.embdedBtn.disabled = true;
    domElements.embedStatus.textContent = 'embedding documentation…';
    
    try {
        // For now, we're just storing the selected model but not using it in the API call
        // The backend API will be updated later to use this value
        const selectedModel = JSON.parse(embeddingModelValue);
        console.log('Selected embedding model:', selectedModel);
        
        const response = await fetch(`/perform_embedding?chunk_set_id=${chunkSetId}`, {
            method: 'POST'
        });
        if (!response.ok) {
            const errorData = await response.json();
            handleError('Error embedding documentation', errorData.errorDetails, errorData.stackTrace);
            return;
        }
        const data = await response.json();
        domElements.embedStatus.textContent = data.message;
    } catch (error) {
        handleError('Error embedding documentation', error.message, error.stack);
    } finally {
        domElements.embdedBtn.disabled = false;
    }
});

domElements.scanSelectorForViewEmbeddings.addEventListener('input', async () => {
    populateChunkSetSelector(domElements.scanSelectorForViewEmbeddings, domElements.chunkSetSelectorForViewEmbeddings);
});

domElements.chunkSetSelectorForViewEmbeddings.addEventListener('input', async () => {
    populateEmbeddingSetSelector(domElements.chunkSetSelectorForViewEmbeddings, domElements.embeddingSetSelectorForViewEmbeddings);
});

domElements.embeddingSetSelectorForViewEmbeddings.addEventListener('input', async () => {
    const embeddingSetId = domElements.embeddingSetSelectorForViewEmbeddings.value;
    
    if (embeddingSetId == 0) {
        return;
    }
    
    try {
        const response = await fetch(`/embeddings?embedding_set_id=${embeddingSetId}`);
        if (!response.ok) {
            const errorData = await response.json();
            handleError('Error fetching embeddings', errorData.errorDetails, errorData.stackTrace);
            return;
        }
        const embeddings = await response.json();
        domElements.embeddingDisplay.textContent = JSON.stringify(embeddings, null, 2);
    } catch (error) {
        handleError('Error fetching embeddings', error.message, error.stack);
    }
});

domElements.scanSelectorForQuestionAnswering.addEventListener('input', async () => {
    populateChunkSetSelector(domElements.scanSelectorForQuestionAnswering, domElements.chunkSetSelectorForQuestionAnswering);
});

domElements.chunkSetSelectorForQuestionAnswering.addEventListener('input', async () => {
    populateEmbeddingSetSelector(domElements.chunkSetSelectorForQuestionAnswering, domElements.embeddingSetForSelectorForQuestionAnswering);
});

// answer question
domElements.submitBtn.addEventListener('click', async () => {
    const embeddingSetId = domElements.embeddingSetForSelectorForQuestionAnswering.value;
    const query = domElements.question.value;
    
    if (!query) return;
    
    domElements.loading.style.display = 'block';
    domElements.response.innerHTML = '';
    domElements.submitBtn.disabled = true;
    
    try {
        const response = await fetch(`generate_answer?embedding_set_id=${embeddingSetId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query })
        });
        if (!response.ok) {
            const data = await response.json();
            handleError('Error answering question', data.errorDetails, data.stackTrace);
            return;
        }
        const data = await response.json();
        
        domElements.response.innerHTML = `
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title">Answer:</h5>
                    <p class="card-text">${data.answer}</p>
                    <div class="sources">
                        <strong>Sources:</strong><br>
                        ${data.sources.map(source => `<a href="${source}" target="_blank">${source}</a>`).join('<br>')}
                    </div>
                </div>
            </div>
        `;
    } catch (error) {
        handleError('Error getting query response', error.message, error.stack);
    } finally {
        domElements.loading.style.display = 'none';
        domElements.submitBtn.disabled = false;
    }
});
