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
                
                /* Create a link to the app's download page */
                const link = document.createElement('a');
                link.href = `/apps/${app.filename}`;
                link.textContent = app.app_name;
                link.setAttribute('download', app.filename); // Ensure it is always a download link
                row.insertCell(1).appendChild(link);
                
                /* Add the app version and MD5 hash */
                row.insertCell(2).textContent = app.app_version;
                row.insertCell(3).textContent = app.md5_hash;

                /* Format the last updated date */
                const lastUpdated = new Date(app.last_updated);
                const formattedDate = lastUpdated.toLocaleString('en-US', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                });
                row.insertCell(4).textContent = formattedDate;
            });
        })
        .catch(error => console.error('Error fetching data:', error));
});