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
                    console.log("Match Data:", match);

                    var matchDiv = document.createElement('div');
                    matchDiv.classList.add('match');
                    
                    var homeTeam = document.createElement('span');
                    homeTeam.textContent = match.homeTeamName;
                    
                    var awayTeam = document.createElement('span');
                    awayTeam.textContent = match.awayTeamName;
                    
                    var homeConfidence = document.createElement('span');
                    homeConfidence.textContent = 'Home Confidence: ' + match.home_confidence + '%';

                    var awayConfidence = document.createElement('span');
                    awayConfidence.textContent = 'Away Confidence: ' + match.away_confidence + '%';




                    matchDiv.appendChild(homeTeam);
                    matchDiv.appendChild(document.createTextNode(' vs '));
                    matchDiv.appendChild(awayTeam);
                    matchDiv.appendChild(document.createElement('br'));
                    matchDiv.appendChild(homeConfidence);
                    matchDiv.appendChild(document.createElement('br'));
                    matchDiv.appendChild(awayConfidence);
                    
                    resultContainer.appendChild(matchDiv);
                    resultContainer.appendChild(document.createElement('hr'));
                });
            })
            .catch(error => {
                console.error('Error:', error);
            });
    });
});