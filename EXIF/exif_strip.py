import os
import sys
from PIL import Image, ImageOps

def main(argz=[]):
    images = []
    replace = False
    if not argz:
        argz = sys.argv

    for i in range(1, len(argz)):
        if argz[i].lower() in ['-r', '--r', '-replace', '--replace']:
            replace = True
        elif argz[i].lower() in ['-h', '--h', '-help', '--help']:
            usage()
        else:
            images.append(argz[i])

    if len(images) < 1:
        usage()

    batch_exif_delete(images, replace)

def usage():
    print(__doc__)
    exit()

def batch_exif_delete(images, replace):
    print('\nRemoving EXIF data from:')

    for original_image_path in images:
        if not os.path.exists(original_image_path):
            print('\tERROR: File Not Found. ' + str(original_image_path))
            continue

        if replace:
            new_image_path = original_image_path
        else:
            base_path, ext = os.path.splitext(original_image_path)
            new_image_path = base_path + "_safe" + ext

        print('\t' + str(original_image_path))
        exif_delete(original_image_path, new_image_path)

def exif_delete(original_file_path, new_file_path):
    try:
        original = Image.open(original_file_path)
    except IOError:
        print('ERROR: Problem reading image file. ' + str(original_file_path))
        return

    print_metadata(original.info)

    original = ImageOps.exif_transpose(original)

    stripped = Image.new(original.mode, original.size)
    stripped.putdata(list(original.getdata()))
    stripped.save(new_file_path)

def print_metadata(metadata):
    print("\nMetadata:")
    for key, value in metadata.items():
        print(f"{key}: {value}")

if __name__ == '__main__':
    main()
