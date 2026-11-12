
import cv2
import pytesseract

# Tesseract OCR path
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


def preprocess_image(image_path):

    image = cv2.imread(image_path)

    if image is None:
        print(f"Image could not be loaded: {image_path}")
        return None

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    gray = cv2.resize(
        gray,
        None,
        fx=2,
        fy=2,
        interpolation=cv2.INTER_CUBIC
    )

    denoised = cv2.bilateralFilter(
        gray, 9, 75, 75
    )

    processed = cv2.threshold(
        denoised,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )[1]

    return processed


def extract_image_text(image_path):

    processed_image = preprocess_image(image_path)

    if processed_image is None:
        return ""

    extracted_text = pytesseract.image_to_string(
        processed_image,
        lang="eng"
    )

    return extracted_text


def process_medicine_images(image_paths):

    all_extracted_data = {}

    for image_path in image_paths:

        print(f"\nProcessing: {image_path}")

        extracted_text = extract_image_text(image_path)

        all_extracted_data[image_path] = extracted_text

        print("OCR extraction completed!")

    return all_extracted_data
