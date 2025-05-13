"""
Standalone script to train the face recognition model
"""
import os
import sys
import cv2
import numpy as np
import pandas as pd
from datetime import datetime

def train_model():
    """Train the face recognition model"""
    try:
        # Add app directory to path
        sys.path.append(os.path.abspath(''))
        
        # Import face recognition module
        from app.face_recognition import FaceRecognition
        
        # Create face recognition instance
        face_rec = FaceRecognition()
        
        # Train the model
        success, message = face_rec.train_model()
        
        if success:
            print("Model training successful:")
            print(message)
        else:
            print("Model training failed:")
            print(message)
            
    except Exception as e:
        import traceback
        print(f"Error in train_model: {e}")
        print(traceback.format_exc())

if __name__ == "__main__":
    train_model()
    input("Press Enter to exit...")
