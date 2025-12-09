"""
QR Code Generation Service
Generates branded QR codes with village-specific styling
"""
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer, SquareModuleDrawer
from qrcode.image.styles.colormasks import SolidFillColorMask
from PIL import Image, ImageDraw, ImageFont
import io
import os
from pathlib import Path
from typing import Optional, Tuple
import hashlib

from app.services.logger import get_logger

logger = get_logger(__name__)


class QRCodeSize:
    """QR code size presets"""
    SMALL = 200  # 200x200px
    MEDIUM = 400  # 400x400px
    LARGE = 800  # 800x800px


class VillageColors:
    """
    Default color schemes for villages
    Can be customized per village through village.settings
    """
    DEFAULT = {
        'fill_color': '#000000',  # Black QR modules
        'back_color': '#FFFFFF',  # White background
        'accent_color': '#2563eb',  # Blue accent
    }

    CHIRAC = {
        'fill_color': '#0f766e',  # Teal (historical)
        'back_color': '#f0fdfa',  # Light teal background
        'accent_color': '#0f766e',  # Teal accent
    }


class QRCodeGenerator:
    """
    Generates and manages QR codes with village branding
    """

    def __init__(self, upload_dir: str = "/app/uploads/qr_codes"):
        """
        Initialize QR code generator

        Args:
            upload_dir: Directory to save generated QR codes
        """
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def _get_village_colors(self, village_slug: str, village_settings: dict = None) -> dict:
        """
        Get color scheme for a village

        Args:
            village_slug: Village slug/identifier
            village_settings: Village settings JSON (may contain custom colors)

        Returns:
            Dictionary with fill_color, back_color, accent_color
        """
        # Check if village has custom colors in settings
        if village_settings and 'qr_colors' in village_settings:
            return village_settings['qr_colors']

        # Use predefined colors for known villages
        if village_slug == 'chirac':
            return VillageColors.CHIRAC

        # Default colors
        return VillageColors.DEFAULT

    def generate_qr_code(
        self,
        data: str,
        village_slug: str,
        size: int = QRCodeSize.MEDIUM,
        village_settings: dict = None,
        logo_path: Optional[str] = None,
        add_branding: bool = True
    ) -> Tuple[bytes, str]:
        """
        Generate a QR code image

        Args:
            data: Data to encode in QR code (usually a URL)
            village_slug: Village identifier for branding
            size: QR code size in pixels
            village_settings: Village settings for custom colors
            logo_path: Optional path to village logo to overlay
            add_branding: Add village name at bottom

        Returns:
            Tuple of (image_bytes, format) - PNG image data and format ('PNG')
        """
        try:
            # Get village colors
            colors = self._get_village_colors(village_slug, village_settings)

            # Create QR code with optimal settings
            qr = qrcode.QRCode(
                version=None,  # Auto-determine version
                error_correction=qrcode.constants.ERROR_CORRECT_H,  # High error correction for logo overlay
                box_size=10,
                border=4,
            )

            qr.add_data(data)
            qr.make(fit=True)

            # Generate image with color
            img = qr.make_image(
                image_factory=StyledPilImage,
                module_drawer=RoundedModuleDrawer(),  # Rounded corners for modern look
                color_mask=SolidFillColorMask(
                    back_color=colors['back_color'],
                    front_color=colors['fill_color']
                )
            )

            # Convert to PIL Image for further processing
            img = img.convert('RGB')

            # Resize to requested size
            img = img.resize((size, size), Image.Resampling.LANCZOS)

            # Add logo overlay if provided and exists
            if logo_path and os.path.exists(logo_path):
                img = self._add_logo_overlay(img, logo_path)

            # Add branding (village name) if requested
            if add_branding:
                img = self._add_branding(img, village_slug, colors['accent_color'])

            # Convert to bytes
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG', optimize=True)
            img_bytes.seek(0)

            return img_bytes.getvalue(), 'PNG'

        except Exception as e:
            logger.error(f"Failed to generate QR code: {e}", exc_info=True)
            raise

    def _add_logo_overlay(self, img: Image.Image, logo_path: str) -> Image.Image:
        """
        Add logo overlay to center of QR code

        Args:
            img: QR code image
            logo_path: Path to logo image

        Returns:
            Image with logo overlay
        """
        try:
            # Open logo
            logo = Image.open(logo_path)

            # Calculate logo size (15% of QR code size, max)
            qr_width, qr_height = img.size
            logo_max_size = min(qr_width, qr_height) // 6  # 16.67% of size

            # Resize logo maintaining aspect ratio
            logo.thumbnail((logo_max_size, logo_max_size), Image.Resampling.LANCZOS)

            # Add white background circle behind logo
            logo_bg = Image.new('RGB', logo.size, 'white')
            logo_bg.paste(logo, (0, 0), logo if logo.mode == 'RGBA' else None)

            # Calculate position (center)
            logo_pos = (
                (qr_width - logo.size[0]) // 2,
                (qr_height - logo.size[1]) // 2
            )

            # Paste logo
            img.paste(logo_bg, logo_pos)

            return img

        except Exception as e:
            logger.warning(f"Failed to add logo overlay: {e}")
            return img  # Return original image if logo fails

    def _add_branding(self, img: Image.Image, village_slug: str, accent_color: str) -> Image.Image:
        """
        Add village branding at bottom of QR code

        Args:
            img: QR code image
            village_slug: Village identifier
            accent_color: Accent color for text

        Returns:
            Image with branding
        """
        try:
            # Create new image with extra space at bottom
            old_width, old_height = img.size
            new_height = old_height + 60  # Add 60px for branding
            new_img = Image.new('RGB', (old_width, new_height), 'white')

            # Paste QR code at top
            new_img.paste(img, (0, 0))

            # Draw village name
            draw = ImageDraw.Draw(new_img)

            # Try to use a nice font, fall back to default if not available
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
            except:
                font = ImageFont.load_default()

            # Format village name (capitalize)
            village_name = village_slug.capitalize()
            text = f"Visit {village_name}"

            # Get text bounding box
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            # Center text
            text_x = (old_width - text_width) // 2
            text_y = old_height + 20

            # Draw text
            draw.text((text_x, text_y), text, fill=accent_color, font=font)

            return new_img

        except Exception as e:
            logger.warning(f"Failed to add branding: {e}")
            return img  # Return original image if branding fails

    def save_qr_code(
        self,
        image_bytes: bytes,
        qr_code: str,
        village_slug: str,
        size: int = QRCodeSize.MEDIUM
    ) -> str:
        """
        Save QR code image to disk

        Args:
            image_bytes: QR code image data
            qr_code: QR code identifier
            village_slug: Village slug
            size: Image size for filename

        Returns:
            Relative path to saved image (for database storage)
        """
        try:
            # Create village directory
            village_dir = self.upload_dir / village_slug
            village_dir.mkdir(parents=True, exist_ok=True)

            # Generate filename
            filename = f"{qr_code}_{size}px.png"
            filepath = village_dir / filename

            # Save file
            with open(filepath, 'wb') as f:
                f.write(image_bytes)

            # Return relative path
            return f"/uploads/qr_codes/{village_slug}/{filename}"

        except Exception as e:
            logger.error(f"Failed to save QR code: {e}", exc_info=True)
            raise

    def generate_and_save_qr_code(
        self,
        data: str,
        qr_code: str,
        village_slug: str,
        village_settings: dict = None,
        sizes: list[int] = None,
        logo_path: Optional[str] = None
    ) -> dict[int, str]:
        """
        Generate QR code in multiple sizes and save all

        Args:
            data: Data to encode
            qr_code: QR code identifier
            village_slug: Village slug
            village_settings: Village settings
            sizes: List of sizes to generate (defaults to all standard sizes)
            logo_path: Optional logo overlay

        Returns:
            Dictionary mapping size to saved path
        """
        if sizes is None:
            sizes = [QRCodeSize.SMALL, QRCodeSize.MEDIUM, QRCodeSize.LARGE]

        paths = {}

        for size in sizes:
            try:
                # Generate QR code
                image_bytes, _ = self.generate_qr_code(
                    data=data,
                    village_slug=village_slug,
                    size=size,
                    village_settings=village_settings,
                    logo_path=logo_path
                )

                # Save to disk
                path = self.save_qr_code(
                    image_bytes=image_bytes,
                    qr_code=qr_code,
                    village_slug=village_slug,
                    size=size
                )

                paths[size] = path

                logger.info(f"Generated QR code: {qr_code} ({size}px) for {village_slug}")

            except Exception as e:
                logger.error(f"Failed to generate QR code size {size}px: {e}")

        return paths

    def generate_qr_code_data_url(
        self,
        data: str,
        village_slug: str,
        size: int = QRCodeSize.SMALL,
        village_settings: dict = None
    ) -> str:
        """
        Generate QR code as data URL (for inline display)

        Args:
            data: Data to encode
            village_slug: Village slug
            size: QR code size
            village_settings: Village settings

        Returns:
            Data URL string (base64 encoded PNG)
        """
        import base64

        try:
            image_bytes, _ = self.generate_qr_code(
                data=data,
                village_slug=village_slug,
                size=size,
                village_settings=village_settings,
                add_branding=False  # No branding for small inline images
            )

            # Encode as base64
            b64_data = base64.b64encode(image_bytes).decode('utf-8')

            return f"data:image/png;base64,{b64_data}"

        except Exception as e:
            logger.error(f"Failed to generate data URL: {e}")
            raise


# Global instance
_qr_generator: Optional[QRCodeGenerator] = None


def get_qr_generator() -> QRCodeGenerator:
    """
    Get global QR code generator instance

    Returns:
        QRCodeGenerator instance
    """
    global _qr_generator
    if _qr_generator is None:
        _qr_generator = QRCodeGenerator()
    return _qr_generator
