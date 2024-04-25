// document.addEventListener('DOMContentLoaded', function() {
//     var matchweekSelect = document.getElementById('matchweek-select');
//     var resultContainer = document.getElementById('result-container');
    
//     matchweekSelect.addEventListener('change', function() {
//         var selectedWeek = parseInt(this.value);
        
//         // Make an API request to the Python script
//         fetch('/predict?matchweek=' + selectedWeek)
//             .then(response => response.json())
//             .then(data => {
//                 // Display the resulting dataframe in the result container
//                 resultContainer.textContent = JSON.stringify(data, null, 2);
//             })
//             .catch(error => {
//                 console.error('Error:', error);
//             });
//     });
// });

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
                    
                    var homeTeam = document.createElement('span');
                    homeTeam.textContent = match.homeTeamName;
                    
                    var awayTeam = document.createElement('span');
                    awayTeam.textContent = match.awayTeamName;
                    
                    var homeConfidence = document.createElement('span');
                    homeConfidence.textContent = 'Home Confidence: ' + (match.home_confidence*100).toFixed(2) + '%';

                    var awayConfidence = document.createElement('span');
                    awayConfidence.textContent = 'Away Confidence: ' + (match.away_confidence*100).toFixed(2) + '%';

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