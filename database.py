
import mysql.connector
import os

from dynamic_schema import ensure_dynamic_columns
from dotenv import load_dotenv

load_dotenv()


# 1. MySQL Database Connection
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


# 2. Insert Medicine Record
def insert_record(medicine_data):

    connection = create_connection()

    if connection is None:
        return

    cursor = None

    try:
        cursor = connection.cursor()

        fixed = medicine_data["fixed_attributes"]
        additional = medicine_data["additional_attributes"]

        # Create missing dynamic columns
        dynamic_data = ensure_dynamic_columns(
            cursor,
            additional
        )

        # Fixed attributes
        insert_data = {
            "medicine_name": fixed.get("medicine_name"),
            "batch_no": fixed.get("batch_no"),
            "manufacturing_date": fixed.get("manufacturing_date"),
            "expiry_date": fixed.get("expiry_date"),
            "mrp": fixed.get("mrp")
        }

        # Add dynamic attributes
        insert_data.update(dynamic_data)

        columns = list(insert_data.keys())

        column_names = ", ".join(
            f"`{column}`" for column in columns
        )

        placeholders = ", ".join(
            ["%s"] * len(columns)
        )

        query = f"""
            INSERT INTO medicines ({column_names})
            VALUES ({placeholders})
        """

        cursor.execute(
            query,
            tuple(insert_data.values())
        )

        connection.commit()

        print("\nMedicine record inserted successfully!")
        print("Fixed and dynamic attributes saved separately.")

    except Exception as error:
        connection.rollback()
        print("\nData Insertion Error:", error)

    finally:
        if cursor:
            cursor.close()

        connection.close()


# 3. Display Medicine Database Records
def display_database_records():

    connection = create_connection()

    if connection is None:
        return

    cursor = None

    try:
        cursor = connection.cursor()

        cursor.execute("SHOW COLUMNS FROM medicines")

        all_columns = [
            row[0] for row in cursor.fetchall()
        ]

        display_columns = [
            column for column in all_columns
            if column.lower() != "additional_attributes"
        ]

        column_query = ", ".join(
            f"`{column}`" for column in display_columns
        )

        cursor.execute(
            f"SELECT {column_query} FROM medicines"
        )

        records = cursor.fetchall()

        if not records:
            print("\nNo medicine records found!")
            return

        headers = display_columns

        rows = [
            [
                "NULL" if value is None else str(value)
                for value in record
            ]
            for record in records
        ]

        column_widths = [
            max(
                len(headers[i]),
                max(len(row[i]) for row in rows)
            )
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
        if cursor:
            cursor.close()

        connection.close()
