# blob_exporter
A python script to export SQLite blob data.

Exported blob data filename includes reference to the database file, table, field, and rowID where the blob data was located.

Currently, only binary blob data is exported and blob data from all tables/blob fields.

Change Log

Alpha 0.1 : Initial GitHub release

Alpha 0.2 : Added select table/field option, fixed typos, cleaned up code 

Sometimes, the contents of blob data is pretty straightforward, such as an image or text file.
Other times, there may be padding before the file contents or multiple files clumped together in a single blob.

This script will dump out the data and can be used in conjunction with the plist_carver script (https://github.com/pug4N6/plist_carver) to carve plist files from the exported blobs. Having the table, field, and rowID included in the exported files provides a reference point if relevant data is identified in an exported blob.
