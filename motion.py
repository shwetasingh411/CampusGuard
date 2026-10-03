"""Reusable frame-difference movement detector."""
import cv2


class MotionDetector:
    def __init__(self, threshold_pixels=5000, pixel_threshold=25):
        self.threshold_pixels = threshold_pixels
        self.pixel_threshold = pixel_threshold
        self.previous_frame = None

    def detect(self, frame):
        if frame is None or frame.size == 0:
            raise ValueError("detect() received an empty frame")
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        movement = False
        if self.previous_frame is not None and self.previous_frame.shape == gray.shape:
            diff = cv2.absdiff(self.previous_frame, gray)
            _, mask = cv2.threshold(diff, self.pixel_threshold, 255, cv2.THRESH_BINARY)
            movement = cv2.countNonZero(mask) > self.threshold_pixels
        self.previous_frame = gray
        return movement
