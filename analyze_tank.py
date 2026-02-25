import cv2
import numpy as np
import os

def analyze(path):
    if not os.path.exists(path):
        print(f"{path} not found")
        return
    img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    print(f"File: {path}")
    print(f"Shape: {img.shape}")
    if img.shape[2] == 4:
        alpha = img[:, :, 3]
        print(f"Alpha channel: min={alpha.min()}, max={alpha.max()}, mean={alpha.mean()}")
    else:
        print("No alpha channel")

    # Try to find the "inner" rectangle if it's a frame
    gray = cv2.cvtColor(img[:,:,:3], cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        c = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(c)
        print(f"Largest bounding box: x={x}, y={y}, w={w}, h={h}")

print("Analyzing Tank.png...")
analyze('asset/Tank/Tank.png')
print("\nAnalyzing aquarium.png...")
analyze('asset/Tank/aquarium.png')
