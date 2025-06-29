from PIL import Image, ImageDraw

def crop_circle(img_path, output_path):
    img = Image.open(img_path).convert("RGBA")
    size = min(img.size)
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size, size), fill=255)

    img = img.crop(((img.width - size)//2, (img.height - size)//2,
                    (img.width + size)//2, (img.height + size)//2))
    img.putalpha(mask)
    img.save(output_path)

# 예시 사용
crop_circle("speaker8.png", "speaker_circle8.png")