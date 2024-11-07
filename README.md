# Quark Apps Server (QAS)

The Quark Apps Server was designed as a simple approach to a convoluted problem. Distributing apps throughout an organization can be difficult.

To resolve this, the Quark Apps Server set out to develop an easy way for administrators to log in, upload files, and retrieve a download link for each file.

Then, a system administrator can use either their favorite MDM or scripting language to pull down the file, verify the SHA256/MD5 checksum if required, and install the app on the client device.


## The Design

### Client
Using a simple, elegant HTML and CSS frontend, users or administrators can see the available apps on the server, as well as their size, version, and date uploaded.

### Admin Panel
The admin panel is a separate UI that should have access restricted via any means that the implementing systems administrator desires. The recommended way is by restricting access via VLANs


## The API

To make this possible, we needed to create a simple API that allows administrators to pull down the MD5 or SHA256 checksum on a device, dynamically, allowing for new versions of a file to be uploaded, without causing issues on client devices.

To achieve this, after the web server receives a request from a client asking for the file checksum, the Python backend will communicate with the MySQL database holding information about the files. The server will then respond with the appropriate MD5 or SHA256 hash value, allowing for file integrity checking on the client.

Example: `curl -o https://apps.mydomain.com/api/md5/file`

Example: `curl -o https://apps.mydomain.com/api/sha256/file`

The example above will return a simple hash of the file located at the specified path.