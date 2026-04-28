import cv2
import numpy as np
from PIL import Image


def calculate_damage(img_path):
    try:
        img = cv2.imread(img_path)
        if img is None:
            img = np.array(Image.open(img_path).convert("RGB"))
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # Green (healthy)
        green_lower = np.array([35, 40, 40])
        green_upper = np.array([85, 255, 255])
        green_mask  = cv2.inRange(hsv, green_lower, green_upper)

        # Brown/Red (redrot)
        brown_lower = np.array([0, 40, 40])
        brown_upper = np.array([20, 255, 200])
        brown_mask  = cv2.inRange(hsv, brown_lower, brown_upper)

        # Yellow (yellow leaf)
        yellow_lower = np.array([20, 40, 40])
        yellow_upper = np.array([35, 255, 255])
        yellow_mask  = cv2.inRange(hsv, yellow_lower, yellow_upper)

        # Dark/Black (rust, severe)
        dark_lower = np.array([0, 0, 0])
        dark_upper = np.array([180, 255, 60])
        dark_mask  = cv2.inRange(hsv, dark_lower, dark_upper)

        total_pixels   = img.shape[0] * img.shape[1]
        green_pixels   = cv2.countNonZero(green_mask)
        damaged_pixels = (cv2.countNonZero(brown_mask) +
                          cv2.countNonZero(yellow_mask) +
                          cv2.countNonZero(dark_mask))

        damage_pct = round((damaged_pixels / total_pixels) * 100, 1)
        damage_pct = min(damage_pct, 100.0)

        if damage_pct < 10:
            severity = "Mild"
        elif damage_pct < 35:
            severity = "Moderate"
        else:
            severity = "Severe"

        return {
            "damage_percent": damage_pct,
            "severity":       severity,
            "green_pixels":   green_pixels,
            "damaged_pixels": damaged_pixels,
            "total_pixels":   total_pixels,
        }

    except Exception as e:
        return {
            "damage_percent": 0.0,
            "severity":       "Mild",
            "green_pixels":   0,
            "damaged_pixels": 0,
            "total_pixels":   0,
        }