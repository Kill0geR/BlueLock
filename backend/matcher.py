"""
BlueLock - Screen Matcher
Uses OpenCV to compare screenshots and find matching saved credentials
"""

import cv2
import numpy as np
import base64


class ScreenMatcher:
    def __init__(self, threshold: float = 0.65):
        """
        threshold: minimum similarity score (0-1) to consider a match
        0.65 = 65% similar → good balance between strict and loose matching
        """
        self.threshold = threshold

    def find_match(self, current_screenshot: np.ndarray, entries: list) -> dict | None:
        """
        Compare current screenshot against all saved screenshots.
        Returns the best matching entry or None.
        
        Args:
            current_screenshot: numpy array (BGR) of current screen
            entries: list of vault entries with screenshot_b64
        
        Returns:
            Best matching entry dict or None
        """
        best_match = None
        best_score = 0.0

        for entry in entries:
            if not entry.get("screenshot_b64"):
                continue

            try:
                saved_screenshot = self._b64_to_cv2(entry["screenshot_b64"])
                score = self._compare(current_screenshot, saved_screenshot)

                print(f"[Matcher] {entry['app_name']}: {score:.2f}")

                if score > best_score and score >= self.threshold:
                    best_score = score
                    best_match = entry

            except Exception as e:
                print(f"[Matcher] Fehler bei {entry['app_name']}: {e}")
                continue

        if best_match:
            print(f"[Matcher] ✓ Match gefunden: {best_match['app_name']} ({best_score:.2f})")
        else:
            print(f"[Matcher] ✗ Kein Match gefunden (bester Score: {best_score:.2f})")

        return best_match

    def _compare(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """
        Compare two screenshots using multiple methods for better accuracy.
        Returns similarity score between 0 and 1.
        """
        # Resize both to same size for comparison
        target_size = (640, 480)
        img1_resized = cv2.resize(img1, target_size)
        img2_resized = cv2.resize(img2, target_size)

        # Method 1: Histogram comparison (good for overall color/layout)
        hist_score = self._histogram_similarity(img1_resized, img2_resized)

        # Method 2: Structural similarity on grayscale (good for UI structure)
        struct_score = self._structural_similarity(img1_resized, img2_resized)

        # Method 3: Feature matching with ORB (good for specific UI elements)
        feature_score = self._feature_similarity(img1_resized, img2_resized)

        # Weighted average: structure matters most, then features, then color
        final_score = (struct_score * 0.5) + (feature_score * 0.3) + (hist_score * 0.2)
        
        return final_score

    def _histogram_similarity(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """Compare color histograms"""
        scores = []
        for channel in range(3):  # B, G, R
            hist1 = cv2.calcHist([img1], [channel], None, [256], [0, 256])
            hist2 = cv2.calcHist([img2], [channel], None, [256], [0, 256])
            cv2.normalize(hist1, hist1)
            cv2.normalize(hist2, hist2)
            score = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
            scores.append(max(0, score))  # Can be negative, clamp to 0
        return sum(scores) / len(scores)

    def _structural_similarity(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """Compare structural similarity on grayscale images"""
        gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
        
        # Normalize
        gray1 = gray1.astype(np.float32) / 255.0
        gray2 = gray2.astype(np.float32) / 255.0
        
        # Simple normalized cross-correlation
        result = cv2.matchTemplate(gray1, gray2, cv2.TM_CCOEFF_NORMED)
        score = float(np.max(result))
        return max(0, score)

    def _feature_similarity(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """Compare features using ORB detector"""
        try:
            orb = cv2.ORB_create(nfeatures=500)
            gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

            kp1, des1 = orb.detectAndCompute(gray1, None)
            kp2, des2 = orb.detectAndCompute(gray2, None)

            if des1 is None or des2 is None or len(kp1) < 10 or len(kp2) < 10:
                return 0.0

            # BFMatcher for ORB (Hamming distance)
            bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
            matches = bf.match(des1, des2)

            if not matches:
                return 0.0

            # Good matches = distance < 50
            good_matches = [m for m in matches if m.distance < 50]
            score = len(good_matches) / max(len(kp1), len(kp2))
            return min(1.0, score * 3)  # Scale up slightly

        except Exception:
            return 0.0

    def _b64_to_cv2(self, b64_string: str) -> np.ndarray:
        """Convert base64 string to OpenCV image"""
        img_data = base64.b64decode(b64_string)
        img_array = np.frombuffer(img_data, np.uint8)
        return cv2.imdecode(img_array, cv2.IMREAD_COLOR)
