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
def apply_conv_and_save(channel, kernel_variant, filename, do_invert=False, contrast=1.0, threshold=None):
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
    
    # Apply threshold if specified
    if threshold is not None:
        img_result = (img_result > threshold).astype(np.uint8) * 255
    
    # Save the result
    imsave(filename, img_result)
    return img_result

# Center of the kernel
center = kernel.shape[0] // 2

# 1. Use very precise boost factors for the 3x3 center region
for boost_factor in np.arange(1.45, 1.55, 0.01):  # 1.45-1.55 with finer 0.01 steps
    center_boost = kernel.copy()
    center_boost[center-1:center+2, center-1:center+2] *= boost_factor  # Boost center 3x3 region
    center_boost = center_boost / np.sum(center_boost)  # Renormalize
    
    # Save normal and inverted versions
    apply_conv_and_save(green_channel, center_boost, f"final_boost_{boost_factor:.2f}.png")
    apply_conv_and_save(green_channel, center_boost, f"final_boost_{boost_factor:.2f}_inv.png", do_invert=True)

# 2. Use the optimal boost factor of 1.5 with very precise threshold values
center_boost = kernel.copy()
center_boost[center-1:center+2, center-1:center+2] *= 1.5
center_boost = center_boost / np.sum(center_boost)

# Apply finer threshold values
for threshold in range(145, 166):
    # Normal image with threshold
    apply_conv_and_save(green_channel, center_boost, f"final_thresh_{threshold}.png", threshold=threshold)
    
    # Inverted image with threshold
    apply_conv_and_save(green_channel, center_boost, f"final_thresh_{threshold}_inv.png", 
                        do_invert=True, threshold=threshold)

# 3. Combine center boost, inversion, and specific contrast levels
for contrast in np.arange(1.8, 2.2, 0.05):
    # Apply contrast to original image
    apply_conv_and_save(green_channel, center_boost, f"final_contrast_{contrast:.2f}.png", contrast=contrast)
    
    # Apply contrast to inverted image
    apply_conv_and_save(green_channel, center_boost, f"final_contrast_{contrast:.2f}_inv.png", 
                       do_invert=True, contrast=contrast)

# 4. Boost only specific parts of the center region
# Try boosting only the center row, column, or specific pixels
variations = [
    ("center_only", np.array([[1, 1, 1], [1, 3, 1], [1, 1, 1]])),
    ("row", np.array([[1, 1, 1], [2, 2, 2], [1, 1, 1]])),
    ("col", np.array([[1, 2, 1], [1, 2, 1], [1, 2, 1]])),
    ("corners", np.array([[2, 1, 2], [1, 1, 1], [2, 1, 2]])),
    ("center_strong", np.array([[0.5, 0.5, 0.5], [0.5, 5, 0.5], [0.5, 0.5, 0.5]]))
]

for name, pattern in variations:
    custom_kernel = kernel.copy()
    # Apply the pattern to the center region
    for i in range(3):
        for j in range(3):
            custom_kernel[center-1+i, center-1+j] *= pattern[i, j]
    
    # Normalize
    custom_kernel = custom_kernel / np.sum(custom_kernel)
    
    # Apply and save
    apply_conv_and_save(green_channel, custom_kernel, f"final_pattern_{name}.png")
    apply_conv_and_save(green_channel, custom_kernel, f"final_pattern_{name}_inv.png", do_invert=True)
    
    # Also try with thresholds
    for threshold in [150, 155, 160]:
        apply_conv_and_save(green_channel, custom_kernel, f"final_pattern_{name}_thresh_{threshold}.png", 
                           threshold=threshold)
        apply_conv_and_save(green_channel, custom_kernel, f"final_pattern_{name}_thresh_{threshold}_inv.png", 
                           do_invert=True, threshold=threshold)

# 5. Boost center with contrast and auto-levels
center_result = apply_conv_and_save(green_channel, center_boost, "final_base.png")
inv_center_result = apply_conv_and_save(green_channel, center_boost, "final_base_inv.png", do_invert=True)

# Convert to PIL for auto-levels
pil_center = Image.fromarray(center_result)
pil_inv = Image.fromarray(inv_center_result)

# Apply auto-contrast
auto_center = ImageOps.autocontrast(pil_center)
auto_inv = ImageOps.autocontrast(pil_inv)

# Save auto-contrast versions
auto_center.save("final_auto.png")
auto_inv.save("final_auto_inv.png")

# Apply thresholds to auto-contrast versions
for threshold in range(145, 166, 5):
    center_array = np.array(auto_center)
    inv_array = np.array(auto_inv)
    
    binary = (center_array > threshold).astype(np.uint8) * 255
    imsave(f"final_auto_thresh_{threshold}.png", binary)
    
    binary_inv = (inv_array > threshold).astype(np.uint8) * 255
    imsave(f"final_auto_thresh_{threshold}_inv.png", binary_inv)

print("Generated final kernel center boost variations. Check for the flag.") 