import cv2
import numpy as np
from kivy.logger import Logger


def blend_transparent(face_img, overlay_t_img):
    # Split out the transparency mask from the colour info
    overlay_img = overlay_t_img[:,:,:3] # Grab the BRG planes
    overlay_mask = overlay_t_img[:,:,3:]  # And the alpha plane

    # Again calculate the inverse mask
    background_mask = 255 - overlay_mask

    # Turn the masks into three channel, so we can use them as weights
    overlay_mask = cv2.cvtColor(overlay_mask, cv2.COLOR_GRAY2BGR)
    background_mask = cv2.cvtColor(background_mask, cv2.COLOR_GRAY2BGR)

    # Create a masked out face image, and masked out overlay
    # We convert the images to floating point in range 0.0 - 1.0
    face_part = (face_img[:,:,:3] * (1 / 255.0)) * (background_mask * (1 / 255.0))
    overlay_part = (overlay_img * (1 / 255.0)) * (overlay_mask * (1 / 255.0))

    # And finally just add them together, and rescale it back to an 8bit integer image
    return np.uint8(cv2.addWeighted(face_part, 255.0, overlay_part, 255.0, 0.0))


def out_shadow(image, image_for_shape):
    height, width, _ = image.shape
    Logger.debug('\n\n\n\n\nWORK NORMAL\n\n\n\n')
    image_yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
    image_y = np.zeros(image_yuv.shape[0:2], np.uint8)
    image_y[:, :] = image_yuv[:, :, 0]
    image_blurred = cv2.GaussianBlur(image_y, (3, 3), 0)
    edges = cv2.Canny(image_blurred, 100, 300, apertureSize=3)
    Logger.debug('\n\n\n\n\nWORK NORMAL\n\n\n\n')
    contours, hierarchy = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnt = max(contours, key=cv2.contourArea)
    hull = cv2.convexHull(cnt)
    simplified_cnt = cv2.approxPolyDP(hull, 0.03 * cv2.arcLength(hull, True), True)
    height, width, _ = image_for_shape.shape
    (H, mask) = cv2.findHomography(np.array([[[width, height]], [[0, height]], [[0, 0]], [[width, 0]]], dtype=np.single), simplified_cnt)
    # height, width, _ = image_for_shape.shape
    height, width, _ = image.shape
    final_image = cv2.warpPerspective(image_for_shape, H, (width, height))
    # final_image = cv2.flip(np.rot90(final_image, 1), 1)
    # return final_image
    return final_image


def find_shadow(image, image_for_shape):
    height, width, _ = image_for_shape.shape
    image_yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
    image_y = np.zeros(image_yuv.shape[0:2], np.uint8)
    image_y[:, :] = image_yuv[:, :, 0]
    image_blurred = cv2.GaussianBlur(image_y, (3, 3), 0)
    edges = cv2.Canny(image_blurred, 100, 300, apertureSize=3)
    _, contours, hierarchy = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnt = max(contours, key=cv2.contourArea)
    hull = cv2.convexHull(cnt)
    simplified_cnt = cv2.approxPolyDP(hull, 0.03 * cv2.arcLength(hull, True), True)

    (H, mask) = cv2.findHomography(simplified_cnt.astype('single'),
                                   np.array([[[0, 0]], [[0, width]], [[height, width]], [[height, 0]]], dtype=np.single))
    final_image = cv2.warpPerspective(image, H, (height, width))
    final_image = cv2.flip(np.rot90(final_image, 1), 1)
    return final_image