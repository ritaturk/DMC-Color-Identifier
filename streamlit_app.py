import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import io
import os
import sys
from pathlib import Path

# Add the Utils folder to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent))

# Import your custom functions
from Utils.Image import readImage, getRoi
from Utils.Color import getDMCColors, rgba2hex, nearestDMC
from Utils.Excel import createExcel
from Utils.Constants import DMC_FILE

# Set page config
st.set_page_config(
    page_title="DMC Color Identifier",
    page_icon="🎨",
    layout="wide"
)

st.title("🎨 DMC Color Identifier")
st.markdown("Convert your sprite images to DMC cross-stitch patterns!")

# Sidebar for settings
with st.sidebar:
    st.header("Settings")
    st.write("Upload a PNG file to get started!")
    st.markdown("---")
    st.markdown("### ☕ Support This Project")
    st.markdown("[Buy me a coffee!](https://www.buymeacoffee.com/ritaturk)")
    st.header("Settings")
    st.write("Upload a PNG sprite image and the app will identify the colors and create a DMC cross-stitch pattern.")

# Create two containers for layout
col1, col2 = st.columns(2)

with col1:
    st.header("📤 Upload Your Sprite")
    uploaded_file = st.file_uploader("Choose a PNG file", type="png")

with col2:
    st.header("📊 Results")
    results_placeholder = st.empty()

# Process the uploaded file
if uploaded_file is not None:
    # Convert uploaded file to image
    image_bytes = uploaded_file.read()
    pil_image = Image.open(io.BytesIO(image_bytes))
    
    # Display the uploaded image
    with col1:
        st.image(pil_image, caption="Uploaded Sprite", use_container_width=True)
    
    # Process the image
    with st.spinner("Processing sprite..."):
        try:
            # Save temporary file to process
            temp_path = "temp_sprite.png"
            pil_image.save(temp_path)
            
            # Load and process the sprite
            sprite = getRoi(readImage(temp_path))
            
            if sprite is None:
                st.error("No visible pixels found in the image. Make sure your sprite has non-transparent areas.")
            else:
                # Load DMC colors
                colors_df = getDMCColors(DMC_FILE)
                
                # First pass: Identify all unique DMC colors
                unique_dmc = {}
                temp_colors = []
                index_counter = 0
                
                for i in range(sprite.shape[0]):
                    for j in range(sprite.shape[1]):
                        if sprite[i, j, 3] != 0:  # Non-transparent pixels
                            color = sprite[i, j]
                            dmc, floss = nearestDMC(color, colors_df)
                            
                            if floss not in unique_dmc:
                                index = chr(65 + index_counter)
                                unique_dmc[floss] = {
                                    'INDEX': index,
                                    'DMC': dmc,
                                    'REAL': color
                                }
                                temp_colors.append([index, color, dmc, floss])
                                index_counter += 1
                
                # Create DataFrame from collected color data
                sprite_colors = pd.DataFrame(temp_colors, 
                                           containers=['INDEX', 'REAL', 'DMC', 'FLOSS'])
                
                # Initialize matrices for Excel output
                index_matrix = np.full((sprite.shape[0], sprite.shape[1]), "x", dtype=object)
                real_matrix = np.full((sprite.shape[0], sprite.shape[1]), "x", dtype="U9")
                dmc_matrix = np.full((sprite.shape[0], sprite.shape[1]), "x", dtype="U9")
                
                # Second pass: Fill matrices with color information
                for i in range(sprite.shape[0]):
                    for j in range(sprite.shape[1]):
                        if sprite[i, j, 3] != 0:  # Non-transparent pixels only
                            color = sprite[i, j]
                            dmc, floss = nearestDMC(color, colors_df)
                            index = unique_dmc[floss]['INDEX']
                            
                            index_matrix[i, j] = index
                            real_matrix[i, j] = rgba2hex(color)
                            dmc_matrix[i, j] = rgba2hex(dmc)
                
                # Display results
                with col2:
                    st.success("✅ Processing complete!")
                    
                    st.subheader("Color Palette")
                    st.write(f"**Total unique colors found:** {len(sprite_colors)}")
                    
                    # Display color palette as a table
                    palette_display = sprite_colors.copy()
                    palette_display['REAL_HEX'] = palette_display['REAL'].apply(lambda x: rgba2hex(x))
                    palette_display['DMC_HEX'] = palette_display['DMC'].apply(lambda x: rgba2hex(x))
                    
                    st.dataframe(
                        palette_display[['INDEX', 'FLOSS', 'REAL_HEX', 'DMC_HEX']],
                        use_container_width=True,
                        hide_index=True
                    )
                
                # Generate Excel file
                excel_buffer = io.BytesIO()
                
                # Create a temporary file path for Excel
                temp_excel = "temp_output.xlsx"
                createExcel(index_matrix, real_matrix, dmc_matrix, sprite_colors, temp_excel)
                
                # Read the Excel file into bytes
                with open(temp_excel, 'rb') as f:
                    excel_buffer = f.read()
                
                # Provide download button
                st.download_button(
                    label="📥 Download Excel Pattern",
                    data=excel_buffer,
                    file_name=f"{uploaded_file.name.replace('.png', '')}_pattern.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                
                # Clean up temporary files
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                if os.path.exists(temp_excel):
                    os.remove(temp_excel)
        
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.write("Make sure all required files (DMC.csv, Utils modules) are in the correct locations.")
else:
    with col2:
        st.info("👈 Upload a PNG file to get started!")
