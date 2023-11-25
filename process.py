import os
import shutil
import fitz
from PIL import Image
import toml

def read_toml_file(file_path):
    try:
        with open(file_path, 'r') as toml_file:
            data = toml.load(toml_file)
            return data
    except FileNotFoundError:
        print(f"Error: File not found - {file_path}")
        return None
    except toml.TomlDecodeError as e:
        print(f"Error decoding TOML file: {e}")
        return None

def create_screenshot(pdf_path, output_folder, max_resolution=1000):
    # Open the PDF file
    pdf_document = fitz.open(pdf_path)

    # Get the first page
    first_page = pdf_document[0]

    # Get the original size of the page
    original_size = first_page.rect

    # Calculate the new size to maintain the aspect ratio
    new_width = min(original_size.width, max_resolution)
    new_height = int((new_width / original_size.width) * original_size.height)

    # Create a new image with the calculated size
    image = first_page.get_pixmap(matrix=fitz.Matrix(new_width / original_size.width, new_height / original_size.height))

    # Convert the PyMuPDF image to a Pillow image
    pillow_image = Image.frombytes("RGB", [image.width, image.height], image.samples)

    # Save the image to the output folder
    output_file = os.path.join(output_folder, f"{os.path.basename(pdf_path)[:-4]}.png")
    pillow_image.save(output_file, "PNG")

    # Close the PDF document
    pdf_document.close()

def create_poster_page(identifier, name):
    with open('detail.html', 'r') as file:
        detail_content = file.read()

    detail_content = detail_content.replace('{ #IDENTIFIER }', identifier)
    detail_content = detail_content.replace('{ #NAME }', name)

    with open(f'website/posters/{identifier}/index.html', 'w', encoding='utf-8') as output_file:
        output_file.write(detail_content)

def process_pdfs(input_folder):
    with open('index.html', 'r') as file:
        index_content = file.read()

    posters = []
    # Iterate through all PDF files in the input folder
    for filename in os.listdir(input_folder):
        if filename.endswith(".pdf"):
            textfilename = filename[:-3] + 'txt'
            if not os.path.isfile(os.path.join(input_folder, textfilename)):
                print(f'Skipping {filename} because textfile is missing')
                continue
            metadata = read_toml_file(os.path.join(input_folder, textfilename))
            if not metadata:
                continue
            pdf_path = os.path.join(input_folder, filename)
            identifier = filename[:-4]
            os.makedirs(f'website/posters/{identifier}', exist_ok=True)
            create_screenshot(pdf_path, f'website/posters/{identifier}')
            create_poster_page(identifier, metadata['name'])
            posters.append(identifier)
            print(f"Screenshot created for {filename}")

    listed_posters_for_index = '\n\n'.join(map(lambda p: f'<a href="/posters/{p}" class="poster"><img src="/posters/{p}/{p}.png" /></a>', posters))
    # Replace {CONTENT} with the specified string
    index_content = index_content.replace('{ #POSTERS }', listed_posters_for_index)

    # Write the modified content to the output file
    with open('website/index.html', 'w', encoding='utf-8') as output_file:
        output_file.write(index_content)


if __name__ == "__main__":
    input_folder = "queue"

    shutil.rmtree('website')
    os.makedirs('website', exist_ok=True)
    os.makedirs('website/posters', exist_ok=True)
    
    process_pdfs(input_folder)