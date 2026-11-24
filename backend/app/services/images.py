"""Check uploaded images and remove camera metadata before saving a JPEG copy.
Copyright (c) 2026 Imarah.tech. All rights reserved.
"""

import io
import warnings

from PIL import Image, ImageOps, UnidentifiedImageError

from ..config import MAX_UPLOAD


def clean_image(content, destination):
    if not content or len(content) > MAX_UPLOAD:
        raise ValueError("Choose a JPEG, PNG or WebP image smaller than 10 MB.")
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(io.BytesIO(content)) as source:
                if source.format not in ("JPEG", "PNG", "WEBP"):
                    raise ValueError("Only JPEG, PNG and WebP images are supported.")
                if source.width * source.height > 20_000_000:
                    raise ValueError(
                        "The image is too large. Please use a photo below 20 megapixels."
                    )
                source.load()
                image = ImageOps.exif_transpose(source).convert("RGB")
                image.thumbnail((1600, 1600))
                image.save(destination, "JPEG", quality=90)
                return {"width": image.width, "height": image.height}
    except (
        UnidentifiedImageError,
        OSError,
        Image.DecompressionBombError,
        Image.DecompressionBombWarning,
    ) as exc:
        raise ValueError("This file is not a readable image. Please choose another photo.") from exc
