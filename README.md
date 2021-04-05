# blob_exporter
SQLite Blob Exporter

Python script to export blob data from an SQLite database

Exported blob data filename includes reference to the database file, table, field, and rowID where the blob data was located.

Currently, only binary blob data is exported and blob data from all tables/blob fields.

Sometimes, the contents of blob data is pretty straightforward, such as an image or text file.
Other times, there may be padding before the file contents or multiple files clumped together in a single blob.

This script will dump out the data and can be used in conjunction with the plist_carver script (https://github.com/pug4N6/plist_carver) for carving plist files from the exported blobs. Having the table, field, and rowID included in the exported files provides a reference point if relevant data is identified in an exported blob.
