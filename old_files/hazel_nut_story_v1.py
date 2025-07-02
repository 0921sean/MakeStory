from PIL import Image
import pandas as pd

def create_combined_image(image1_path, image2_path, output_path):
    # Load the images
    image1 = Image.open(image1_path)
    image2 = Image.open(image2_path)

    # Resize both images to have a width of 360 pixels
    resize_width = 360
    resize_height_image1 = int((resize_width / image1.width) * image1.height)
    resize_height_image2 = int((resize_width / image2.width) * image2.height)

    image1_resized = image1.resize((resize_width, resize_height_image1))
    image2_resized = image2.resize((resize_width, resize_height_image2))

    # Create a new blank image with 1080x1920 resolution and white background
    final_width = 1080
    final_height = 1920
    final_image = Image.new('RGB', (final_width, final_height), (251, 251, 251))

    # Paste the resized images onto the final image at the specified positions
    image1_position = (120, 607)  # Position for the first image
    image2_position = (600, 236)  # Position for the second image

    final_image.paste(image1_resized, image1_position)
    final_image.paste(image2_resized, image2_position)

    # Save the final combined image
    final_image.save(output_path)
    return output_path

# # Define the date for which the schedule images are to be combined
# today_date = '2025-02-23'

# input_image_path1 = './action_schedule/what-{today_date}.jpeg'.format(today_date=today_date)
# input_image_path2 = './time_schedule/when-{today_date}.jpeg'.format(today_date=today_date)

# # Define paths for input and output
# output_image_path = './remade_schedule/story-{today_date}.jpeg'.format(today_date=today_date)

# # Create the combined image with the specified inputs and layout
# create_combined_image(input_image_path1, input_image_path2, output_image_path)

# Create combined images for a range of dates
date_range = pd.date_range(start='2025-04-17', end='2025-04-22')

for date in date_range:
    today_date = date.strftime('%Y-%m-%d')  # Format date as 'YYYY-MM-DD'

    input_image_path1 = './action_schedule/what-{today_date}.jpeg'.format(today_date=today_date)
    input_image_path2 = './time_schedule/when-{today_date}.jpeg'.format(today_date=today_date)

    # Define paths for input and output
    output_image_path = './remade_schedule/story-{today_date}.jpeg'.format(today_date=today_date)

    # Create the combined image with the specified inputs and layout
    create_combined_image(input_image_path1, input_image_path2, output_image_path)