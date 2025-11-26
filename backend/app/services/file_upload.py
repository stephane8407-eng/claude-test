"""
File upload validation and processing service
Handles image validation, resizing, and security
"""
from PIL import Image
from PIL.ExifTags import TAGS
from io import BytesIO
from typing import Optional, Tuple
import mimetypes
import os


class FileUploadValidator:
    """
    Validates and processes file uploads with security in mind
    """

    # Max file size: 5MB
    MAX_FILE_SIZE = 5 * 1024 * 1024

    # Allowed MIME types
    ALLOWED_MIME_TYPES = {
        'image/jpeg': '.jpg',
        'image/jpg': '.jpg',
        'image/png': '.png',
        'image/webp': '.webp'
    }

    # Allowed file extensions
    ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}

    # Max image dimensions
    MAX_WIDTH = 1920
    MAX_HEIGHT = 1920

    @staticmethod
    def validate_file_size(file_size: int) -> Tuple[bool, Optional[str]]:
        """
        Validate file size

        Args:
            file_size: Size of file in bytes

        Returns:
            Tuple of (is_valid, error_message)
        """
        if file_size > FileUploadValidator.MAX_FILE_SIZE:
            return False, f"File too large: {file_size} bytes (max {FileUploadValidator.MAX_FILE_SIZE / 1024 / 1024}MB)"

        if file_size == 0:
            return False, "File is empty"

        return True, None

    @staticmethod
    def validate_file_extension(filename: str) -> Tuple[bool, Optional[str]]:
        """
        Validate file extension

        Args:
            filename: Name of the file

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not filename:
            return False, "Filename is required"

        ext = os.path.splitext(filename)[1].lower()

        if ext not in FileUploadValidator.ALLOWED_EXTENSIONS:
            return False, f"File type not allowed: {ext} (allowed: {', '.join(FileUploadValidator.ALLOWED_EXTENSIONS)})"

        return True, None

    @staticmethod
    def validate_mime_type(mime_type: str) -> Tuple[bool, Optional[str]]:
        """
        Validate MIME type

        Args:
            mime_type: MIME type of the file

        Returns:
            Tuple of (is_valid, error_message)
        """
        if mime_type not in FileUploadValidator.ALLOWED_MIME_TYPES:
            return False, f"MIME type not allowed: {mime_type} (allowed: {', '.join(FileUploadValidator.ALLOWED_MIME_TYPES.keys())})"

        return True, None

    @staticmethod
    def detect_mime_type(file_content: bytes, filename: str) -> str:
        """
        Detect MIME type from file content

        Args:
            file_content: File content as bytes
            filename: Filename for fallback detection

        Returns:
            Detected MIME type
        """
        # Try to detect from actual file content using PIL
        try:
            img = Image.open(BytesIO(file_content))
            format_to_mime = {
                'JPEG': 'image/jpeg',
                'PNG': 'image/png',
                'WEBP': 'image/webp'
            }
            return format_to_mime.get(img.format, 'application/octet-stream')
        except Exception:
            # Fallback to extension-based detection
            mime_type, _ = mimetypes.guess_type(filename)
            return mime_type or 'application/octet-stream'

    @staticmethod
    def strip_exif(image: Image.Image) -> Image.Image:
        """
        Strip EXIF metadata from image for privacy

        Args:
            image: PIL Image object

        Returns:
            Image without EXIF data
        """
        # Create a new image without EXIF data
        data = list(image.getdata())
        image_without_exif = Image.new(image.mode, image.size)
        image_without_exif.putdata(data)

        return image_without_exif

    @staticmethod
    def resize_image(image: Image.Image, max_width: int = MAX_WIDTH, max_height: int = MAX_HEIGHT) -> Image.Image:
        """
        Resize image to fit within max dimensions while preserving aspect ratio

        Args:
            image: PIL Image object
            max_width: Maximum width in pixels
            max_height: Maximum height in pixels

        Returns:
            Resized image
        """
        # Get current dimensions
        width, height = image.size

        # Check if resize is needed
        if width <= max_width and height <= max_height:
            return image

        # Calculate new dimensions preserving aspect ratio
        ratio = min(max_width / width, max_height / height)
        new_width = int(width * ratio)
        new_height = int(height * ratio)

        # Resize using high-quality resampling
        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    @staticmethod
    def process_image_upload(
        file_content: bytes,
        filename: str,
        max_width: int = MAX_WIDTH,
        max_height: int = MAX_HEIGHT
    ) -> Tuple[bool, Optional[bytes], Optional[str], Optional[str]]:
        """
        Complete image upload processing pipeline

        Args:
            file_content: Raw file content as bytes
            filename: Original filename
            max_width: Maximum image width
            max_height: Maximum image height

        Returns:
            Tuple of (success, processed_image_bytes, mime_type, error_message)
        """
        # Validate file size
        is_valid, error = FileUploadValidator.validate_file_size(len(file_content))
        if not is_valid:
            return False, None, None, error

        # Validate file extension
        is_valid, error = FileUploadValidator.validate_file_extension(filename)
        if not is_valid:
            return False, None, None, error

        # Detect actual MIME type from content
        mime_type = FileUploadValidator.detect_mime_type(file_content, filename)

        # Validate MIME type
        is_valid, error = FileUploadValidator.validate_mime_type(mime_type)
        if not is_valid:
            return False, None, None, error

        try:
            # Open image
            img = Image.open(BytesIO(file_content))

            # Convert RGBA to RGB if needed (for JPEG compatibility)
            if img.mode in ('RGBA', 'LA', 'P'):
                # Create white background
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                img = background

            # Strip EXIF metadata
            img = FileUploadValidator.strip_exif(img)

            # Resize image
            img = FileUploadValidator.resize_image(img, max_width, max_height)

            # Save processed image to bytes
            output = BytesIO()
            if mime_type == 'image/png':
                img.save(output, format='PNG', optimize=True)
            elif mime_type == 'image/webp':
                img.save(output, format='WEBP', quality=85)
            else:  # JPEG
                img.save(output, format='JPEG', quality=85, optimize=True)

            processed_bytes = output.getvalue()

            return True, processed_bytes, mime_type, None

        except Exception as e:
            return False, None, None, f"Failed to process image: {str(e)}"

    @staticmethod
    def validate_and_process(
        file_content: bytes,
        filename: str
    ) -> Tuple[bool, Optional[bytes], Optional[str], Optional[str]]:
        """
        Convenience method for validation and processing

        Args:
            file_content: Raw file content
            filename: Original filename

        Returns:
            Tuple of (success, processed_bytes, mime_type, error_message)
        """
        return FileUploadValidator.process_image_upload(file_content, filename)


# Convenience function
def process_uploaded_file(file_content: bytes, filename: str) -> dict:
    """
    Process an uploaded file and return result

    Args:
        file_content: Raw file content
        filename: Original filename

    Returns:
        Dictionary with result:
        {
            'success': bool,
            'data': bytes or None,
            'mime_type': str or None,
            'error': str or None
        }
    """
    success, data, mime_type, error = FileUploadValidator.validate_and_process(
        file_content, filename
    )

    return {
        'success': success,
        'data': data,
        'mime_type': mime_type,
        'error': error
    }
