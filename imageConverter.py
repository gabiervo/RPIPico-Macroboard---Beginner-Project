from PIL import Image


image_dir = input("what is the directory of your image?")
# Open the BMP image
bmp_image = Image.open(image_dir)
# Convert the image to monochrome (1-bit)
monochrome_image = bmp_image.convert('1')
# Save the monochrome image back to the same file
monochrome_image.save(image_dir + ".bmp")