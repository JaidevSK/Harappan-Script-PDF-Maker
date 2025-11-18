import streamlit as st
import os
import cv2
from fpdf import FPDF

# --- Core PDF Generation Logic ---
def generate_pdf(input_string, image_folder, output_filename, x_start, y_start, max_width, max_height, image_width, h_gap, v_gap):
    """
    Generates a PDF from a string of image indices.

    Args:
        input_string (str): The input string in the format "_i_j_k...".
        image_folder (str): Path to the folder containing images.
        output_filename (str): The name of the output PDF file.
        x_start (int): Initial X position on the page.
        y_start (int): Initial Y position on the page.
        max_width (int): Writable width of the page.
        max_height (int): Writable height of the page.
        image_width (int): The fixed width for each image in the PDF.
        h_gap (int): Horizontal gap between images.
        v_gap (int): Vertical gap between lines of images.

    Returns:
        bytes: The generated PDF file as a byte string.
    """
    # Robustly parse the input string to get a list of integer indices
    try:
        indices = [int(s) for s in input_string.strip().split('_') if s.isdigit()]
        if not indices:
            st.warning("Input string is empty or contains no valid indices.")
            return None
    except (ValueError, TypeError):
        st.error("Invalid input string format. Please use the format '_1_2_3...'.")
        return None

    pdf = FPDF()
    pdf.add_page()

    x, y = x_start, y_start
    line_height = 0

    for index in indices:
        image_path = os.path.join(image_folder, f'{index}.png')
        
        if os.path.exists(image_path):
            try:
                # Get image dimensions to calculate aspect ratio
                img = cv2.imread(image_path)
                h, w, _ = img.shape
                aspect_ratio = w / h
                new_width = image_width
                new_height = new_width / aspect_ratio
            except Exception as e:
                st.warning(f"Could not read image {image_path}. Skipping. Error: {e}")
                continue

            # If adding the image exceeds the page width, move to the next line
            if x + new_width > (x_start + max_width):
                x = x_start
                y += line_height + v_gap
                line_height = 0

            # If adding the image exceeds the page height, create a new page
            if y + new_height > (y_start + max_height):
                pdf.add_page()
                x, y = x_start, y_start
                line_height = 0

            pdf.image(image_path, x, y, new_width, new_height)
            x += new_width + h_gap
            line_height = max(line_height, new_height)
        else:
            st.warning(f"Image not found for index {index} at '{image_path}'. Skipping.")
    
    # Return PDF data as bytes for download
    return pdf.output(dest='S').encode('latin-1')


# --- Streamlit User Interface ---

st.set_page_config(layout="wide", page_title="Harappan Script PDF Generator")

st.title("📄 PDF Maker for Harappan Script")

# --- Sidebar for Parameters ---
st.sidebar.header("⚙️ PDF Parameters")

# File and Folder Parameters
st.sidebar.subheader("File Settings")
image_folder = "final"
output_filename = st.sidebar.text_input("Output PDF Name", value="output.pdf")

# Page Layout Parameters
st.sidebar.subheader("Page Layout (in mm)")
# A4 page is 210 x 297 mm
max_width_val = st.sidebar.slider("Max Writable Page Width", 50, 210, 190)
max_height_val = st.sidebar.slider("Max Writable Page Height", 50, 297, 277)
x_start_val = st.sidebar.number_input("Starting X Position (Left Margin)", 0, 100, 10)
y_start_val = st.sidebar.number_input("Starting Y Position (Top Margin)", 0, 100, 10)

# Font Sizing and Spacing Parameters
st.sidebar.subheader("Font Sizing & Spacing (in mm)")
img_width_val = st.sidebar.slider("Font Width", 5, 50, 10)
h_gap_val = st.sidebar.slider("Horizontal Gap Between Characters", 0, 20, 5)
v_gap_val = st.sidebar.slider("Vertical Gap Between Lines", 0, 20, 5)


# --- Main Application Area ---
st.header("Enter Your Numeric String")
input_text = st.text_area(
    "Enter the string of character indices (e.g., _1_2_3_4_5...):",
    "_1_2_3_4_5_6_7_8_9_10_11_12_13_14_15_16_17_18_19_20_21_22_23_24_25_26_27_28_29_30",
    height=150
)

if st.button("🚀 Generate PDF"):
    if not input_text:
        st.warning("Please enter an input string.")
    else:
        with st.spinner("Creating your PDF... This may take a moment."):
            pdf_data = generate_pdf(
                input_string=input_text,
                image_folder=image_folder,
                output_filename=output_filename,
                x_start=x_start_val,
                y_start=y_start_val,
                max_width=max_width_val,
                max_height=max_height_val,
                image_width=img_width_val,
                h_gap=h_gap_val,
                v_gap=v_gap_val,
            )
        
        if pdf_data:
            st.success("🎉 PDF generated successfully!")
            
            # Provide a download button
            st.download_button(
                label="📥 Download PDF",
                data=pdf_data,
                file_name=output_filename,
                mime="application/pdf"
            )

# Now, have a reference. We will display the image "all_images.png" which contains all the images from 1 to 330 in a grid format.
st.header("Reference: All Harappan Script Characters")
if os.path.exists("all_images.png"):
    st.image("all_images.png", caption="All Harappan Script Characters", use_container_width=True)