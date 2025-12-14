function analyzeText() {
    const text = document.getElementById('textInput').value.trim();
    const analyzeBtn = document.getElementById('analyzeBtn');
    const spinner = document.getElementById('spinner');
    
    if (!text) {
        showAlert('Пожалуйста, введите текст для анализа', 'warning');
        return;
    }
    
    analyzeBtn.disabled = true;
    spinner.classList.remove('d-none');
    document.getElementById('alertContainer').innerHTML = '';
    
    fetch('/api/analyze', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: text })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            showAlert(data.error + (data.details ? ': ' + data.details.join(', ') : ''), 'danger');
        } else {
            displayResults(data);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('Ошибка при подключении к серверу: ' + error, 'danger');
    })
    .finally(() => {
        analyzeBtn.disabled = false;
        spinner.classList.add('d-none');
    });
}

function displayResults(data) {
    document.getElementById('resultsContainer').style.display = 'block';
    document.getElementById('inputTextDisplay').textContent = data.input_text;
    
    const comparison = data.comparison;
    const results = data.individual_results;
    
    let comparisonHTML = `
        <strong>Уровень согласия между сервисами:</strong> ${comparison.agreement_level}<br>
        <strong>Средняя уверенность:</strong> ${(comparison.average_confidence * 100).toFixed(1)}%
    `;
    document.getElementById('comparisonAlert').innerHTML = comparisonHTML;
    
    let tableHTML = `
        <table class="table table-sm table-striped">
            <thead>
                <tr>
                    <th>Сервис</th>
                    <th>Тональность</th>
                    <th>Уверенность</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    comparison.results.forEach(r => {
        const confidencePercent = (r.confidence * 100).toFixed(1);
        let badge = 'secondary';
        if (r.sentiment.includes('ПОЛОЖИТЕЛЬНАЯ')) badge = 'success';
        else if (r.sentiment.includes('ОТРИЦАТЕЛЬНАЯ')) badge = 'danger';
        else badge = 'info';
        
        tableHTML += `
            <tr>
                <td>${r.service}</td>
                <td><span class="badge bg-${badge}">${r.sentiment}</span></td>
                <td>${confidencePercent}%</td>
            </tr>
        `;
    });
    
    tableHTML += `</tbody></table>`;
    document.getElementById('resultsTable').innerHTML = tableHTML;
    
    let detailedHTML = '';
    results.forEach((result, index) => {
        const sentimentLabel = comparison.results[index].sentiment;
        const confidencePercent = (result.confidence * 100).toFixed(1);
        
        detailedHTML += `
            <div class="mb-3 p-3 bg-light rounded">
                <h6>${result.service}</h6>
                <p class="mb-2">
                    <strong>Тональность:</strong> <span class="badge bg-secondary">${sentimentLabel}</span>
                </p>
                <p class="mb-0">
                    <strong>Уверенность:</strong> <div class="progress">
                        <div class="progress-bar" style="width: ${confidencePercent}%">${confidencePercent}%</div>
                    </div>
                </p>
            </div>
        `;
    });
    
    document.getElementById('detailedResults').innerHTML = detailedHTML;
    
    const conclusionText = generateConclusion(comparison, results);
    document.getElementById('conclusions').innerHTML = conclusionText;
    
    window.scrollTo({ top: document.getElementById('resultsContainer').offsetTop - 100, behavior: 'smooth' });
}

function generateConclusion(comparison, results) {
    let conclusion = '';
    
    if (comparison.agreement_level === 'ВЫСОКОЕ') {
        conclusion += '<p><strong>Сервисы показали высокое согласие.</strong> Результат анализа тональности надежен.</p>';
    } else if (comparison.agreement_level === 'СРЕДНЕЕ') {
        conclusion += '<p><strong>Сервисы показали среднее согласие.</strong> Результаты могут быть интерпретированы с осторожностью.</p>';
    } else {
        conclusion += '<p><strong>Сервисы показали низкое согласие.</strong> Результаты требуют дополнительной проверки.</p>';
    }
    
    const sentiments = new Set(comparison.results.map(r => r.sentiment));
    
    if (sentiments.size === 1) {
        const sentiment = Array.from(sentiments)[0];
        if (sentiment.includes('ПОЛОЖИТЕЛЬНАЯ')) {
            conclusion += '<p>Текст имеет <strong>положительную</strong> тональность. Автор выражает удовлетворение, одобрение или радость.</p>';
        } else if (sentiment.includes('ОТРИЦАТЕЛЬНАЯ')) {
            conclusion += '<p>Текст имеет <strong>отрицательную</strong> тональность. Автор выражает недовольство, критику или разочарование.</p>';
        } else {
            conclusion += '<p>Текст имеет <strong>нейтральную</strong> тональность. Автор излагает факты без явного выражения эмоций.</p>';
        }
    }
    
    conclusion += `<p class="text-muted small mt-3">Средняя уверенность сервисов: ${(comparison.average_confidence * 100).toFixed(1)}%</p>`;
    
    return conclusion;
}

function clearForm() {
    document.getElementById('textInput').value = '';
    document.getElementById('resultsContainer').style.display = 'none';
    document.getElementById('alertContainer').innerHTML = '';
    updateCharCount();
}

function loadDemo() {
    fetch('/api/demo')
    .then(response => response.json())
    .then(data => {
        const samples = data.demo_samples;
        const randomSample = samples[Math.floor(Math.random() * samples.length)];
        document.getElementById('textInput').value = randomSample;
        updateCharCount();
        showAlert('Пример загружен. Нажмите "Анализировать" для начала анализа.', 'info');
    })
    .catch(error => {
        console.error('Error loading demo:', error);
        showAlert('Ошибка при загрузке примера', 'danger');
    });
}

function showAlert(message, type = 'info') {
    const alertHTML = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    document.getElementById('alertContainer').innerHTML = alertHTML;
}

function checkServiceStatus() {
    fetch('/api/status')
    .then(response => response.json())
    .then(data => {
        let statusHTML = '<ul class="list-unstyled small">';
        
        Object.keys(data.services).forEach(key => {
            const service = data.services[key];
            const status = service.available ? 'Доступен' : 'Требуется конфигурация';
            const badgeClass = service.available ? 'success' : 'warning';
            
            statusHTML += `
                <li class="mb-2">
                    ${service.name}<br>
                    <span class="badge bg-${badgeClass}">${status}</span>
                </li>
            `;
        });
        
        statusHTML += '</ul>';
        document.getElementById('serviceStatus').innerHTML = statusHTML;
    })
    .catch(error => {
        console.error('Error checking status:', error);
        document.getElementById('serviceStatus').innerHTML = '<small class="text-danger">Ошибка при проверке статуса</small>';
    });
}
