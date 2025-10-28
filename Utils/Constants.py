import os
# Main code directory paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)

SPRITES_FOLDER = os.path.join(PROJECT_DIR, 'Sprites')  # Folder containing sprite images
RESULTS_FOLDER = os.path.join(PROJECT_DIR, 'Results')  # Folder for saving results
DMC_FILE = os.path.join(PROJECT_DIR, 'Sprites', 'DMC.csv')  # DMC color palette file