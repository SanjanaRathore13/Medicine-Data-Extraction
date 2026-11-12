
import re


def ensure_dynamic_columns(cursor, additional_attributes):
    """
    Automatically create missing attribute columns
    in the existing medicines table.
    """

    if not isinstance(additional_attributes, dict):
        raise TypeError("Additional attributes must be a dictionary.")

    # Get existing table columns
    cursor.execute("SHOW COLUMNS FROM medicines")

    existing_columns = {
        row[0].lower() for row in cursor.fetchall()
    }

    dynamic_data = {}

    for attribute, value in additional_attributes.items():

        if value is None or not str(attribute).strip():
            continue

        # Convert attribute name into a valid SQL column name
        column_name = re.sub(
            r"[^a-zA-Z0-9_]",
            "_",
            attribute.strip().lower()
        )

        if not column_name or not column_name[0].isalpha():
            continue

        # Create column if it does not already exist
        if column_name not in existing_columns:

            query = (
                f"ALTER TABLE medicines "
                f"ADD COLUMN `{column_name}` TEXT"
            )

            cursor.execute(query)

            existing_columns.add(column_name)

            print(f"New column created: {column_name}")

        dynamic_data[column_name] = value

    return dynamic_data
