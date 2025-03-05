document.getElementById('fetchBtn').addEventListener('click', async () => {
    const fetchStatus = document.getElementById('fetchStatus');
    const fetchBtn = document.getElementById('fetchBtn');
    const docUrl = document.getElementById('docUrl').value.trim();
    
    if (!docUrl) {
        fetchStatus.textContent = 'Please enter a documentation URL';
        return;
    }
    
    fetchBtn.disabled = true;
    fetchStatus.textContent = 'fetching documentation…';
    
    try {
        const response = await fetch(`/fetch?root_url=${encodeURIComponent(docUrl)}`, {
            method: 'POST'
        });
        const data = await response.json();
        fetchStatus.textContent = data.message;
        
        // Refresh the scan selectors after fetching
        loadScans();
    } catch (error) {
        fetchStatus.textContent = 'Error fetching documentation';
        console.error(error);
    } finally {
        fetchBtn.disabled = false;
    }
});

// Function to load scans into both selectors
async function loadScans() {
    const scanSelectorForChunk = document.getElementById('scanSelectorForChunk');
    const scanSelectorForDisplay = document.getElementById('scanSelectorForDisplay');
    const scanSelectorForViewChunk = document.getElementById('scanSelectorForViewChunk');
    
    // Clear existing options except the default one
    while (scanSelectorForChunk.options.length > 1) {
        scanSelectorForChunk.remove(1);
    }
    
    while (scanSelectorForDisplay.options.length > 1) {
        scanSelectorForDisplay.remove(1);
    }
    
    while (scanSelectorForViewChunk.options.length > 1) {
        scanSelectorForViewChunk.remove(1);
    }
    
    try {
        const response = await fetch('/scans');
        const scans = await response.json();
        scans.forEach(scan => {
            value = scan[0];
            textContent = scan[1] + " - " + scan[2];

            // Add to chunk selector
            const chunkOption = document.createElement('option');
            chunkOption.value = value;
            chunkOption.textContent = textContent;
            scanSelectorForChunk.appendChild(chunkOption);
            
            // Add to scan selector
            const displayOption = document.createElement('option');
            displayOption.value = value;
            displayOption.textContent = textContent;
            scanSelectorForDisplay.appendChild(displayOption);
            
            // Add to view chunk selector
            const viewChunkOption = document.createElement('option');
            viewChunkOption.value = value;
            viewChunkOption.textContent = textContent;
            scanSelectorForViewChunk.appendChild(viewChunkOption);
        });
    } catch (error) {
        console.error('Error fetching scans:', error);
    }
}

// Load scans when the page loads
document.addEventListener('DOMContentLoaded', () => {
    loadScans();
});

document.getElementById('scanSelectorForDisplay').addEventListener('input', async () => {
    const scan_id = document.getElementById('scanSelectorForDisplay').value;
    const scannedUrlSelectorForDisplay = document.getElementById('scannedUrlSelectorForDisplay');

    // Clear existing options except the default one
    while (scannedUrlSelectorForDisplay.options.length > 1) {
        scannedUrlSelectorForDisplay.remove(1);
    }

    if (scan_id == 0) {
        return;
    }

    try {
        const response = await fetch(`/scanned_urls?scan_id=${scan_id}`, {
            method: 'POST'
        });
        const scans = await response.json();
        scans.forEach(scan => {
            // Add to scanned URLs selector
            const scannedUrlOption = document.createElement('option');
            scannedUrlOption.value = scan[0];
            scannedUrlOption.textContent = scan[1];
            scannedUrlSelectorForDisplay.appendChild(scannedUrlOption);
        });

    } catch (error) {
        fetchStatus.textContent = 'Error fetching documentation';
        console.error(error);
    } finally {
        fetchBtn.disabled = false;
    }}
)

document.getElementById('scannedUrlSelectorForDisplay').addEventListener('input', async () => {
    const scanned_url_id = document.getElementById('scannedUrlSelectorForDisplay').value;
    document.getElementById('scannedUrlSelectorForDisplay').value = scanned_url_id;
    const displayedDocumentation = document.getElementById('scannedUrlDisplay');

    if (scanned_url_id == 0) {
        displayedDocumentation.textContent = '';
        return;
    }

    try {
        const response = await fetch(`/scanned_url?scanned_url_id=${scanned_url_id}`, {
            method: 'POST'
        });
        const data = await response.json();
        displayedDocumentation.textContent = data;
    } catch (error) {
        console.error(error);
    }
})

