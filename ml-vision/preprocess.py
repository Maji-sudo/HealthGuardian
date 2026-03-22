import cv2
import numpy as np


# ─────────────────────────────────────────────
# LOAD IMAGE FROM DIFFERENT SOURCES
# ─────────────────────────────────────────────

def load_image_from_path(image_path):
    """Load a JPG/PNG image from file path."""
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Could not load image: {image_path}")
    return image


def load_image_from_bytes(image_bytes):
    """Load image from bytes (e.g. from FastAPI UploadFile)."""
    np_arr = np.frombuffer(image_bytes, np.uint8)
    image  = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    return image


def convert_pdf_page_to_image(pdf_path, page_number=0):
    """Convert a PDF page to OpenCV image (for scanned PDFs)."""
    import fitz
    pdf       = fitz.open(pdf_path)
    page      = pdf[page_number]
    mat       = fitz.Matrix(3.0, 3.0)  # high resolution for better OCR
    pix       = page.get_pixmap(matrix=mat)
    img_bytes = pix.tobytes("png")
    np_arr    = np.frombuffer(img_bytes, np.uint8)
    image     = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    return image


# ─────────────────────────────────────────────
# DETECT IF IMAGE IS HANDWRITTEN
# ─────────────────────────────────────────────

def is_handwritten(image):
    """
    Rough heuristic to detect handwriting.
    Handwritten text has lower, irregular edge density.
    Returns True if likely handwritten.
    """
    gray         = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
    edges        = cv2.Canny(gray, 50, 150)
    edge_density = np.sum(edges > 0) / edges.size
    return edge_density < 0.08


# ─────────────────────────────────────────────
# INDIVIDUAL PROCESSING STEPS
# ─────────────────────────────────────────────

def to_grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def enhance_brightness(image):
    """CLAHE — fixes dark or shadowed scans."""
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    return clahe.apply(image)


def remove_noise(image):
    return cv2.GaussianBlur(image, (3, 3), 0)


def deskew(image):
    """Fix rotation/skew — useful for phone photos taken at an angle."""
    coords = np.column_stack(np.where(image > 0))
    if len(coords) == 0:
        return image
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    (h, w) = image.shape[:2]
    center  = (w // 2, h // 2)
    M       = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(
        image, M, (w, h),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_REPLICATE
    )
    return rotated


def apply_threshold(image):
    """Otsu threshold — best for printed/digital documents."""
    _, thresh = cv2.threshold(
        image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )
    return thresh


def apply_adaptive_threshold(image):
    """Adaptive threshold — best for handwritten or uneven lighting."""
    return cv2.adaptiveThreshold(
        image, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31, 10
    )


def sharpen(image):
    """Sharpen text edges."""
    kernel = np.array([[0, -1,  0],
                       [-1,  5, -1],
                       [0,  -1,  0]])
    return cv2.filter2D(image, -1, kernel)


# ─────────────────────────────────────────────
# MAIN PREPROCESS FUNCTION
# ─────────────────────────────────────────────

def preprocess(image, is_handwrite=False):
    """
    Full preprocessing pipeline.

    Parameters:
    - image        : OpenCV image (numpy array)
    - is_handwrite : True for handwritten prescriptions

    Returns:
    - Cleaned grayscale image ready for OCR
    """
    gray     = to_grayscale(image)
    bright   = enhance_brightness(gray)
    clean    = remove_noise(bright)
    deskewed = deskew(clean)

    # Printed → Otsu | Handwritten → Adaptive
    if is_handwrite:
        final = apply_adaptive_threshold(deskewed)
    else:
        final = apply_threshold(deskewed)

    sharpened = sharpen(final)
    return sharpened