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

// Cache DOM elements
const domElements = {
    // Fetch section
    docUrl: document.getElementById('docUrl'),
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
    embdedBtn: document.getElementById('embedBtn'),
    embedStatus: document.getElementById('embedStatus'),
    
    // View Embeddings section
    scanSelectorForViewEmbeddings: document.getElementById('scanSelectorForViewEmbeddings'),
    chunkSetSelectorForViewEmbeddings: document.getElementById('chunkSetSelectorForViewEmbeddings'),
    embeddingSetSelectorForViewEmbeddings: document.getElementById('embeddingSetSelectorForViewEmbeddings'),
    embeddingDisplay: document.getElementById('viewEmbeddings'),
    
    // Query section
    submitBtn: document.getElementById('submitBtn'),
    query: document.getElementById('query'),
    loading: document.getElementById('loading'),
    response: document.getElementById('response')
};

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
        scans.forEach(scan => {
            // Add to scanned URLs selector
            addOptionToSelect(scannedUrlSelector, scan[0], scan[1]);
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
    
    if (!docUrl) {
        domElements.fetchStatus.textContent = 'Please enter a documentation URL';
        return;
    }

    domElements.fetchBtn.disabled = true;
    domElements.fetchStatus.textContent = 'fetching documentation…';

    try {
        const response = await fetch(`/perform_fetch?root_url=${encodeURIComponent(docUrl)}`, {
            method: 'POST'
        });
        if (!response.ok) {
            const data = await response.json();
            handleError('Error fetching documentation', data.errorDetails, data.stackTrace);
            return;
        }
        domElements.fetchStatus.textContent = "";
        // Refresh the scan selectors after fetching
        loadScans();
    } catch (error) {
        handleError('Error fetching documentation', error.message, error.stack);
    } finally {
        domElements.fetchBtn.disabled = false;
    }
});

// load scans into all scan selectors
async function loadScans() {
    // Clear existing options except the default one
    clearSelectOptions(domElements.scanSelectorForChunk);
    clearSelectOptions(domElements.scanSelectorForDisplay);
    clearSelectOptions(domElements.scanSelectorForViewChunk);
    clearSelectOptions(domElements.scanSelectorForEmbedding);
    clearSelectOptions(domElements.scanSelectorForViewEmbeddings);
    
    try {
        const response = await fetch('/scans');
        if (!response.ok) {
            const errorData = await response.json();
            handleError('Error fetching scans', errorData.errorDetails, errorData.stackTrace);
            return;
        }
        const scans = await response.json();
        scans.forEach(scan => {
            const value = scan[0];
            const textContent = scan[1] + " - " + scan[2];

            // Add to all selectors
            addOptionToSelect(domElements.scanSelectorForChunk, value, textContent);
            addOptionToSelect(domElements.scanSelectorForDisplay, value, textContent);
            addOptionToSelect(domElements.scanSelectorForViewChunk, value, textContent);
            addOptionToSelect(domElements.scanSelectorForEmbedding, value, textContent);
            addOptionToSelect(domElements.scanSelectorForViewEmbeddings, value, textContent);
        });
    } catch (error) {
        handleError('Error fetching scans', error.message, error.stack);
    }
}

// load scans when the page loads
document.addEventListener('DOMContentLoaded', () => {
    loadScans();
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

// embed documentation
domElements.embdedBtn.addEventListener('click', async () => {
    const chunkSetId = domElements.chunkSetSelectorForEmbedding.value;
    
    if (chunkSetId == 0) {
        return;
    }
    
    domElements.embdedBtn.disabled = true;
    domElements.embedStatus.textContent = 'embedding documentation…';
    
    try {
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

// answer question
domElements.submitBtn.addEventListener('click', async () => {
    const query = domElements.query.value;
    
    if (!query) return;
    
    domElements.loading.style.display = 'block';
    domElements.response.innerHTML = '';
    domElements.submitBtn.disabled = true;
    
    try {
        const response = await fetch('generate_answer', {
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
