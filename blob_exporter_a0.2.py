import sqlite3
import os
from datetime import datetime
import argparse

"""

Roadmap:
Handle multiple database files as an input
Output blob content other than binary-type data
Improve error-handling and report details

"""

"""

Change Log
alpha 0.1 : Initial GitHub release
alpha 0.2 : Added select table/field option, fixed typos, cleaned up code 

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

        if table_name is not None:

            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';")

        else:

            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table';")

        table_list = cursor.fetchall()

    except Exception as e:

        report_file.write(f"Error reading database tables: {e}")

        print(f"ERROR: Reading database tables was unsuccessful (see report for details)")

    return table_list


def create_blob_list(conn, table_list):

    table_blob_list = []
    blob_columns = []

    try:

        for i in table_list:

            table_names = i[0]

            if field_name is None:

                query = f"pragma table_info('{table_names}');"

                cursor = conn.cursor()

                cursor.execute(query)

                column_list = cursor.fetchall()

                blob_columns = []

                for column in column_list:

                    if column[2] == "BLOB":

                        blob_columns.append(column[1])

            elif field_name is not None:

                blob_columns = [f"{field_name}"]

            if blob_columns:

                table_blob_list.append([table_names, blob_columns])

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

                    output_file = open(export_blob, "wb")

                    output_file.write(bytes(rows[1]))

                    output_file.close()

                    carved_blobs += 1

                else:

                    report_file.write(f"\nDatabase: {process_item} -- Table: {i[0]} -- "
                                      f"Column: {x} -- ROWID: {rows[0]} -- "
                                      f"Blob data identified as {blob_type}, not binary data")

                    skipped_blobs += 1

                rows = cursor.fetchone()


def report_finish():

    report_input_db = f"Input database: {input_db}"
    report_file.write(f"\n\n{report_input_db}")
    print(report_input_db)

    if table_name:
        if field_name:
            print(f"Selected table: {table_name}\nSelected field:  {field_name}")
            report_file.write(f"\nSelected table: {table_name}\nSelected field:  {field_name}")
        else:
            print(f"Selected table: {table_name}")
            report_file.write(f"\nSelected table: {table_name}")

    report_start_time = f"Start time: {start_time_report}"
    report_file.write(f"\n{report_start_time}")
    print(report_start_time)

    end_time_report = (datetime.now()).strftime(time_format_report)
    report_end_time = f"End time: {end_time_report}"
    report_file.write(f"\n{report_end_time}")
    print(report_end_time)

    report_exported_blobs = f"Exported blobs: {carved_blobs}"
    report_file.write(f"\n{report_exported_blobs}")
    print(report_exported_blobs)

    report_skipped_blobs = f"Skipped blobs: {skipped_blobs}"
    report_file.write(f"\n{report_skipped_blobs}")
    print(report_skipped_blobs)

    print(f"Output folder: {report_folder}")

    report_file.close()


def main():

    if os.path.exists(input_db):

        conn = create_db_connection()

    else:

        conn = None

        print(f"Error locating database: {input_db}")
        report_file.write(f"ERROR: Database {input_db} could not be located")

    if conn is not None:

        table_list = create_table_list(conn)

    else:

        table_list = []

    if table_list:

        table_blob_list = create_blob_list(conn, table_list)

    else:

        table_blob_list = []

    if table_blob_list:

        export_blobs(conn, table_blob_list)

    else:

        print(f"No blob fields identified in database")
        report_file.write(f"\nERROR: No blob fields identified in database")

    conn.close()


if __name__ == '__main__':

    time_format_filename = "%Y%m%d_%H%M%S"
    time_format_report = "%Y-%m-%d_%H:%M:%S"
    version = f"alpha0.2 (2021)"
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
                                                 f"\nNOTE: Output filenames include database name, "
                                                 f"table, column, and rowID")
    parser.add_argument("-i", dest="input_db", required=True, action="store",
                        help="Input database file (required)")
    parser.add_argument("-t", dest="table_name", required=False, action="store",
                        help=f"Identify specific table for exporting (optional)")
    parser.add_argument("-f", dest="field_name", required=False, action="store",
                        help=f"Identify specific field for exporting"
                             f"\n(optional, only used if -t (table) is specified")

    args = parser.parse_args()

    input_db = f"{args.input_db}"

    if args.field_name is not None and args.table_name is None:

        print("ERROR: Cannot list a field within listing a table as well")

        exit(-1)

    if args.table_name is not None:

        table_name = f"{args.table_name}"

    else:

        table_name = None

    if (args.field_name is not None) and (table_name is not None):

        field_name = f"{args.field_name}"

    else:

        field_name = None

    if not os.path.exists(output_paths):

        os.makedirs(output_paths)

    if not os.path.exists(report_file_path):

        report_file = open(report_file_path, "w+")

        report_file.write(f"SQLite Database Blob Exporter version {version}\n")

    main()

    report_finish()
