document.addEventListener('DOMContentLoaded', function() {
    var matchweekSelect = document.getElementById('matchweek-select');
    var resultContainer = document.getElementById('result-container');
    
    matchweekSelect.addEventListener('change', function() {
        var selectedWeek = parseInt(this.value);
        
        // Make an API request to the Python script
        fetch('/predict?matchweek=' + selectedWeek)
            .then(response => response.json())
            .then(data => {
                // Clear the previous result
                resultContainer.innerHTML = '';
                
                // Loop through the data and create elements for each match
                data.forEach(match => {
                    var matchDiv = document.createElement('div');
                    matchDiv.classList.add('match');
                    
                    var predictionContainer = document.createElement('div');
                    predictionContainer.classList.add('prediction-container');
                    
                    var matchInfo = document.createElement('div');
                    matchInfo.classList.add('match-info');
                    
                    var homeTeam = document.createElement('span');
                    homeTeam.classList.add('team');
                    homeTeam.textContent = match.homeTeamName;
                    
                    var vsText = document.createElement('span');
                    vsText.classList.add('vs');
                    vsText.textContent = 'vs';
                    
                    var awayTeam = document.createElement('span');
                    awayTeam.classList.add('team');
                    awayTeam.textContent = match.awayTeamName;
                    
                    matchInfo.appendChild(homeTeam);
                    matchInfo.appendChild(vsText);
                    matchInfo.appendChild(awayTeam);
                    
                    var confidenceDiv = document.createElement('div');
                    confidenceDiv.classList.add('confidence');
                    
                    var homeConfidence = document.createElement('span');
                    homeConfidence.classList.add('confidence-value');
                    homeConfidence.textContent = match.home_confidence + '%';
                    
                    var awayConfidence = document.createElement('span');
                    awayConfidence.classList.add('confidence-value');
                    awayConfidence.textContent = match.away_confidence + '%';
                    
                    if (match.home_confidence > match.away_confidence) {
                        homeConfidence.classList.add('higher-confidence');
                        awayConfidence.classList.add('lower-confidence');
                    } else {
                        homeConfidence.classList.add('lower-confidence');
                        awayConfidence.classList.add('higher-confidence');
                    }
                    
                    confidenceDiv.appendChild(homeConfidence);
                    confidenceDiv.appendChild(awayConfidence);
                    
                    predictionContainer.appendChild(matchInfo);
                    predictionContainer.appendChild(confidenceDiv);
                    
                    matchDiv.appendChild(predictionContainer);
                    
                    resultContainer.appendChild(matchDiv);
                });
            })
            .catch(error => {
                console.error('Error:', error);
            });
    });
});