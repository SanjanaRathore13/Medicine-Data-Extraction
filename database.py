
import mysql.connector
import json
import os

from dotenv import load_dotenv

load_dotenv()

# MySQL Database Connection
def create_connection():

    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")

        )

        return connection

    except mysql.connector.Error as error:
        print("\nDatabase Connection Error:", error)
        return None


# Insert Medicine Record
def insert_record(medicine_data):

    connection = create_connection()

    if connection is None:
        return

    try:
        cursor = connection.cursor()

        fixed = medicine_data["fixed_attributes"]
        additional = medicine_data["additional_attributes"]

        query = """
            INSERT INTO medicines (
                medicine_name,
                batch_no,
                manufacturing_date,
                expiry_date,
                mrp,
                additional_attributes
            )
            VALUES (%s, %s, %s, %s, %s, %s)
        """

        values = (
            fixed.get("medicine_name"),
            fixed.get("batch_no"),
            fixed.get("manufacturing_date"),
            fixed.get("expiry_date"),
            fixed.get("mrp"),
            json.dumps(additional)
        )

        cursor.execute(query, values)
        connection.commit()

        print("\nMedicine record inserted successfully!")

    except mysql.connector.Error as error:
        print("\nData Insertion Error:", error)

    finally:
        cursor.close()
        connection.close()


# Display Medicine Database Records
def display_database_records():

    connection = create_connection()

    if connection is None:
        return

    try:
        cursor = connection.cursor()

        query = """
            SELECT
                medicine_id,
                medicine_name,
                batch_no,
                manufacturing_date,
                expiry_date,
                mrp,
                additional_attributes
            FROM medicines
        """

        cursor.execute(query)

        records = cursor.fetchall()

        if not records:
            print("\nNo medicine records found in database!")
            return

        headers = [
            "ID",
            "Medicine Name",
            "Batch No",
            "MFG Date",
            "EXP Date",
            "MRP",
            "Additional Attributes"
        ]

        rows = []

        for record in records:

            rows.append([
                str(record[0]),
                str(record[1] or ""),
                str(record[2] or ""),
                str(record[3] or ""),
                str(record[4] or ""),
                str(record[5] or ""),
                str(record[6] or "")
            ])

        column_widths = [
            max(len(headers[i]), max(len(row[i]) for row in rows))
            for i in range(len(headers))
        ]

        separator = "+".join(
            "-" * (width + 2)
            for width in column_widths
        )

        print("\nMEDICINE DATABASE RECORDS\n")
        print(separator)

        print(
            "|".join(
                " " + headers[i].ljust(column_widths[i]) + " "
                for i in range(len(headers))
            )
        )

        print(separator)

        for row in rows:
            print(
                "|".join(
                    " " + row[i].ljust(column_widths[i]) + " "
                    for i in range(len(row))
                )
            )

        print(separator)

    except mysql.connector.Error as error:
        print("\nDatabase Fetch Error:", error)

    finally:
        cursor.close()
        connection.close()