document.getElementById('displayScannedUrlBtn').addEventListener('click', () => {
    const scannedUrlSelectorForDisplay = document.getElementById('scannedUrlSelectorForDisplay');
    const scanned_url_id = scannedUrlSelectorForDisplay.value;
    const scanned_url = scannedUrlSelectorForDisplay.options[scannedUrlSelectorForDisplay.selectedIndex].text;

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

document.getElementById('chunkBtn').addEventListener('click', async () => {
    const scanSelectorForChunk = document.getElementById('scanSelectorForChunk');
    const scanId = scanSelectorForChunk.value;
    const chunkStatus = document.getElementById('chunkStatus');
    const chunkBtn = document.getElementById('chunkBtn');
    
    if (scanId == 0) {
        chunkStatus.textContent = 'Please select a scan';
        return;
    }
    
    chunkBtn.disabled = true;
    chunkStatus.textContent = 'chunking documentation…';
    
    try {
        const response = await fetch(`/perform_chunk?scan_id=${scanId}`, {
            method: 'POST'
        });
        const data = await response.json();
        chunkStatus.textContent = data.message;
    } catch (error) {
        chunkStatus.textContent = 'Error chunking documentation';
        console.error(error);
    } finally {
        chunkBtn.disabled = false;
    }
});

document.getElementById('submitBtn').addEventListener('click', async () => {
    const query = document.getElementById('query').value;
    const loading = document.getElementById('loading');
    const response = document.getElementById('response');
    const submitBtn = document.getElementById('submitBtn');
    
    if (!query) return;
    
    loading.style.display = 'block';
    response.innerHTML = '';
    submitBtn.disabled = true;
    
    try {
        const res = await fetch('/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query })
        });
        
        const data = await res.json();
        
        response.innerHTML = `
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
        response.innerHTML = '<div class="alert alert-danger">Error getting response</div>';
        console.error(error);
    } finally {
        loading.style.display = 'none';
        submitBtn.disabled = false;
    }
});

// Event listener for the scan selector in the View Chunks section
document.getElementById('scanSelectorForViewChunk').addEventListener('input', async () => {
    const scan_id = document.getElementById('scanSelectorForViewChunk').value;
    const scannedUrlSelectorForViewChunk = document.getElementById('scannedUrlSelectorForViewChunk');
    const chunkSelector = document.getElementById('chunkSelector');
    const chunkDisplay = document.getElementById('chunkDisplay');
    
    // Clear existing options except the default one
    while (scannedUrlSelectorForViewChunk.options.length > 1) {
        scannedUrlSelectorForViewChunk.remove(1);
    }
    
    // Clear chunk selector and display
    while (chunkSelector.options.length > 1) {
        chunkSelector.remove(1);
    }
    chunkDisplay.textContent = '';
    
    if (scan_id == 0) {
        return;
    }
    
    try {
        const response = await fetch(`/scanned_urls?scan_id=${scan_id}`, {
            method: 'POST'
        });
        const scannedUrls = await response.json();
        scannedUrls.forEach(url => {
            // Add to scanned URLs selector
            const scannedUrlOption = document.createElement('option');
            scannedUrlOption.value = url[0];
            scannedUrlOption.textContent = url[1];
            scannedUrlSelectorForViewChunk.appendChild(scannedUrlOption);
        });
    } catch (error) {
        console.error('Error fetching scanned URLs:', error);
    }
});

// Event listener for the scanned URL selector in the View Chunks section
document.getElementById('scannedUrlSelectorForViewChunk').addEventListener('input', async () => {
    const scan_id = document.getElementById('scanSelectorForViewChunk').value;
    const scannedUrlId = document.getElementById('scannedUrlSelectorForViewChunk').value;
    const chunkSelector = document.getElementById('chunkSelector');
    const chunkDisplay = document.getElementById('chunkDisplay');
    
    // Clear existing options except the default one
    while (chunkSelector.options.length > 1) {
        chunkSelector.remove(1);
    }
    chunkDisplay.textContent = '';
    
    if (scannedUrlId == 0) {
        return;
    }
    
    try {
        const response = await fetch(`/chunks?scanned_url_id=${scannedUrlId}`, {
            method: 'POST'
        });
        const chunks = await response.json();
        
        chunks.forEach(chunk => {
            const chunkOption = document.createElement('option');
            chunkOption.value = chunk;
            chunkOption.textContent = `Chunk ${chunk}`;
            chunkSelector.appendChild(chunkOption);
        });
    } catch (error) {
        console.error('Error fetching chunks:', error);
    }
});

// Event listener for the chunk selector
document.getElementById('chunkSelector').addEventListener('input', async () => {
    const chunkId = document.getElementById('chunkSelector').value;
    const chunkDisplay = document.getElementById('chunkDisplay');
    
    if (chunkId == 0) {
        chunkDisplay.textContent = '';
        return;
    }
    
    try {
        const response = await fetch(`/chunk_content?chunk_id=${chunkId}`, {
            method: 'POST'
        });
        const data = await response.json();
        chunkDisplay.textContent = data.text;
    } catch (error) {
        console.error('Error fetching chunk content:', error);
        chunkDisplay.textContent = 'Error loading chunk content';
    }
});
