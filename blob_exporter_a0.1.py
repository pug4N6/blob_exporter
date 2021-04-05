import sqlite3
import os
from datetime import datetime
import argparse

"""

Roadmap:
Handle multiple database files as an input
Output blob content other than binary-type data
Improve error-handling and report details
Allow specifying specific table and/or field for exporting

"""

def create_db_connection():

    conn = None

    try:

        conn = sqlite3.connect(input_db)

    except Exception as e:

        report_file.write(f"Error connecting to database: {e}")
        print(f"Error connecting to database (see report for details)")

    return conn

def create_table_list(conn):

    table_list = []

    try:

        cursor = conn.cursor()

        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table';")

        table_list = cursor.fetchall()

    except Exception as e:

        report_file.write(f"Error reading database tables: {e}")
        print(f"ERROR: Reading database tables was unsuccessful (see report for details)")

    return table_list

def create_blob_list(conn, table_list):

    table_blob_list = []

    try:

        for i in table_list:

            table_name = i[0]

            query = f"pragma table_info('{table_name}');"

            cursor = conn.cursor()

            cursor.execute(query)

            column_list = cursor.fetchall()

            blob_columns = []

            for column in column_list:

                if column[2] == "BLOB":

                    blob_columns.append(column[1])

            if blob_columns != []:

                table_blob_list.append([table_name, blob_columns])

    except Exception as e:

        report_file.write(f"Error identifying blob data: {e}")
        print(f"ERROR: Identifying blob data was unsuccessful (see report for details)")

    return table_blob_list

def export_blobs(conn, table_blob_list):

    global carved_blobs
    global skipped_blobs

    for i in table_blob_list:

        for x in i[1]:

            query = f"SELECT ROWID, \"{x}\" FROM \"{i[0]}\" WHERE \"{x}\" <> \"\";"

            cursor = conn.cursor()

            cursor.execute(query)

            rows = cursor.fetchone()

            while rows:

                process_item = os.path.basename(input_db)

                blob_type = type(rows[1]).__name__

                if isinstance(rows[1], bytes):

                    export_name = f"db_{process_item}__tbl_{i[0]}__col_{x}_ROWID_{rows[0]}"

                    export_blob = os.path.join(output_paths, export_name)

                    outputfile = open(export_blob, "wb")

                    outputfile.write(bytes(rows[1]))

                    outputfile.close()

                    carved_blobs += 1

                # elif isinstance(rows[1], str):

                #    outputfile.write(bytes(rows[1], encoding="utf8"))

                else:

                    report_file.write(f"\nDatabase: {input_db} -- Table: {i[0]} -- "
                                      f"Column: {x} -- ROWID: {rows[0]} -- "
                                      f"Blob data identified as {blob_type}, not binary data")

                    skipped_blobs += 1

                rows = cursor.fetchone()

def report_finish():

    report_file.write(f"\n\nInput database: {input_db}")
    report_file.write(f"\nStart time: {start_time_report}")

    end_time = datetime.now()
    end_time_report = end_time.strftime(time_format_report)

    report_file.write(f"\nEnd time: {end_time_report}")

    report_file.write(f"\nCarved blobs: {carved_blobs}")
    report_file.write(f"\nSkipped blobs: {skipped_blobs}")

def main():

    if os.path.exists(input_db):

        conn = create_db_connection()

    else:

        conn = None

        print(f"Error locating database: {input_db}")
        report_file.write(f"ERROR: Database {input_db} could not be located")

    if conn != None:

        table_list = create_table_list(conn)

    else:

        table_list = []

    if table_list != []:

        table_blob_list = create_blob_list(conn, table_list)

    else:

        table_blob_list = []

    if table_blob_list != []:

        export_blobs(conn, table_blob_list)

if __name__ == '__main__':

    time_format_filename = "%Y%m%d_%H%M%S"
    time_format_report = "%Y-%m-%d_%H:%M:%S"
    version = "alpha0.1 (2021)"
    email = "pug4n6@gmail.com"
    start_time = datetime.now()
    start_time_report = start_time.strftime(time_format_report)
    output_folder = "blob_exporter_output"
    report_folder = output_folder + "/blob_exporter_" + start_time.strftime(time_format_filename)
    export_folder = "carved_files"
    output_paths = os.path.join(report_folder, export_folder)
    report_filename = "report.txt"
    report_file_path = os.path.join(report_folder, report_filename)

    carved_blobs = 0
    skipped_blobs = 0

    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                     description=f"SQLite Blob Exporter version {version}"
                                                 f"\n\nNOTE: Output filenames include database name, table, column, and rowID")
    parser.add_argument("-i", dest="input_db", required=True, action="store", help="Input database file (required)")

    args = parser.parse_args()
    input_db = f"{args.input_db}"

    if not os.path.exists(output_paths):

        os.makedirs(output_paths)

    if not os.path.exists(report_file_path):

        report_file = open(report_file_path, "w+")

        report_file.write(f"SQLite Database Blob Exporter version {version}\n")

    main()

    report_finish()