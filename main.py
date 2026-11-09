
from file_handler import get_image_files
from image_processing import process_medicine_images
from attribute_extractor import extract_attributes
from database import display_database_records
from excel_exporter import export_database_to_excel

# View Extracted Medicine Data
def view_extracted_medicine_data():

    image_paths = get_image_files()

    if not image_paths:
        print("\nNo medicine images found!")
        return

    print(f"\nTotal Medicine Images Found: {len(image_paths)}")

    ocr_results = process_medicine_images(image_paths)

    for index, (image_path, raw_text) in enumerate(
        ocr_results.items(), start=1
    ):

        print("\n" + "=" * 55)
        print(f"MEDICINE RECORD {index}")
        print("=" * 55)

        if not raw_text.strip():
            print("No text extracted from this image!")
            continue

        medicine_data = extract_attributes(raw_text)

        print("\nFIXED ATTRIBUTES:")

        for key, value in medicine_data["fixed_attributes"].items():
            print(f"{key}: {value}")

        print("\nADDITIONAL ATTRIBUTES:")

        for key, value in medicine_data["additional_attributes"].items():
            print(f"{key}: {value}")


# Main Menu
def main():

    while True:

        print("\n" + "=" * 45)
        print("       MEDICINE DATA EXTRACTION SYSTEM")
        print("=" * 45)

        print("1. View Extracted Medicine Data")
        print("2. View Medicine Data in Table Format")
        print("3. Export Medicine Data to Excel")
        print("0. Exit")

        choice = input("\nEnter your choice: ").strip()

        if choice == "1":

            view_extracted_medicine_data()

        elif choice == "2":

            display_database_records()
        elif choice == "3":
            export_database_to_excel()

        elif choice == "0":

            print("\nExiting Medicine Data Extraction System. Goodbye!")
            break

        else:

            print("\nInvalid choice! Please select a valid option.")


if __name__ == "__main__":
    main()
