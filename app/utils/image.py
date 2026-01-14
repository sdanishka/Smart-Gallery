"""
Smart Gallery Backend - Image Processing Utilities
"""
import cv2
import numpy as np
from PIL import Image, ExifTags
from pathlib import Path
from typing import Tuple, Optional, Dict, Any
import io
import hashlib
from datetime import datetime
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


def generate_filename(original_filename: str, content: bytes) -> str:
    """Generate a unique filename based on content hash."""
    ext = Path(original_filename).suffix.lower()
    if ext not in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.heic']:
        ext = '.jpg'
    
    content_hash = hashlib.md5(content).hexdigest()[:16]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    return f"{timestamp}_{content_hash}{ext}"


def load_image(file_content: bytes) -> np.ndarray:
    """
    Load image from bytes into OpenCV format (BGR).
    
    Args:
        file_content: Raw image bytes
        
    Returns:
        BGR numpy array
    """
    nparr = np.frombuffer(file_content, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if image is None:
        raise ValueError("Failed to decode image")
    
    return image


def resize_image(image: np.ndarray, max_size: int = None) -> np.ndarray:
    """
    Resize image if it exceeds max_size while maintaining aspect ratio.
    
    Args:
        image: BGR numpy array
        max_size: Maximum dimension (width or height)
        
    Returns:
        Resized BGR numpy array
    """
    if max_size is None:
        max_size = settings.max_image_size
    
    h, w = image.shape[:2]
    
    if max(h, w) <= max_size:
        return image
    
    if w > h:
        new_w = max_size
        new_h = int(h * max_size / w)
    else:
        new_h = max_size
        new_w = int(w * max_size / h)
    
    return cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)


def create_thumbnail(image: np.ndarray, size: Tuple[int, int] = None) -> np.ndarray:
    """
    Create a square thumbnail from an image.
    
    Args:
        image: BGR numpy array
        size: Thumbnail size (width, height)
        
    Returns:
        Thumbnail BGR numpy array
    """
    if size is None:
        size = settings.thumbnail_size
    
    h, w = image.shape[:2]
    
    # Crop to square from center
    if w > h:
        start = (w - h) // 2
        image = image[:, start:start + h]
    elif h > w:
        start = (h - w) // 2
        image = image[start:start + w, :]
    
    # Resize to thumbnail size
    return cv2.resize(image, size, interpolation=cv2.INTER_AREA)


def save_image(image: np.ndarray, path: Path, quality: int = None) -> None:
    """
    Save image to disk.
    
    Args:
        image: BGR numpy array
        path: Output path
        quality: JPEG quality (1-100)
    """
    if quality is None:
        quality = settings.jpeg_quality
    
    ext = path.suffix.lower()
    
    if ext in ['.jpg', '.jpeg']:
        cv2.imwrite(str(path), image, [cv2.IMWRITE_JPEG_QUALITY, quality])
    elif ext == '.png':
        cv2.imwrite(str(path), image, [cv2.IMWRITE_PNG_COMPRESSION, 6])
    elif ext == '.webp':
        cv2.imwrite(str(path), image, [cv2.IMWRITE_WEBP_QUALITY, quality])
    else:
        cv2.imwrite(str(path), image)


def image_to_bytes(image: np.ndarray, format: str = 'jpeg', quality: int = None) -> bytes:
    """
    Convert image to bytes.
    
    Args:
        image: BGR numpy array
        format: Output format ('jpeg', 'png', 'webp')
        quality: Compression quality
        
    Returns:
        Image bytes
    """
    if quality is None:
        quality = settings.jpeg_quality
    
    if format.lower() in ['jpg', 'jpeg']:
        encode_param = [cv2.IMWRITE_JPEG_QUALITY, quality]
        ext = '.jpg'
    elif format.lower() == 'png':
        encode_param = [cv2.IMWRITE_PNG_COMPRESSION, 6]
        ext = '.png'
    elif format.lower() == 'webp':
        encode_param = [cv2.IMWRITE_WEBP_QUALITY, quality]
        ext = '.webp'
    else:
        encode_param = [cv2.IMWRITE_JPEG_QUALITY, quality]
        ext = '.jpg'
    
    success, buffer = cv2.imencode(ext, image, encode_param)
    if not success:
        raise ValueError("Failed to encode image")
    
    return buffer.tobytes()


def extract_exif(file_content: bytes) -> Dict[str, Any]:
    """
    Extract EXIF data from image.
    
    Args:
        file_content: Raw image bytes
        
    Returns:
        Dictionary of EXIF data
    """
    try:
        pil_image = Image.open(io.BytesIO(file_content))
        exif_data = pil_image._getexif()
        
        if exif_data is None:
            return {}
        
        # Convert EXIF tags to readable names
        result = {}
        for tag_id, value in exif_data.items():
            tag = ExifTags.TAGS.get(tag_id, tag_id)
            
            # Skip binary data and very long values
            if isinstance(value, bytes):
                continue
            if isinstance(value, str) and len(value) > 500:
                continue
            
            # Convert special types
            if hasattr(value, 'numerator'):  # Rational number
                value = float(value)
            
            result[tag] = value
        
        return result
    except Exception as e:
        logger.debug(f"Failed to extract EXIF: {e}")
        return {}


def get_taken_date(exif_data: Dict[str, Any]) -> Optional[datetime]:
    """
    Extract the date photo was taken from EXIF.
    
    Args:
        exif_data: Dictionary of EXIF data
        
    Returns:
        datetime or None
    """
    date_fields = ['DateTimeOriginal', 'DateTimeDigitized', 'DateTime']
    
    for field in date_fields:
        if field in exif_data:
            try:
                date_str = exif_data[field]
                # EXIF format: "YYYY:MM:DD HH:MM:SS"
                return datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")
            except (ValueError, TypeError):
                continue
    
    return None


def get_image_dimensions(image: np.ndarray) -> Tuple[int, int]:
    """Get image width and height."""
    h, w = image.shape[:2]
    return w, h


def get_mime_type(filename: str) -> str:
    """Get MIME type from filename extension."""
    ext = Path(filename).suffix.lower()
    mime_types = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.webp': 'image/webp',
        '.heic': 'image/heic',
        '.heif': 'image/heif',
    }
    return mime_types.get(ext, 'image/jpeg')
