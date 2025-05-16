"""
Comprehensive script to train the face recognition model and verify it works
"""
import os
import sys
import cv2
import numpy as np
import pandas as pd
from datetime import datetime
import time

def train_and_verify():
    """Train the model and verify recognition works"""
    try:
        # Add app directory to path
        sys.path.append(os.path.abspath(''))
        
        # Import face recognition module
        from app.enhanced_face_recognition import EnhancedFaceRecognition
        
        print("======= FACE RECOGNITION TRAINING AND VERIFICATION =======")
        print("Step 1: Creating Enhanced Face Recognition instance...")
        
        # Create enhanced face recognition instance
        face_rec = EnhancedFaceRecognition()
        
        print("\nStep 2: Training the face recognition model...")
        # Train the model
        success, message = face_rec.train_model()
        
        if not success:
            print("Model training failed:")
            print(message)
            return False
            
        print(f"Face recognition model training successful: {message}")

        print("\nStep 3: Testing recognition with camera and enhanced anti-spoofing...")
        print("Opening camera to test face recognition and anti-spoofing...")
        print("Press ESC to exit the test")
        
        # Test recognition with camera
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Cannot open camera")
            return False
        
        # Recognition loop
        frame_count = 0
        recognized_count = 0
        spoof_attempts = 0
        
        while frame_count < 100:  # Process max 100 frames
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame")
                break
            
            # Make a copy for display
            display_frame = frame.copy()
            
            # Extract faces
            faces = face_rec.extract_face(frame)
            
            # Process detected faces
            for face_img, face_box in faces:
                # Perform anti-spoofing check
                is_live, liveness_score, spoof_details = face_rec.anti_spoofing.is_live_face(face_img)
                
                x1, y1, x2, y2 = face_box
                
                if is_live:
                    # Try to recognize the face
                    match_result = face_rec.recognize_face(face_img)
                    
                    # Draw rectangle around face
                    cv2.rectangle(display_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    
                    if match_result is not None:
                        student_code, name, similarity = match_result
                        recognized_count += 1
                        
                        # Display recognition results
                        cv2.putText(display_frame, f"Student: {name}", (x1, y1 - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                        cv2.putText(display_frame, f"Similarity: {similarity:.2f}", (x1, y1 - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                        cv2.putText(display_frame, f"Liveness: {liveness_score}", (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    else:
                        # Display "Unknown" for unrecognized faces
                        cv2.putText(display_frame, "Unknown (Live)", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                else:
                    # Draw red rectangle around potential spoof face
                    cv2.rectangle(display_frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                    cv2.putText(display_frame, "FAKE - Not a live face", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    spoof_attempts += 1
            
            # Show the frame
            cv2.imshow("Face Recognition Test", display_frame)
            
            # Check for exit key
            key = cv2.waitKey(100)  # Wait for 100ms
            if key == 27:  # ESC key
                break
            
            frame_count += 1
            
            # Brief pause to make results readable
            time.sleep(0.1)
        
        # Clean up
        cap.release()
        cv2.destroyAllWindows()
        
        print(f"\nTest complete: {recognized_count} successful recognitions in {frame_count} frames")
        print(f"Spoof attempts detected: {spoof_attempts}")
        print("Face recognition system is " + ("working properly" if recognized_count > 0 else "NOT working correctly"))
        
        return recognized_count > 0
    
    except Exception as e:
        import traceback
        print(f"Error in train_and_verify: {e}")
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    result = train_and_verify()
    
    if result:
        print("\nSUCCESS: Face recognition is working correctly!")
    else:
        print("\nWARNING: Face recognition may not be working correctly.")
    
    input("\nPress Enter to exit...")
