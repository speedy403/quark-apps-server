// Ensure content is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Contact the Flask App search API
    fetch('/api/db_reader')
        .then(response => response.json())
        .then(data => {
            // Construct a table with the data
            const table = document.getElementById('apps-table');

            // Create a row for each app in the data
            data.forEach(app => {
                // Create a row for each app in the data
                const row = table.insertRow();

                // Insert cells for each attribute of the app
                row.insertCell(0).textContent = app.app_id;
                row.insertCell(1).textContent = app.app_name;
                row.insertCell(2).textContent = app.app_version;
                row.insertCell(3).textContent = app.md5_hash;
            });
        })
        .catch(error => console.error('Error fetching data:', error));
});