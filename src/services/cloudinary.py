"""
Cloudinary integration for avatar image uploads.
"""
 
import cloudinary
import cloudinary.uploader
from src.conf.config import settings
 
cloudinary.config(
    cloud_name=settings.CLOUDINARY_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True
)
 
 
def upload_avatar(file_path: str, public_id: str) -> str:
    """
    Upload an image file to Cloudinary and return its secure URL.
 
    The file is stored under the ``avatars/`` folder in Cloudinary.
    If a file with the same ``public_id`` already exists, it is overwritten.
 
    :param file_path: Local path to the image file to upload.
    :param public_id: Unique identifier for the image in Cloudinary.
    :return: The secure HTTPS URL of the uploaded image.
    """
    result = cloudinary.uploader.upload(
        file_path,
        public_id=f"avatars/{public_id}",
        overwrite=True,
        folder="avatars"
    )
    return result["secure_url"]
 