
import os

# Folder containing medicine images
UPLOAD_FOLDER = "upload"


def get_image_files():
    """
    Get all supported image files from the upload folder.
    """

    if not os.path.exists(UPLOAD_FOLDER):
        raise FileNotFoundError(
            f"Upload folder not found: {UPLOAD_FOLDER}"
        )

    supported_formats = (".png", ".jpg", ".jpeg")

    image_files = []

    for file_name in os.listdir(UPLOAD_FOLDER):
        if file_name.lower().endswith(supported_formats):
            image_path = os.path.join(
                UPLOAD_FOLDER, file_name
            )
            image_files.append(image_path)

    return image_files
