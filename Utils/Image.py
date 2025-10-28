
import cv2 as cv
def readImage(image_path):
    return cv.cvtColor(cv.imread(image_path, cv.IMREAD_UNCHANGED), cv.COLOR_BGRA2RGBA)

def getRoi(image):
    """
    Extracts the region of interest (ROI) from an image based on non-transparent pixels.
    
    Parameters:
    - image: A 3D NumPy array representing the image (height x width x RGBA).
    
    Returns:
    - A 3D NumPy array representing the ROI or None if no non-zero alpha pixels are found.
    """
    # Initialize boundaries for the ROI
    top, bottom, left, right = None, None, None, None

    # Iterate over each pixel in the image
    for y in range(image.shape[0]):  # Iterate over rows (height)
        for x in range(image.shape[1]):  # Iterate over columns (width)
            if image[y, x, 3] != 0:  # Check if the pixel is not transparent (alpha > 0)
                # Update the top boundary
                if top is None or y < top:
                    top = y
                # Update the bottom boundary
                if bottom is None or y > bottom:
                    bottom = y
                # Update the left boundary
                if left is None or x < left:
                    left = x
                # Update the right boundary
                if right is None or x > right:
                    right = x

    # Check if any non-transparent pixels were found
    if top is None or bottom is None or left is None or right is None:
        return None  # No non-zero alpha pixels found, return None

    # Extract and return the ROI from the image
    return image[top:bottom + 1, left:right + 1]  