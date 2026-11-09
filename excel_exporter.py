
import os
import pandas as pd

from database import create_connection


def export_database_to_excel():

    connection = create_connection()

    if connection is None:
        print("\nDatabase connection failed!")
        return

    try:
        cursor = connection.cursor()

        query = "SELECT * FROM medicines"

        cursor.execute(query)

        records = cursor.fetchall()

        if not records:
            print("\nNo medicine records found to export!")
            return

        # Get column names from MySQL table
        columns = [
            column[0]
            for column in cursor.description
        ]

        # Convert database records into DataFrame
        dataframe = pd.DataFrame(
            records,
            columns=columns
        )

        # Excel file path
        excel_path = os.path.join(
            os.getcwd(),
            "medicine_data.xlsx"
        )

        # Export data to Excel
        dataframe.to_excel(
            excel_path,
            index=False,
            engine="openpyxl"
        )

        print("\nMedicine data exported successfully!")
        print(f"Excel file saved at: {excel_path}")

    except Exception as error:
        print("\nExcel Export Error:", error)

    finally:
        cursor.close()
        connection.close()
