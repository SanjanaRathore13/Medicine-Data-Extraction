
import os

from image_processing import process_medicine_images
from attribute_extractor import extract_attributes
from database import insert_record


def main():

    print("\n" + "=" * 50)
    print("       MEDICINE DATA EXTRACTION SYSTEM")
    print("=" * 50)

    # Step 1: Get image name or path
    image_path = input(
        "\nEnter medicine image name/path: "
    ).strip().strip('"')

    # Search inside upload folder if direct path is not found
    if not os.path.isfile(image_path):
        image_path = os.path.join("upload", image_path)

    # Step 2: Validate image
    if not os.path.isfile(image_path):
        print("\nError: Image not found!")
        return

    if not image_path.lower().endswith(
        (".png", ".jpg", ".jpeg")
    ):
        print("\nError: Unsupported image format!")
        return

    # Step 3: Perform OCR
    print("\nProcessing medicine image...")

    ocr_results = process_medicine_images([image_path])

    raw_text = ocr_results.get(image_path, "")
    print("\n========== RAW OCR TEXT ==========")
    print(raw_text)
    print("==================================")

    if not raw_text.strip():
        print("\nNo text extracted from image!")
        return

    # Step 4: Extract attributes
    medicine_data = extract_attributes(raw_text)

    print("\n" + "=" * 50)
    print("       EXTRACTED MEDICINE DETAILS")
    print("=" * 50)

    print("\nFIXED ATTRIBUTES:")

    for key, value in medicine_data["fixed_attributes"].items():
        print(f"{key}: {value}")

    print("\nADDITIONAL ATTRIBUTES:")

    for key, value in medicine_data["additional_attributes"].items():
        print(f"{key}: {value}")

    # Step 5: Insert into MySQL
    print("\nSaving data to database...")

    insert_record(medicine_data)


if __name__ == "__main__":
    main()
