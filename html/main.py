import os

def generate_html_file(image_size, image_count):
    """
    Generate HTML file for the specified image size and number of images.
    """
    images_path = f"./src/src{image_size}"
    images = sorted([file for file in os.listdir(images_path) if file.endswith('.jpg')])[:image_count]

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Image {image_size} ({image_count} images)</title>
</head>
<body>
"""
    for image in images:
        html_content += f'    <img src="{images_path}/{image}" alt="Image {image}">\n'
    
    html_content += """</body>
</html>
"""
    
    with open(f"index_{image_size}_{image_count}.html", "w") as html_file:
        html_file.write(html_content)

def main():
    # maps image size to the number of images
    image_sizes = ["5KB", "10KB", "100KB", "200KB", "500KB", "1MB", "10MB", "5KB", "10KB", "100KB", "200KB", "500KB"]
    image_counts = [5, 5, 5, 5, 5, 5, 5, 200, 100, 10, 5, 2]  
    
    for size, count in zip(image_sizes, image_counts):
        generate_html_file(size, count)

if __name__ == "__main__":
    main()
