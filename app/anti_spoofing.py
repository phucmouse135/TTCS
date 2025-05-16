import cv2
import numpy as np
from scipy.stats import entropy

class AntiSpoofing:
    def __init__(self):
        # Initialize parameters for anti-spoofing
        self.min_texture_variation = 18.0  # Further decreased minimum texture variation threshold
        self.max_reflection_ratio = 0.04   # Keeping this value as it is
        self.frame_similarity_threshold = 0.85  # Decreased threshold to detect subtle differences
        self.min_entropy = 5.2 # Further decreased minimum entropy for texture naturalness

    def check_image_depth(self, face_img):
        """
        Analyze image for depth cues using texture gradients and edge strength
        Returns a score (higher = more likely to be real)
        """
        # Convert to grayscale if needed
        if len(face_img.shape) == 3:
            gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
        else:
            gray = face_img.copy()
            
        # Calculate gradient magnitude
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        gradient_magnitude = np.sqrt(sobelx**2 + sobely**2)
        
        # Calculate average gradient strength as a measure of texture/depth
        avg_gradient = np.mean(gradient_magnitude)
        
        # Calculate Laplacian variance as a measure of focus/texture
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        lap_var = np.var(laplacian)
        
        # Combine scores (higher = more texture/depth cues = more likely real)
        depth_score = (avg_gradient + lap_var/100) / 2
        
        # Threshold to determine if image likely has depth
        return depth_score > self.min_texture_variation, depth_score

    def check_abnormal_reflections(self, face_img):
        """
        Check for abnormal light reflections that might indicate a screen
        Returns a score (lower = more likely to be real)
        """
        # Convert to HSV to better handle brightness
        if len(face_img.shape) == 3:
            hsv = cv2.cvtColor(face_img, cv2.COLOR_BGR2HSV)
            v_channel = hsv[:, :, 2]
        else:
            v_channel = face_img.copy()
        
        # Find bright spots (potential screen reflections)
        threshold = 240  # High brightness threshold
        bright_pixels = np.sum(v_channel > threshold)
        total_pixels = v_channel.size
        
        # Calculate ratio of bright pixels
        bright_ratio = bright_pixels / total_pixels
        
        # Check if ratio is below the threshold (fewer reflections = more likely real)
        return bright_ratio < self.max_reflection_ratio, bright_ratio

    def check_texture_naturalness(self, face_img):
        """
        Check texture naturalness using local binary patterns
        Printed/displayed faces tend to have more uniform texture
        """
        if len(face_img.shape) == 3:
            gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
        else:
            gray = face_img.copy()
            
        # Resize for faster processing
        resized = cv2.resize(gray, (128, 128))
        
        # Calculate texture uniformity using histograms of pixel intensities
        hist = cv2.calcHist([resized], [0], None, [256], [0, 256])
        hist = hist.flatten() / resized.size
        
        # Calculate entropy - higher entropy means more natural texture variation
        texture_entropy = entropy(hist)
        
        # Define threshold for good texture entropy
        texture_threshold = self.min_entropy  # Adjust based on testing
        
        return texture_entropy > texture_threshold, texture_entropy

    def compare_frames(self, frame1, frame2):
        """
        Compare two frames to detect static images (anti-spoofing)
        Returns True if frames are different enough to be from a live person
        """
        if frame1 is None or frame2 is None:
            return True, 0
            
        # Convert to grayscale for comparison
        if len(frame1.shape) == 3:
            gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        else:
            gray1 = frame1.copy()
            
        if len(frame2.shape) == 3:
            gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
        else:
            gray2 = frame2.copy()
            
        # Resize for consistent comparison
        if gray1.shape != gray2.shape:
            gray1 = cv2.resize(gray1, (128, 128))
            gray2 = cv2.resize(gray2, (128, 128))
        
        # Calculate structural similarity index (SSIM)
        try:
            from skimage.metrics import structural_similarity as ssim
            similarity, _ = ssim(gray1, gray2, full=True)
        except ImportError:
            # Fallback if scikit-image is not available
            # Calculate mean square difference
            diff = cv2.absdiff(gray1, gray2)
            diff_squared = diff.astype(float) ** 2
            mse = np.mean(diff_squared)
            if mse == 0:
                similarity = 1.0
            else:
                # Convert to similarity score (1.0 = identical)
                similarity = 1.0 - min(1.0, mse / 10000.0)
        
        # Check if frames are different enough
        # Lower similarity means more difference between frames (more likely to be real)
        is_live = similarity < self.frame_similarity_threshold
        
        return is_live, similarity

    def is_live_face(self, face_img, previous_face=None):
        """
        Comprehensive liveness check combining multiple techniques
        Returns (is_live, confidence, details)
        """
        results = {}
        
        # Check image depth
        has_depth, depth_score = self.check_image_depth(face_img)
        results['depth_check'] = {'passed': has_depth, 'score': depth_score}
        
        # Check abnormal reflections
        normal_reflections, reflection_ratio = self.check_abnormal_reflections(face_img)
        results['reflection_check'] = {'passed': normal_reflections, 'score': reflection_ratio}
        
        # Check texture naturalness
        natural_texture, texture_score = self.check_texture_naturalness(face_img)
        results['texture_check'] = {'passed': natural_texture, 'score': texture_score}
        
        # Check frame difference (if previous frame is provided)
        if previous_face is not None:
            frame_diff, similarity = self.compare_frames(face_img, previous_face)
            results['frame_diff_check'] = {'passed': frame_diff, 'score': similarity}
        else:
            # If no previous frame, consider this check passed
            results['frame_diff_check'] = {'passed': True, 'score': 0}
        
        # Calculate overall result
        # A face must pass depth check, reflection check and either texture check or frame diff check
        is_live = (results['depth_check']['passed'] and 
                  results['reflection_check']['passed'] and 
                  (results['texture_check']['passed'] or results['frame_diff_check']['passed']))
        
        # Calculate confidence score (0-100)
        confidence = (
            (1 if results['depth_check']['passed'] else 0) * 30 +
            (1 if results['reflection_check']['passed'] else 0) * 30 +
            (1 if results['texture_check']['passed'] else 0) * 20 +
            (1 if results['frame_diff_check']['passed'] else 0) * 20
        )
        
        return is_live, confidence, results
