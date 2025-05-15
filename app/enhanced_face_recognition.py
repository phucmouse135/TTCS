"""
Enhanced Face Recognition module with anti-spoofing capabilities
This module builds on the existing face_recognition.py to add anti-spoofing features
"""

import os
import cv2
import numpy as np
import torch
from datetime import datetime
from app.face_recognition import FaceRecognition
from app.anti_spoofing import AntiSpoofing

class EnhancedFaceRecognition(FaceRecognition):
    """
    Enhanced version of FaceRecognition class with anti-spoofing features
    """
    def __init__(self, data_dir='data/faces', database_path='data/face_database.csv'):
        super().__init__(data_dir, database_path)
        # Initialize the anti-spoofing module
        self.anti_spoofing = AntiSpoofing()
        
    def process_video_feed(self, schedule_id, update_callback=None):
        """Process video feed for attendance with anti-spoofing checks"""
        try:
            # Open camera
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                return False, "Cannot open camera"
            
            # Initialize variables
            recognized_students = {}
            running = True
            frame_count = 0
            
            # For anti-spoofing: store previous face images for face tracking and analysis
            previous_faces = {}  # Format: {face_id: {'img': face_img, 'box': face_box, 'time': timestamp}}
            face_id_counter = 0  # Counter to assign unique IDs to faces
            
            # Face detection and recognition loop
            while running and frame_count < 150:  # Process max 150 frames
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Make a copy for display
                display_frame = frame.copy()
                
                # Extract faces using OpenCV instead of MTCNN
                faces = self.extract_face(frame)
                
                # Current faces in this frame (for tracking)
                current_face_ids = []
                
                # Process detected faces
                for face_img, face_box in faces:
                    # Generate a simple face identifier based on position
                    x1, y1, x2, y2 = face_box
                    face_center = ((x1 + x2) // 2, (y1 + y2) // 2)
                    
                    # Find closest previous face, if any
                    best_match_id = None
                    best_match_dist = float('inf')
                    
                    for face_id, data in previous_faces.items():
                        prev_box = data['box']
                        prev_x1, prev_y1, prev_x2, prev_y2 = prev_box
                        prev_center = ((prev_x1 + prev_x2) // 2, (prev_y1 + prev_y2) // 2)
                        
                        # Calculate distance between face centers
                        dist = np.sqrt((face_center[0] - prev_center[0])**2 + 
                                       (face_center[1] - prev_center[1])**2)
                        
                        # If close enough, consider it the same face
                        if dist < 50 and dist < best_match_dist:  # 50 pixels threshold
                            best_match_dist = dist
                            best_match_id = face_id
                    
                    # Assign face ID - either existing or new
                    if best_match_id is not None:
                        face_id = best_match_id
                        prev_face = previous_faces[face_id]['img']
                    else:
                        face_id = f"face_{face_id_counter}"
                        face_id_counter += 1
                        prev_face = None
                    
                    current_face_ids.append(face_id)
                    
                    # Perform anti-spoofing check
                    is_live, liveness_score, spoof_details = self.anti_spoofing.is_live_face(face_img, prev_face)
                    
                    # Update previous face data
                    previous_faces[face_id] = {
                        'img': face_img,
                        'box': face_box,
                        'time': datetime.now(),
                        'is_live': is_live,
                        'liveness_score': liveness_score
                    }
                    
                    # Only proceed with recognition if the face passes liveness check
                    if is_live:
                        # Try to recognize the face
                        match_result = self.recognize_face(face_img)
                        
                        # Draw green rectangle around live face
                        cv2.rectangle(display_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        
                        if match_result is not None:
                            student_code, name, similarity = match_result
                            
                            # Use dictionary-style access only if embeddings is properly structured
                            if isinstance(self.embeddings, dict) and student_code in self.embeddings and isinstance(self.embeddings[student_code], dict):
                                name = self.embeddings[student_code]['name']
                            else:
                                # Try to get name from dataframe instead
                                try:
                                    student_row = self.df[self.df['student_code'] == student_code].iloc[0]
                                    name = str(student_row['name'])
                                except:
                                    name = "Unknown"
                            
                            # Current timestamp
                            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            
                            # Mark attendance for the recognized student
                            if student_code not in recognized_students:
                                recognized_students[student_code] = {
                                    'name': name,
                                    'similarity': similarity,
                                    'count': 1,
                                    'timestamp': current_time,
                                    'liveness_score': liveness_score
                                }
                            else:
                                recognized_students[student_code]['count'] += 1
                                if similarity > recognized_students[student_code]['similarity']:
                                    recognized_students[student_code]['similarity'] = similarity
                                    recognized_students[student_code]['liveness_score'] = max(
                                        recognized_students[student_code]['liveness_score'], 
                                        liveness_score
                                    )
                            
                            # Display recognition results
                            cv2.putText(display_frame, f"Student: {name}", (x1, y1 - 40), 
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                            cv2.putText(display_frame, f"Similarity: {similarity:.2f}", (x1, y1 - 20), 
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                            cv2.putText(display_frame, f"Liveness: {liveness_score}", (x1, y1), 
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                        else:
                            # Display "Unknown" for unrecognized faces
                            cv2.putText(display_frame, "Unknown (Live)", (x1, y1 - 10), 
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                    else:
                        # Draw red rectangle around potential spoof face
                        cv2.rectangle(display_frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                        cv2.putText(display_frame, "FAKE - Not a live face", (x1, y1 - 10), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
                # Remove faces that are no longer visible
                for face_id in list(previous_faces.keys()):
                    if face_id not in current_face_ids:
                        # Keep for a few frames in case face temporarily disappears
                        time_diff = (datetime.now() - previous_faces[face_id]['time']).total_seconds()
                        if time_diff > 2.0:  # Remove after 2 seconds
                            del previous_faces[face_id]
                
                # Show the frame
                cv2.imshow("Attendance", display_frame)
                
                # Check for exit key
                key = cv2.waitKey(1)
                if key == 27:  # ESC key
                    running = False
                
                frame_count += 1
            
            # Clean up
            cap.release()
            cv2.destroyAllWindows()
            
            # Return results
            if not recognized_students:
                return False, "No students recognized"
            
            # Convert recognized students to a list for easier handling
            attendance_results = []
            for student_code, data in recognized_students.items():
                # Only count as present if recognized in multiple frames with good liveness score
                if data['count'] >= 3 and data.get('liveness_score', 0) >= 60:  # Recognized in at least 3 frames and good liveness
                    attendance_results.append({
                        'student_code': student_code,
                        'name': data['name'],
                        'present': True,
                        'status': 'Có mặt',
                        'similarity': data['similarity'],
                        'schedule_id': schedule_id,
                        'timestamp': data['timestamp']
                    })
            
            return True, attendance_results
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error in process_video_feed: {e}\n{error_details}")
            # Make sure to release camera
            try:
                cap.release()
                cv2.destroyAllWindows()
            except:
                pass
            return False, f"Error processing video: {str(e)}"
