document.addEventListener('DOMContentLoaded', function() {
    var matchweekSelect = document.getElementById('matchweek-select');
    
    matchweekSelect.addEventListener('change', function() {
        var selectedWeek = parseInt(this.value);
        console.log('Selected week:', selectedWeek);
        // Call your algorithm function here, passing the selectedWeek as an argument
    });
});