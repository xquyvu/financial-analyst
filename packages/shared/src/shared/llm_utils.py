import base64
import logging
from mimetypes import guess_type
from pathlib import Path

import pdfplumber

logger = logging.getLogger(__name__)


def extract_pages_as_images(pdf_path: Path, output_dir: Path) -> dict[str, Path]:
    """Extract each page of a PDF as an image"""

    image_paths: dict[str, Path] = {}

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            # Generate the output path for this page
            image_path = output_dir / f"{pdf_path.stem}_page_{page.page_number}.png"

            # Save the image
            page.to_image(resolution=500).save(image_path, format="PNG")
            image_paths[str(page.page_number)] = image_path

    return image_paths


def local_image_to_data_url(image_path: str | Path) -> str:
    mime_type, _ = guess_type(image_path)
    if mime_type is None:
        mime_type = "application/octet-stream"

    try:
        with open(image_path, "rb") as image_file:
            base64_encoded_data = base64.b64encode(image_file.read()).decode("utf-8")

        return f"data:{mime_type};base64,{base64_encoded_data}"

    except FileNotFoundError:
        logger.error(f"Error: The file at {image_path} was not found.")
        raise


async def get_image_data_urls(pdf_path: Path, output_dir: Path) -> dict[str, str]:
    """Converts PDF to image(s) and returns the image data URLs for LLM input"""

    image_paths = extract_pages_as_images(pdf_path, output_dir)
    image_data_urls = {
        page_num: local_image_to_data_url(image_path)
        for page_num, image_path in image_paths.items()
    }

    return image_data_urls
