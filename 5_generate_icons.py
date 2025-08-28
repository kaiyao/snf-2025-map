from PIL import Image, ImageDraw, ImageFont

def generate_icon_with_text(template_path, output_path, text_to_add):
    font_size = 120
    text_color = (0,0,0) # Black color (R, G, B)

    try:
        # Open the image file
        with Image.open(template_path) as img:
            # Get the image dimensions
            img_width, img_height = img.size

            # Create a drawing context
            draw = ImageDraw.Draw(img)

            # Specify a font
            try:
                # You can use a path to a custom .ttf font file
                font = ImageFont.truetype("fonts/desktop/ProdigySans-SemiBold.otf", font_size)
            except IOError:
                print("Arial font not found. Using default font.")
                font = ImageFont.load_default()

            # Calculate the center coordinates of the image
            text_center_x = img_width // 2
            text_center_y = img_height // 2 * 1.1 # Slightly lower than exact center

            # Draw the text at the center, using the 'mm' (middle-middle) anchor
            draw.text(
                (text_center_x, text_center_y),
                text_to_add,
                fill=text_color,
                font=font,
                anchor="mm" # Sets the text's center point to xy
            )

            # Save the modified image
            img.save(output_path)
            print(f"Image saved successfully with centered text to {output_path}")

    except FileNotFoundError:
        print(f"Error: The file '{template_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

icon_templates = ['icon_experiential_programmes.png',
 'icon_festival_villages.png',
 'icon_highlight_experiences.png',
 'icon_national_day_activations.png',
 'icon_night_lights.png',
 'icon_performances.png',
 'icon_projection_mapping.png']

for icon_template in icon_templates:
    for number in range(1, 50):
        output_icon = icon_template.replace('.png', f'_{number}.png')
        generate_icon_with_text(f'icons/template/{icon_template}', f'icons/generated/{output_icon}', str(number))
