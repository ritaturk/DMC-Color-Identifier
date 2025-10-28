import pandas as pd
import numpy as np


def getDMCColors(path):
    colors_df = pd.read_csv(path)
    colors_df['dmc'] = colors_df.apply(lambda row: (int(row['R']), int(row['G']), int(row['B']), 255), axis=1)  # Add an alpha channel
    return colors_df


def rgba2hex(rgba):
    """
    Converts RGBA color to hexadecimal format.
    
    Parameters:
    - rgba: Color in RGBA format (tuple).
    
    Returns:
    - Hexadecimal color string.
    """
    return "{:02X}{:02X}{:02X}{:02X}".format(rgba[3], rgba[0], rgba[1], rgba[2])  # Format ARGB to HEX

def nearestDMC(color, colors_df):
    """
    Finds the nearest DMC color for a given color.
    
    Parameters:
    - color: The color to find the nearest DMC for.
    - colors_df: DataFrame containing DMC colors.
    
    Returns:
    - Tuple containing the nearest DMC color and corresponding floss.
    """
    min_dist = float('inf')  # Initialize minimum distance to infinity
    min_dmc = None  # Placeholder for minimum DMC color
    floss = None  # Placeholder for floss associated with DMC color
    for i in range(colors_df.shape[0]):  # Iterate through color DataFrame
        dmc = colors_df.loc[i, 'dmc']  # Get DMC color
        # Calculate Euclidean distance between colors
        dist = np.linalg.norm(np.array(dmc) - np.array(color))
        if dist < min_dist:  # If current distance is less than the minimum
            min_dist = dist  # Update minimum distance
            min_dmc = dmc  # Update minimum DMC color
            floss = colors_df.loc[i, 'Floss']  # Get corresponding floss
    return np.array(min_dmc), floss  # Return the nearest DMC color and floss


def createMatrix(sprite, sprite_colors):
    """
    Creates matrices for the sprite colors, including real colors and DMC colors.
    
    Parameters:
    - sprite: The sprite image array.
    - sprite_colors: DataFrame containing colors used in the sprite.
    
    Returns:
    - Three matrices: index matrix, real color matrix, and DMC color matrix.
    """
    index_matrix = np.full((sprite.shape[0], sprite.shape[1]), "x", dtype=object)  # Initialize index matrix
    real_matrix = np.full((sprite.shape[0], sprite.shape[1]), "x", dtype="U9")  # Initialize real color matrix
    dmc_matrix = np.full((sprite.shape[0], sprite.shape[1]), "x", dtype="U9")  # Initialize DMC color matrix

    for i in range(sprite.shape[0]):  # Iterate over rows of the sprite
        for j in range(sprite.shape[1]):  # Iterate over columns of the sprite
            if sprite[i, j, 3] != 0:  # Check if pixel is not transparent
                color = sprite[i, j]  # Get the RGBA color
                # Find index of the color in sprite_colors DataFrame
                index = sprite_colors[sprite_colors['REAL'].apply(lambda x: np.array_equal(x, color))]['INDEX'].values[0]
                real_matrix[i, j] = rgba2hex(color)  # Convert color to hex and store
                dmc_matrix[i, j] = rgba2hex(sprite_colors[sprite_colors['REAL'].apply(lambda x: np.array_equal(x, color))]['DMC'].values[0])
                index_matrix[i, j] = index  # Store index of the color

    return index_matrix, real_matrix, dmc_matrix  # Return the constructed matrices