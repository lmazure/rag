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
    
    // Clear existing options except the default one
    while (scanSelectorForChunk.options.length > 1) {
        scanSelectorForChunk.remove(1);
    }
    
    while (scanSelectorForDisplay.options.length > 1) {
        scanSelectorForDisplay.remove(1);
    }
    
    try {
        const response = await fetch('/scans');
        const scans = await response.json();
        scans.forEach(scan => {
            // Add to chunk selector
            const chunkOption = document.createElement('option');
            chunkOption.value = scan[0];
            chunkOption.textContent = scan[1] + " - " + scan[2];
            scanSelectorForChunk.appendChild(chunkOption);
            
            // Add to display selector
            const displayOption = document.createElement('option');
            displayOption.value = scan[0];
            displayOption.textContent = scan[1] + " - " + scan[2];
            scanSelectorForDisplay.appendChild(displayOption);
        });
    } catch (error) {
        console.error('Error fetching scans:', error);
    }
}

// Load scans when the page loads
document.addEventListener('DOMContentLoaded', loadScans);

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
        const response = await fetch(`/chunk?scan_id=${scanId}`, {
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
