# Import necessary libraries
import os
import streamlit as st
from PIL import Image, ImageOps


def batch_exif_delete(images, replace):
    """ Remove the EXIF data from a list of images.
    If the replace flag is set to True, then the new path is the same as the original path.
    If not, the file name will have "_safe" appended to it.

    Args:
        images (list): paths to one or more image files
        replace (bool): Do you want to over-write the original file(s)?
    Returns: None
    """
    st.write('\nExtracting EXIF data from:')
    for original_image_path in images:
        # validate that the file exists
        if not os.path.exists(original_image_path):
            st.error('ERROR: File Not Found. ' + str(original_image_path))
            continue

        # build output file name
        if replace:
            new_image_path = original_image_path
        else:
            base_path, ext = os.path.splitext(original_image_path)
            new_image_path = base_path + "_safe" + ext

        # create new image file, with stripped EXIF data
        st.write('\t' + str(original_image_path))
        exif_delete(original_image_path, new_image_path)


def exif_delete(original_file_path, new_file_path):
    """ Read an image file, print its metadata, and write a new one that lacks all metadata.

    Args:
        original_file_path (str): file path for the original image
        new_file_path (str): where to write the new image
    Returns: None
    """
    # open input image file
    try:
        original = Image.open(original_file_path)
    except IOError:
        st.error('ERROR: Problem reading image file. ' + str(original_file_path))
        return

    # print metadata
    print_metadata(original.info)

    # rotate image to correct orientation before removing EXIF data
    original = ImageOps.exif_transpose(original)

    # create output image, forgetting the EXIF metadata
    stripped = Image.new(original.mode, original.size)
    stripped.putdata(list(original.getdata()))

    # Save the stripped image
    stripped.save(new_file_path)
    st.success(f'Image saved to: {new_file_path}')


def print_metadata(metadata):
    """ Print metadata to the console.

    Args:
        metadata (dict): Dictionary containing metadata information
    Returns: None
    """
    st.write("\nMetadata:")
    for key, value in metadata.items():
        st.write(f"{key}: {value}")


# Streamlit UI
def main():
    st.set_page_config(
        page_title="Image EXIF Data Remover",
        page_icon="✂",
        layout="wide"
    )

    st.title("Image EXIF Data Remover")

    uploaded_files = st.file_uploader("Upload images", type=["jpg", "jpeg"], accept_multiple_files=True)

    if not uploaded_files:
        st.warning("Please upload at least one image.")
        st.stop()

    replace = st.checkbox("Replace original files", value=False)
    images = [uploaded_file.name for uploaded_file in uploaded_files]

    batch_exif_delete(images, replace)


if __name__ == '__main__':
    main()