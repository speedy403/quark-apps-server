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
                
                /* Add the app version, SHA256, and MD5 hash */
                row.insertCell(2).textContent = app.app_version;
                

                /* Requires HTTPS to work */
                // const sha256Cell = row.insertCell(3);
                // const sha256Link = document.createElement('a');
                // sha256Link.href = '#';
                // sha256Link.textContent = 'Copy';
                // sha256Link.addEventListener('click', (event) => {
                //     event.preventDefault();
                //     navigator.clipboard.writeText(app.sha256_hash);
                // });
                // sha256Cell.appendChild(sha256Link);

                // const md5Cell = row.insertCell(4);
                // const md5Link = document.createElement('a');
                // md5Link.href = '#';
                // md5Link.textContent = 'Copy';
                // md5Link.addEventListener('click', (event) => {
                //     event.preventDefault();
                //     navigator.clipboard.writeText(app.md5_hash);
                // });
                // md5Cell.appendChild(md5Link);

                /* Use if HTTPS is not available */
                const sha256Cell = row.insertCell(3);
                const sha256Text = document.createElement('span');
                sha256Text.textContent = app.sha256_hash;
                sha256Text.style.whiteSpace = 'nowrap';
                sha256Text.style.overflow = 'hidden';
                sha256Text.style.textOverflow = 'ellipsis';
                sha256Cell.appendChild(sha256Text);

                const md5Cell = row.insertCell(4);
                const md5Text = document.createElement('span');
                md5Text.textContent = app.md5_hash;
                md5Text.style.whiteSpace = 'nowrap';
                md5Text.style.overflow = 'hidden';
                md5Text.style.textOverflow = 'ellipsis';
                md5Cell.appendChild(md5Text);

                /* Add the app filesize */
                filesize = app.filesize
                if (filesize < 1024) {
                    filesize = filesize + " B";
                } else if (filesize < 1048576) {
                    filesize = (filesize / 1024).toFixed(2) + " KB";
                } else if (filesize < 1073741824) {
                    filesize = (filesize / 1048576).toFixed(2) + " MB";
                } else {
                    filesize = (filesize / 1073741824).toFixed(2) + " GB";
                }
                row.insertCell(5).textContent = filesize;

                /* Format the last updated date */
                const lastUpdated = new Date(app.last_updated);
                const formattedDate = lastUpdated.toLocaleString('en-US', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                });
                row.insertCell(6).textContent = formattedDate;

                // Add the sums, update, edit, and delete buttons
                const sumsCell = row.insertCell(7);
                const sumsLink = document.createElement('a');
                sumsLink.href = `/admin/sums/${app.app_id}`;
                sumsLink.textContent = 'Recalc';
                sumsCell.appendChild(sumsLink);

                const updateCell = row.insertCell(8);
                const updateLink = document.createElement('a');
                updateLink.href = `/admin/update/${app.app_id}`;
                updateLink.textContent = 'Update';
                updateCell.appendChild(updateLink);
            
                const editCell = row.insertCell(9);
                const editLink = document.createElement('a');
                editLink.href = `/admin/edit/${app.app_id}`;
                editLink.textContent = 'Edit';
                editCell.appendChild(editLink);

                const deleteCell = row.insertCell(10);
                const deleteLink = document.createElement('a');
                deleteLink.href = `/admin/delete/${app.app_id}`;
                deleteLink.textContent = 'Delete';
                deleteCell.appendChild(deleteLink);

            });
        })
        .catch(error => console.error('Error fetching data:', error));
});