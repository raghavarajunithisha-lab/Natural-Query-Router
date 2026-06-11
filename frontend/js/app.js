document.addEventListener('DOMContentLoaded', () => {
    // Handle switching between the different navigation panels
    const tabs = document.querySelectorAll('.tab');
    const panels = document.querySelectorAll('.panel');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            panels.forEach(p => p.classList.remove('active'));
            
            tab.classList.add('active');
            document.getElementById(tab.dataset.target).classList.add('active');
        });
    });

    // Set up the Natural Language Search input and rendering logic
    const nlqInput = document.getElementById('nlq-input');
    const nlqSubmit = document.getElementById('nlq-submit');
    const nlqLoading = document.getElementById('nlq-loading');
    const nlqResults = document.getElementById('nlq-results');

    const renderResults = (results) => {
        nlqResults.innerHTML = '';
        if (!results || results.length === 0) {
            nlqResults.innerHTML = '<p>No results found for this query.</p>';
            return;
        }

        results.forEach(item => {
            const card = document.createElement('div');
            card.className = 'glass-card';
            
            let title = 'Result';
            let desc = '';
            let acc = '';
            let url = '#';

            if (item.primaryAccession) {
                // Extract UniProt (Protein) data into a clean card format
                acc = item.primaryAccession;
                title = item.proteinDescription?.recommendedName?.fullName?.value || item.uniProtkbId || 'Protein';
                desc = item.genes?.[0]?.geneName?.value ? `Gene: ${item.genes[0].geneName.value}` : '';
                if (item.organism?.scientificName) desc += ` (${item.organism.scientificName})`;
                url = `https://www.uniprot.org/uniprotkb/${acc}/entry`;
            } else if (item.title || item.pmid) {
                // Extract Europe PMC (Literature) metadata
                let itemId = item.id || item.pmid;
                let src = item.source || 'MED'; // MED, PPR, PMC, etc.
                acc = `${src}: ${itemId}`;
                title = item.title || 'Publication';
                desc = item.abstractText || 'No abstract available.';
                url = `https://europepmc.org/article/${src}/${itemId}`;
            } else if (item.object_type === "Gene" || item.species) {
                // Extract Ensembl (Gene) data from the API response
                acc = item.id;
                title = item.display_name || item.id;
                desc = item.description || `Species: ${item.species}`;
                url = `https://www.ensembl.org/id/${acc}`;
            } else if (item.source) {
                // Handle generic EBI search results
                acc = item.id;
                title = item.name || item.id;
                desc = item.description || `Source: ${item.source}`;
                if (item.source === 'ensembl_gene') {
                    url = `https://www.ensembl.org/id/${acc}`;
                } else {
                    url = `https://www.ebi.ac.uk/ebisearch/search.ebi?db=${item.source}&query=${acc}`;
                }
            } else {
                // Final catch-all for any unknown data formats
                title = item.title || item.name || item.id || 'Result';
                desc = item.abstractText || item.description || '';
                acc = item.accession || item.id || '';
            }

            card.innerHTML = `
                <a href="${url}" target="_blank" style="text-decoration: none; color: inherit; display: block; height: 100%;">
                    <h3>${title}</h3>
                    <p><strong>ID/Accession:</strong> ${acc}</p>
                    <p>${desc.toString().substring(0, 100)}...</p>
                </a>
            `;
            nlqResults.appendChild(card);
        });
    };

    const performSearch = async () => {
        const query = nlqInput.value.trim();
        if (!query) return;

        nlqResults.innerHTML = '';
        nlqLoading.classList.remove('hidden');

        try {
            const response = await fetch('/api/search', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query })
            });
            const data = await response.json();
            nlqLoading.classList.add('hidden');
            renderResults(data.results);
        } catch (error) {
            nlqLoading.classList.add('hidden');
            nlqResults.innerHTML = `<p style="color:#ef4444;">Error performing search: ${error.message}</p>`;
        }
    };

    nlqSubmit.addEventListener('click', performSearch);
    nlqInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') performSearch();
    });

    // Set up the BLAST Sequence Alignment submission form and status polling
    const blastInput = document.getElementById('blast-input');
    const blastProgram = document.getElementById('blast-program');
    const blastSubmit = document.getElementById('blast-submit');
    const blastStatusArea = document.getElementById('blast-status-area');
    const blastStatusText = document.getElementById('blast-status-text');
    const blastJobIdText = document.getElementById('blast-job-id');
    const blastResultsArea = document.getElementById('blast-results-area');
    const blastResultsContent = document.getElementById('blast-results-content');

    const pollBlastStatus = async (jobId) => {
        try {
            const res = await fetch(`/api/blast/status/${jobId}`);
            const data = await res.json();
            
            blastStatusText.textContent = `Status: ${data.status}`;
            
            if (data.status === 'RUNNING' || data.status === 'PENDING') {
                setTimeout(() => pollBlastStatus(jobId), 3000);
            } else if (data.status === 'FINISHED') {
                const resResult = await fetch(`/api/blast/results/${jobId}`);
                const resultData = await resResult.json();
                blastStatusArea.classList.add('hidden');
                blastResultsArea.classList.remove('hidden');
                blastResultsContent.textContent = resultData.results;
            } else {
                blastStatusText.textContent = `Status: ${data.status} (Failed or Not Found)`;
                document.querySelector('.status-indicator .spinner').classList.add('hidden');
            }
        } catch (error) {
            blastStatusText.textContent = "Error checking status.";
        }
    };

    blastSubmit.addEventListener('click', async () => {
        const seq = blastInput.value.trim();
        const prog = blastProgram.value;
        if (!seq) return;

        blastStatusArea.classList.remove('hidden');
        blastResultsArea.classList.add('hidden');
        blastStatusText.textContent = "Submitting job...";
        blastJobIdText.textContent = "";
        
        // Show spinner
        const spinner = document.querySelector('.status-indicator .spinner');
        if (spinner) spinner.classList.remove('hidden');

        try {
            const response = await fetch('/api/blast/submit', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ sequence: seq, program: prog })
            });
            const data = await response.json();
            
            blastJobIdText.textContent = `Job ID: ${data.job_id}`;
            pollBlastStatus(data.job_id);
            
        } catch (error) {
            blastStatusText.textContent = "Failed to submit job.";
            if (spinner) spinner.classList.add('hidden');
        }
    });

    // Demo panel to show how AI Agents invoke the underlying MCP tools
    const mcpTestBtn = document.getElementById('mcp-test-btn');
    const mcpToolSelect = document.getElementById('mcp-tool-select');
    const mcpQueryInput = document.getElementById('mcp-query');
    const mcpOutput = document.getElementById('mcp-output');

    mcpTestBtn.addEventListener('click', async () => {
        const tool = mcpToolSelect.value;
        const query = mcpQueryInput.value.trim();
        if(!query) return;

        mcpOutput.textContent = "Simulating MCP client call to backend (via API shortcut for demo)...";
        
        try {
            // Note: In a real MCP setup, the AI agent calls the MCP server.
            // For UI demo purposes, we reuse the FastAPI endpoint or mock a call.
            const response = await fetch('/api/search', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: query })
            });
            const data = await response.json();
            mcpOutput.textContent = JSON.stringify(data, null, 2);
        } catch (error) {
            mcpOutput.textContent = "Error: " + error.message;
        }
    });
});
