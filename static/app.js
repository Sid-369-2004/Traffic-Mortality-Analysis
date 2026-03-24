document.addEventListener('DOMContentLoaded', async () => {
    Chart.defaults.color = '#475569';
    Chart.defaults.font.family = "'Inter', sans-serif";
    Chart.defaults.scale.grid.color = '#e2e8f0';

    // --- 2. ANALYTICS PAGE LOGIC ---
    const metricsDataEl = document.getElementById('metrics-data');
    if (metricsDataEl) {
        try {
            const data = JSON.parse(metricsDataEl.textContent);
            // Rank exactly as provided in the array (We know MLP is always top ranking)
            const models = ["MLP_Neural_Net", "Decision_Tree", "SVM"];
            
            const labels = ["MLP Neural Network", "Decision Tree", "SVM"];
            const accuracies = models.map(m => data[m].Accuracy);
            const precisions = models.map(m => data[m].Precision);
            const recalls = models.map(m => data[m].Recall);
            const f1s = models.map(m => data[m].F1_Score);

            const ctxAcc = document.getElementById('accuracyChart').getContext('2d');
            new Chart(ctxAcc, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Accuracy (%)',
                        data: accuracies,
                        backgroundColor: ['#2563eb', '#94a3b8', '#94a3b8'],
                        borderRadius: 4
                    }]
                },
                options: { 
                    responsive: true, 
                    maintainAspectRatio: false,
                    scales: { x: { ticks: { maxRotation: 0, minRotation: 0, font: { weight: '600' } } } }
                }
            });

            const ctxMulti = document.getElementById('multiMetricChart').getContext('2d');
            new Chart(ctxMulti, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [
                        { label: 'Precision', data: precisions, backgroundColor: '#3b82f6', borderRadius: 2 },
                        { label: 'Recall', data: recalls, backgroundColor: '#8b5cf6', borderRadius: 2 },
                        { label: 'F1-Score', data: f1s, backgroundColor: '#10b981', borderRadius: 2 }
                    ]
                },
                options: { 
                    responsive: true, 
                    maintainAspectRatio: false,
                    scales: { x: { ticks: { maxRotation: 0, minRotation: 0, font: { weight: '600' } } } }
                }
            });
        } catch(e) {
            console.error(e);
        }
    }

    // --- 3. PREDICTOR PAGE LOGIC ---
    const form = document.getElementById('prediction-form');
    if(form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const btn = document.getElementById('predictBtn');
            const resultBox = document.getElementById('resultBox');
            const dynamicUI = document.getElementById('dynamicPredictionUI');
            
            btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Processing...';
            btn.disabled = true;

            const payload = {
                "Start_Lat": parseFloat(document.getElementById('Start_Lat').value),
                "Start_Lng": parseFloat(document.getElementById('Start_Lng').value),
                "Temperature(F)": parseFloat(document.getElementById('Temperature').value),
                "Humidity(%)": parseFloat(document.getElementById('Humidity').value),
                "Pressure(in)": parseFloat(document.getElementById('Pressure').value),
                "Visibility(mi)": parseFloat(document.getElementById('Visibility').value),
                "Wind_Speed(mph)": parseFloat(document.getElementById('WindSpeed').value),
                "Sunrise_Sunset": document.getElementById('SunriseSunset').value,
                "Crossing": document.getElementById('Crossing').checked ? 1.0 : 0.0,
                "Junction": document.getElementById('Junction').checked ? 1.0 : 0.0,
                "Traffic_Signal": document.getElementById('TrafficSignal').checked ? 1.0 : 0.0
            };

            try {
                const res = await fetch('/api/predict', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                
                resultBox.className = 'result-box';
                
                if (data.status === 'success') {
                    if(data.prediction.includes("Severe")) {
                        resultBox.classList.add('severe-result');
                    } else {
                        resultBox.classList.add('non-severe-result');
                    }
                    
                    // Show standard result
                    resultBox.querySelector('.status-title').innerText = data.prediction;
                    resultBox.querySelector('.result-reason').innerText = "Inference Complete. Parsing analytics...";
                    
                    // Display hidden UI
                    dynamicUI.style.display = 'block';
                    document.getElementById('dynReason').innerText = data.reason;
                    
                    const safeColor = '#16a34a';
                    const alertColor = '#b91c1c';

                    // 1. Doughnut Chart
                    const oldConf = Chart.getChart("confidenceChart");
                    if(oldConf) oldConf.destroy();
                    new Chart(document.getElementById('confidenceChart').getContext('2d'), {
                        type: 'doughnut',
                        data: {
                            labels: ['Non-Severe', 'Severe'],
                            datasets: [{ data: [data.confidence.safe, data.confidence.severe], backgroundColor: [safeColor, alertColor], borderWidth: 0 }]
                        },
                        options: { responsive: true, maintainAspectRatio: false, cutout: '70%', plugins: { legend: { position: 'right'} } }
                    });

                    // 2. Dynamic Table Injection
                    const tbody = document.getElementById('dynamicModelTable');
                    const mList = ["MLP_Neural_Net", "Decision_Tree", "SVM"];
                    tbody.innerHTML = '';
                    mList.forEach((m, idx) => {
                        const mData = data.models[m];
                        const name = m === "MLP_Neural_Net" ? "MLP Neural Network 👑" : m.replace('_', ' ');
                        const row = `<tr style="border-bottom: 1px solid var(--border-color); ${idx===0 ? 'background: rgba(0, 94, 162, 0.05);' : ''}">
                            <td style="padding: 0.75rem; color: var(--primary); font-weight: 600; vertical-align: middle;">${name}</td>
                            <td style="padding: 0.75rem; vertical-align: middle;">
                                <div style="display: flex; flex-direction: column; gap: 4px;">
                                    <span>${mData.Accuracy}%</span>
                                    <div class="progress-bar" style="height: 4px;"><div class="progress-fill safe" style="width: ${mData.Accuracy}%;"></div></div>
                                </div>
                            </td>
                            <td style="padding: 0.75rem; vertical-align: middle;">
                                <div style="display: flex; flex-direction: column; gap: 4px;">
                                    <span>${mData.Precision}%</span>
                                    <div class="progress-bar" style="height: 4px;"><div class="progress-fill" style="width: ${mData.Precision}%;"></div></div>
                                </div>
                            </td>
                            <td style="padding: 0.75rem; vertical-align: middle;">
                                <div style="display: flex; flex-direction: column; gap: 4px;">
                                    <span>${mData.Recall}%</span>
                                    <div class="progress-bar" style="height: 4px;"><div class="progress-fill warn" style="width: ${mData.Recall}%;"></div></div>
                                </div>
                            </td>
                            <td style="padding: 0.75rem; vertical-align: middle;">
                                <div style="display: flex; flex-direction: column; gap: 4px;">
                                    <span>${mData.F1_Score}%</span>
                                    <div class="progress-bar" style="height: 4px;"><div class="progress-fill" style="width: ${mData.F1_Score}%;"></div></div>
                                </div>
                            </td>
                        </tr>`;
                        tbody.innerHTML += row;
                    });

                    // 3. Live Bar Charts
                    const labels = ["MLP", "Dec Tree", "SVM"];
                    const accs = mList.map(m => data.models[m].Accuracy);
                    const precs = mList.map(m => data.models[m].Precision);
                    const recs = mList.map(m => data.models[m].Recall);

                    const oldBar = Chart.getChart("liveBarChart");
                    if(oldBar) oldBar.destroy();
                    new Chart(document.getElementById('liveBarChart').getContext('2d'), {
                        type: 'bar',
                        data: { labels: labels, datasets: [{ label: 'Accuracy', data: accs, backgroundColor: ['#2563eb', '#94a3b8', '#94a3b8'], borderRadius: 3 }] },
                        options: { responsive: true, maintainAspectRatio: false }
                    });

                    const oldMet = Chart.getChart("liveMetricChart");
                    if(oldMet) oldMet.destroy();
                    new Chart(document.getElementById('liveMetricChart').getContext('2d'), {
                        type: 'bar',
                        data: {
                            labels: labels,
                            datasets: [
                                { label: 'Precision', data: precs, backgroundColor: '#3b82f6', borderRadius: 2 },
                                { label: 'Recall', data: recs, backgroundColor: '#8b5cf6', borderRadius: 2 }
                            ]
                        },
                        options: { responsive: true, maintainAspectRatio: false }
                    });

                } else {
                    resultBox.classList.add('severe-result');
                    resultBox.querySelector('.status-title').innerText = "Backend Error";
                    resultBox.querySelector('.result-reason').innerText = data.error;
                    dynamicUI.style.display = 'none';
                }
            } catch(err) {
                resultBox.className = 'result-box severe-result';
                resultBox.querySelector('.status-title').innerText = "Offline";
                resultBox.querySelector('.result-reason').innerText = "Unable to route prediction through the PyBackend.";
                dynamicUI.style.display = 'none';
            } finally {
                btn.innerHTML = '<i class="fa-solid fa-bolt"></i> Analyze Risk';
                btn.disabled = false;
            }
        });
    }
});
