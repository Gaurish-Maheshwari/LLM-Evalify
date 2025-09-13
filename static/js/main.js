document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('evaluation-form');
    const submitBtn = document.getElementById('submit-btn');
    const loader = document.getElementById('loader');
    const resultsContainer = document.getElementById('results-container');
    const errorContainer = document.getElementById('error-container');

    // --- NEW: Global variable to hold the chart instance ---
    let myChart = null;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const prompt = document.getElementById('prompt').value.trim();
        const response = document.getElementById('response').value.trim();

        if (!prompt || !response) {
            showError("Please fill in both the prompt and response fields.");
            return;
        }

        hideError();
        resultsContainer.classList.add('hidden');
        loader.classList.remove('hidden');
        submitBtn.disabled = true;
        submitBtn.textContent = 'Evaluating...';

        try {
            const apiResponse = await fetch('/evaluate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ prompt, response }),
            });

            if (!apiResponse.ok) {
                const errorData = await apiResponse.json();
                throw new Error(errorData.error || 'Something went wrong on the server.');
            }

            const data = await apiResponse.json();
            displayResults(data);

        } catch (error) {
            console.error('Evaluation Error:', error);
            showError(error.message);
        } finally {
            loader.classList.add('hidden');
            submitBtn.disabled = false;
            submitBtn.textContent = 'Evaluate';
        }
    });

    function displayResults(data) {
        resultsContainer.classList.remove('hidden');
        
        document.getElementById('overall-score').textContent = data.overall_score;

        const detailedResultsDiv = document.getElementById('detailed-results');
        detailedResultsDiv.innerHTML = ''; 

        for (const metric in data) {
            if (metric !== 'overall_score') {
                const result = data[metric];
                const card = document.createElement('div');
                card.className = 'metric-card';
                
                const displayName = metric.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());

                // --- UPGRADE: Card now includes the evidence block ---
                card.innerHTML = `
                    <h4>${displayName}</h4>
                    <p class="score">${result.score}/10</p>
                    <p class="justification">"${result.justification}"</p>
                    <p class="evidence"><strong>Evidence:</strong> "${result.evidence}"</p>
                `;
                detailedResultsDiv.appendChild(card);
            }
        }

        // --- NEW: Code to generate the radar chart ---
        const ctx = document.getElementById('resultsChart').getContext('2d');
        const labels = Object.keys(data)
            .filter(key => key !== 'overall_score')
            .map(key => key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()));
            
        const scores = Object.keys(data)
            .filter(key => key !== 'overall_score')
            .map(key => data[key].score);

        // Destroy previous chart instance if it exists to prevent ghosting
        if (myChart) {
            myChart.destroy();
        }

        myChart = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Evaluation Score',
                    data: scores,
                    fill: true,
                    backgroundColor: 'rgba(74, 144, 226, 0.2)',
                    borderColor: 'rgb(74, 144, 226)',
                    pointBackgroundColor: 'rgb(74, 144, 226)',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: 'rgb(74, 144, 226)'
                }]
            },
            options: {
                elements: {
                    line: {
                        borderWidth: 3
                    }
                },
                scales: {
                    r: {
                        angleLines: {
                            display: true
                        },
                        suggestedMin: 0,
                        suggestedMax: 10,
                        ticks: {
                           stepSize: 2
                        }
                    }
                }
            }
        });
    }
    
    function showError(message) {
        errorContainer.textContent = message;
        errorContainer.classList.remove('hidden');
    }

    function hideError() {
        errorContainer.classList.add('hidden');
    }
});