import numpy as np
import random
from skimage.io import imread, imsave
from scipy import signal
from PIL import Image, ImageEnhance, ImageOps

# Reconstruct the exact kernel from the original script
random.seed(420)
kernel = [[float(random.randint(-10,10)) for _ in range(19)] for _ in range(19)]
q = sum(sum(kernel, start=[]))
kernel = [[a / q for a in r] for r in kernel]
kernel = np.array(kernel)

# Load only the output image
output_img = imread("output.png")
print(f"Output image shape: {output_img.shape}")

# Extract the green channel
green_channel = output_img[:,:,1]

# Function to apply convolution and save result
def apply_conv_and_save(channel, kernel_variant, filename, do_invert=False, contrast=1.0):
    # Apply convolution
    conv_result = signal.convolve2d(channel, kernel_variant, mode='same')
    
    # Normalize to 0-255 range
    normalized = (conv_result - np.min(conv_result)) / (np.max(conv_result) - np.min(conv_result)) * 255.0
    
    # Apply inversion if requested
    if do_invert:
        normalized = 255 - normalized
    
    # Convert to uint8 for image processing
    img_result = np.uint8(normalized)
    
    # Apply contrast if requested
    if contrast != 1.0:
        pil_img = Image.fromarray(img_result)
        pil_img = ImageEnhance.Contrast(pil_img).enhance(contrast)
        img_result = np.array(pil_img)
    
    # Save the result
    imsave(filename, img_result)
    return img_result

# Center of the kernel
center = kernel.shape[0] // 2

# Recreate the original kernel_center_boost and kernel_center_boost_inv images
center_boost = kernel.copy()
center_boost[center-1:center+2, center-1:center+2] *= 1.5  # Boost center 3x3 region
center_boost = center_boost / np.sum(center_boost)  # Renormalize

apply_conv_and_save(green_channel, center_boost, "kernel_center_boost.png")
apply_conv_and_save(green_channel, center_boost, "kernel_center_boost_inv.png", do_invert=True)

# Now try more precise variations of the boost factor
for boost_factor in np.arange(1.1, 2.0, 0.05):  # 1.1 to 1.95 with 0.05 steps
    center_boosted = kernel.copy()
    center_boosted[center-1:center+2, center-1:center+2] *= boost_factor
    center_boosted = center_boosted / np.sum(center_boosted)
    
    apply_conv_and_save(green_channel, center_boosted, f"center_boost_{boost_factor:.2f}.png")
    apply_conv_and_save(green_channel, center_boosted, f"center_boost_{boost_factor:.2f}_inv.png", do_invert=True)

# Try different sized center regions
for size in [1, 2, 3, 4, 5]:
    region_boost = kernel.copy()
    region_boost[center-size:center+size+1, center-size:center+size+1] *= 1.5
    region_boost = region_boost / np.sum(region_boost)
    
    apply_conv_and_save(green_channel, region_boost, f"center_boost_size{size*2+1}.png")
    apply_conv_and_save(green_channel, region_boost, f"center_boost_size{size*2+1}_inv.png", do_invert=True)

# Try boosting just the center pixel itself
center_pixel_boost = kernel.copy()
center_pixel_boost[center, center] *= 5.0  # Higher boost for single pixel
center_pixel_boost = center_pixel_boost / np.sum(center_pixel_boost)

apply_conv_and_save(green_channel, center_pixel_boost, "center_pixel_boost.png")
apply_conv_and_save(green_channel, center_pixel_boost, "center_pixel_boost_inv.png", do_invert=True)

# Try center boost with contrast enhancement
for contrast in [1.5, 2.0, 2.5, 3.0]:
    apply_conv_and_save(green_channel, center_boost, f"center_boost_contrast{contrast:.1f}.png", contrast=contrast)
    apply_conv_and_save(green_channel, center_boost, f"center_boost_contrast{contrast:.1f}_inv.png", do_invert=True, contrast=contrast)

# Try applying a threshold after convolution
for thresh in range(135, 175, 5):
    # Apply convolution
    conv_result = signal.convolve2d(green_channel, center_boost, mode='same')
    
    # Normalize to 0-255 range
    normalized = (conv_result - np.min(conv_result)) / (np.max(conv_result) - np.min(conv_result)) * 255.0
    img_result = np.uint8(normalized)
    
    # Apply threshold
    binary = (img_result > thresh).astype(np.uint8) * 255
    imsave(f"center_boost_thresh_{thresh}.png", binary)
    
    # Also try inverting before threshold
    inverted = 255 - img_result
    binary = (inverted > thresh).astype(np.uint8) * 255
    imsave(f"center_boost_thresh_{thresh}_inv.png", binary)

# Try pattern-based center boosting
patterns = [
    ("cross", np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]])),
    ("x", np.array([[1, 0, 1], [0, 1, 0], [1, 0, 1]]))
]

for name, pattern in patterns:
    pattern_boost = kernel.copy()
    for i in range(3):
        for j in range(3):
            if pattern[i, j] == 1:
                pattern_boost[center-1+i, center-1+j] *= 2.0
    
    pattern_boost = pattern_boost / np.sum(pattern_boost)
    apply_conv_and_save(green_channel, pattern_boost, f"pattern_{name}.png")
    apply_conv_and_save(green_channel, pattern_boost, f"pattern_{name}_inv.png", do_invert=True)

print("Generated variations of kernel center boost images. Check for the flag.") 