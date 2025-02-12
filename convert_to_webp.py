import os
from PIL import Image
from django.core.files import File
from blogs.models import Blog  # Update with your actual app name

def convert_existing_images():
    blogs = Blog.objects.all()

    for blog in blogs:
        if blog.image:  # Check if image exists
            img_path = blog.image.path
            if not img_path.endswith(".webp"):  # Skip already converted images
                try:
                    img = Image.open(img_path)
                    webp_path = os.path.splitext(img_path)[0] + ".webp"

                    img.save(webp_path, "WEBP", quality=80)  # Convert and save

                    # Update model to use new WEBP file
                    blog.image.name = os.path.splitext(blog.image.name)[0] + ".webp"
                    blog.save(update_fields=["image"])

                    # Delete the old file
                    if os.path.exists(img_path):
                        os.remove(img_path)

                    print(f"Converted: {img_path} → {webp_path}")

                except Exception as e:
                    print(f"Error converting {img_path}: {e}")

convert_existing_images()
