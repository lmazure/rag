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
function showErrorPopup(message) {
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
        <div class="error-popup-message">${message}</div>
    `;
    
    // Show the popup
    errorPopup.style.display = 'block';
    errorPopup.style.opacity = '1';
}

// Utility function for standardized error handling
function handleError(error, operation, errorMessage = null) {
    // Always log the error to console with operation context
    console.error(`Error ${operation}:`, error);
    
    // Show error popup
    showErrorPopup(errorMessage);
    
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
    scannedUrlSelectorForViewChunk: document.getElementById('scannedUrlSelectorForViewChunk'),
    scannedUrlDisplay: document.getElementById('scannedUrlDisplay'),
    
    // Chunk section
    chunkBtn: document.getElementById('chunkBtn'),
    chunkStatus: document.getElementById('chunkStatus'),
    chunkSelector: document.getElementById('chunkSelector'),
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
        const response = await fetch(`/fetch?root_url=${encodeURIComponent(docUrl)}`, {
            method: 'POST'
        });
        const data = await response.json();
        domElements.fetchStatus.textContent = data.message;
        
        // Refresh the scan selectors after fetching
        loadScans();
    } catch (error) {
        handleError(error, 'fetching documentation', 'Error fetching documentation');
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
        handleError(error, 'fetching scans', 'Error fetching scans');
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
        const scans = await response.json();
        scans.forEach(scan => {
            // Add to scanned URLs selector
            addOptionToSelect(domElements.scannedUrlSelectorForDisplay, scan[0], scan[1]);
        });

    } catch (error) {
        handleError(error, 'fetching scanned URLs', 'Error fetching scanned URLs');
    } finally {
        domElements.fetchBtn.disabled = false;
    }}
)

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
        const data = await response.json();
        displayedDocumentation.textContent = data;
    } catch (error) {
        handleError(error, 'fetching scanned URL content', 'Error loading content');
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
        const response = await fetch(`/perform_chunk?scan_id=${scanId}`, {
            method: 'POST'
        });
        const data = await response.json();
        domElements.chunkStatus.textContent = data.message;
    } catch (error) {
        handleError(error, 'chunking documentation', 'Error chunking documentation');
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
        const res = await fetch('/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query })
        });
        
        const data = await res.json();
        
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
        handleError(error, 'getting query response', 'Error getting response');
    } finally {
        domElements.loading.style.display = 'none';
        domElements.submitBtn.disabled = false;
    }
});

// Event listener for the scan selector in the View Chunks section
domElements.scanSelectorForViewChunk.addEventListener('input', async () => {
    const scan_id = domElements.scanSelectorForViewChunk.value;
    
    // Clear existing options except the default one
    clearSelectOptions(domElements.scannedUrlSelectorForViewChunk);
    
    // Clear chunk selector and display
    clearSelectOptions(domElements.chunkSelector);
    domElements.chunkDisplay.textContent = '';
    
    if (scan_id == 0) {
        return;
    }
    
    try {
        const response = await fetch(`/scanned_urls?scan_id=${scan_id}`);
        const scannedUrls = await response.json();
        scannedUrls.forEach(url => {
            // Add to scanned URLs selector
            addOptionToSelect(domElements.scannedUrlSelectorForViewChunk, url[0], url[1]);
        });
    } catch (error) {
        handleError(error, 'fetching scanned URLs for view chunks', 'Error fetching scanned URLs for view chunks');
    }
});

// Event listener for the scanned URL selector in the View Chunks section
domElements.scannedUrlSelectorForViewChunk.addEventListener('input', async () => {
    const scan_id = domElements.scanSelectorForViewChunk.value;
    const scannedUrlId = domElements.scannedUrlSelectorForViewChunk.value;
    
    // Clear existing options except the default one
    clearSelectOptions(domElements.chunkSelector);
    domElements.chunkDisplay.textContent = '';
    
    if (scannedUrlId == 0) {
        return;
    }
    
    try {
        const response = await fetch(`/chunks?scanned_url_id=${scannedUrlId}`);
        const chunks = await response.json();
        
        chunks.forEach(chunk => {
            addOptionToSelect(domElements.chunkSelector, chunk, `Chunk ${chunk}`);
        });
    } catch (error) {
        handleError(error, 'fetching chunks', 'Error fetching chunks');
    }
});

// Event listener for the chunk selector
domElements.chunkSelector.addEventListener('input', async () => {
    const chunkId = domElements.chunkSelector.value;
    
    if (chunkId == 0) {
        domElements.chunkDisplay.textContent = '';
        return;
    }
    
    try {
        const response = await fetch(`/chunk_content?chunk_id=${chunkId}`);
        const data = await response.json();
        domElements.chunkDisplay.textContent = data.text;
    } catch (error) {
        handleError(error, 'fetching chunk content', 'Error loading chunk content');
    }
});
