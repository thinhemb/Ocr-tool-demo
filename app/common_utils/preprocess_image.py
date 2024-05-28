# from skimage.filters import threshold_sauvola
# from skimage import img_as_ubyte
# from scipy.ndimage import gaussian_filter

import numpy as np
import cv2


def remove_noise(img):
    img = cv2.GaussianBlur(img, (5, 5), 0)
    return img


def equalize(img):
    equalized_image = cv2.equalizeHist(img)
    return equalized_image


# def convert_to_bin(img_gray):
#     window_size = 25
#
#     # thresh_niblack = threshold_niblack(img_gray, window_size=window_size, k=0.8)
#     thresh_sauvola = threshold_sauvola(img_gray, window_size=window_size)
#
#     # binary_global = img_gray > threshold_otsu(img_gray)
#     # binary_niblack = img_gray > thresh_niblack
#     binary_sauvola = img_gray > thresh_sauvola
#
#     img_bw = binary_sauvola.astype(np.uint8)
#     img_bw *= 255
#
#     return img_bw


def remove_noise_bw(img_bw):
    h, w = img_bw.shape[:2]
    mask = np.zeros((h + 2, w + 2), dtype=np.uint8)
    holes = cv2.floodFill(img_bw.copy(), mask, (0, 0), 255)[1]
    holes = ~holes
    img_bw[holes == 255] = 255

    return img_bw


def thinning(img_gray):
    kernel = np.ones((5, 5), np.uint8)
    erosion = cv2.erode(img_gray, kernel, iterations=1)
    return erosion


def convert_bin_to_rgb(img_bw):
    # rgb_image = np.repeat(img_bw[:, :, np.newaxis], 3, axis=2)
    # rgb_image = cv2.cvtColor(rgb_image, cv2.COLOR_GRAY2RGB)
    rgb_image = np.stack([img_bw, img_bw, img_bw], axis=-1)

    return rgb_image


def increase_light(img):
    # Convert the image to HSV
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)

    # Increase the brightness by scaling the V channel
    hsv[:, :, 2] = np.clip(hsv[:, :, 2] * 1.2, 0, 255)

    # Convert the image back to BGR
    bright_img = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
    return bright_img


def increase_resolution(img, times=2):
    return cv2.resize(img, None, fx=times, fy=times, interpolation=cv2.INTER_CUBIC)


def preprocess_image(image):
    # image = equalize(image)

    image = increase_resolution(image)
    image = increase_light(image)
    # image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    # image = equalize(image)
    # image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)

    # image = remove_noise(image)
    # image = convert_to_bin(image)

    # image = thinning(image)

    # image = remove_noise_bw(image)
    # image = convert_bin_to_rgb(image)

    return image
