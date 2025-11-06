from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import cv2
from multiprocessing import Pool


def split_image_grid(img_np, rows=3, cols=3):
    row_blocks = np.array_split(img_np, rows, axis=0)
    fragments = []

    for row in row_blocks:
        col_blocks = np.array_split(row, cols, axis=1)
        fragments.extend(col_blocks)

    return fragments

def merge_image_grid(fragments, rows=3, cols=3):
    merged_rows = []
    for i in range(rows):
        row = np.hstack(fragments[i*cols:(i+1)*cols])
        merged_rows.append(row)
    merged = np.vstack(merged_rows)
    return merged

def sobel_filter(image):
    Kx = np.array([[-1, 0, 1],
                   [-2, 0, 2],
                   [-1, 0, 1]], dtype=np.float32)
    Ky = np.array([[-1, -2, -1],
                   [0,  0,  0],
                   [1,  2,  1]], dtype=np.float32)

    Gx = cv2.filter2D(image, cv2.CV_32F, Kx)
    Gy = cv2.filter2D(image, cv2.CV_32F, Ky)

    magnitude = cv2.magnitude(Gx, Gy)

    result = cv2.convertScaleAbs(magnitude)
    return result

if __name__ == "__main__":
    img = Image.open("bird.jpg").convert("L")
    img_np = np.array(img)

    fragments = split_image_grid(img_np, 3, 3)

    with Pool(processes=4) as pool:
        sobel_fragments = pool.map(sobel_filter, fragments)

    merged_sobel = merge_image_grid(sobel_fragments, 3, 3)

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    axes[0].imshow(img_np, cmap='gray')
    axes[0].set_title("Original")
    axes[0].axis('off')

    axes[1].imshow(merge_image_grid(fragments, 3, 3), cmap='gray')
    axes[1].set_title("After merge (no filter)")
    axes[1].axis('off')

    axes[2].imshow(merged_sobel, cmap='gray')
    axes[2].set_title("Sobel filter (after merge)")
    axes[2].axis('off')

    plt.tight_layout()
    plt.show()
