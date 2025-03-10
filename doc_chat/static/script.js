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
    fetchBtn: document.getElementById('fetchBtn'),
    fetchStatus: document.getElementById('fetchStatus'),
    docUrl: document.getElementById('docUrl'),
    
    // Scan selectors
    scanSelectorForChunk: document.getElementById('scanSelectorForChunk'),
    scanSelectorForDisplay: document.getElementById('scanSelectorForDisplay'),
    scanSelectorForViewChunk: document.getElementById('scanSelectorForViewChunk'),
    
    // Scanned URL selectors
    scannedUrlSelectorForDisplay: document.getElementById('scannedUrlSelectorForDisplay'),
    chunkSetSelectorForViewChunk: document.getElementById('chunkSetSelectorForViewChunk'),
    scannedUrlSelectorForViewChunk: document.getElementById('scannedUrlSelectorForViewChunk'),
    scannedUrlDisplay: document.getElementById('scannedUrlDisplay'),
    
    // Chunk section
    chunkBtn: document.getElementById('chunkBtn'),
    chunkStatus: document.getElementById('chunkStatus'),
    chunkSelectorForViewChunk: document.getElementById('chunkSelectorForViewChunk'),
    chunkDisplay: document.getElementById('chunkDisplay'),
    
    // Display section
    displayScannedUrlBtn: document.getElementById('displayScannedUrlBtn'),
    
    // Query section
    submitBtn: document.getElementById('submitBtn'),
    query: document.getElementById('query'),
    loading: document.getElementById('loading'),
    response: document.getElementById('response')
};

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

// Function to load scans into both selectors
async function loadScans() {
    // Clear existing options except the default one
    clearSelectOptions(domElements.scanSelectorForChunk);
    clearSelectOptions(domElements.scanSelectorForDisplay);
    clearSelectOptions(domElements.scanSelectorForViewChunk);
    
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
        });
    } catch (error) {
        handleError('Error fetching scans', error.message, error.stack);
    }
}

// Load scans when the page loads
document.addEventListener('DOMContentLoaded', () => {
    loadScans();
});

domElements.scanSelectorForDisplay.addEventListener('input', async () => {
    const scan_id = domElements.scanSelectorForDisplay.value;

    // Clear existing options except the default one
    clearSelectOptions(domElements.scannedUrlSelectorForDisplay);

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
            addOptionToSelect(domElements.scannedUrlSelectorForDisplay, scan[0], scan[1]);
        });

    } catch (error) {
        handleError('Error fetching scanned URLs', error.message, error.stack);
    } finally {
        domElements.fetchBtn.disabled = false;
    }
})

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

async function populateChunkSelectorForChunkDisplay() {

    // Clear existing options except the default one
    clearSelectOptions(domElements.chunkSelectorForViewChunk);
    domElements.chunkDisplay.textContent = '';
    
    const chunkSetId = domElements.chunkSetSelectorForViewChunk.value;
    const scannedUrlId = domElements.scannedUrlSelectorForViewChunk.value;
    
    if (chunkSetId == 0) {
        return;
    }
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
            addOptionToSelect(domElements.chunkSelectorForViewChunk, chunk, `Chunk ${chunk}`);
        });
    } catch (error) {
        handleError('Error fetching chunks for view chunks', error.message, error.stack);
    }
}
// Event listener for the scan selector in the View Chunks section
domElements.scanSelectorForViewChunk.addEventListener('input', async () => {
    const scan_id = domElements.scanSelectorForViewChunk.value;
    
    // Clear existings options except the default one
    clearSelectOptions(domElements.chunkSetSelectorForViewChunk);

    // Clear existing options except the default one
    clearSelectOptions(domElements.scannedUrlSelectorForViewChunk);
    
    // Clear chunk selector and display
    clearSelectOptions(domElements.chunkSelectorForViewChunk);
    domElements.chunkDisplay.textContent = '';
    
    if (scan_id == 0) {
        return;
    }

    try {
        const response = await fetch(`/chunk_sets?scan_id=${scan_id}`);
        if (!response.ok) {
            const errorData = await response.json();
            handleError('Error fetching chunk sets for view chunks', errorData.errorDetails, errorData.stackTrace);
            return;
        }
        const chunkSets = await response.json();
        chunkSets.forEach(chunkSet => {
            // Add to chunk set selector
            addOptionToSelect(domElements.chunkSetSelectorForViewChunk, chunkSet[0], chunkSet[1]);
        });
    } catch (error) {
        handleError('Error fetching chunk sets for view chunks', error.message, error.stack);
    }

    try {
        const response = await fetch(`/scanned_urls?scan_id=${scan_id}`);
        if (!response.ok) {
            const errorData = await response.json();
            handleError('Error fetching scanned URLs for view chunks', errorData.errorDetails, errorData.stackTrace);
            return;
        }
        const scannedUrls = await response.json();
        scannedUrls.forEach(url => {
            // Add to scanned URLs selector
            addOptionToSelect(domElements.scannedUrlSelectorForViewChunk, url[0], url[1]);
        });
    } catch (error) {
        handleError('Error fetching scanned URLs for view chunks', error.message, error.stack);
    }
});

// Event listener for the chunk set selector in the View Chunks section
domElements.chunkSetSelectorForViewChunk.addEventListener('input', populateChunkSelectorForChunkDisplay);

// Event listener for the scanned URL selector in the View Chunks section
domElements.scannedUrlSelectorForViewChunk.addEventListener('input', populateChunkSelectorForChunkDisplay);

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
