import os
# Disable CUDA at environment level
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
import cv2
import torch
# Force PyTorch to use CPU
torch.cuda.is_available = lambda : False
device = torch.device('cpu')
import numpy as np
from PIL import Image
from facenet_pytorch import MTCNN, InceptionResnetV1
import pickle
from tqdm import tqdm
import time
import pandas as pd
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Ensure we're using CPU instead of CUDA
device = torch.device('cpu')

class FaceRecognition:
    def __init__(self, data_dir='data/faces', database_path='data/face_database.csv'):
        # Use CPU for processing
        self.device = torch.device('cpu')
        # Initialize the MTCNN for face detection
        self.mtcnn = MTCNN(keep_all=True, min_face_size=20, thresholds=[0.5, 0.6, 0.6], device=self.device)
        # Initialize the InceptionResnetV1 model for face recognition
        self.resnet = InceptionResnetV1(pretrained='vggface2').eval().to(self.device)
        
        # Set recognition threshold
        self.recognition_threshold = 0.6  # Adjust as needed for accuracy
        
        # Setup data directories
        self.data_dir = data_dir
        self.database_path = database_path
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize embeddings dictionary
        self.embeddings = {}
        
        # Load or create face database
        self.load_database()
    
    def load_database(self):
        """Load the database from file and ensure data is properly formatted"""
        try:
            if os.path.exists(self.database_path):
                # Use encoding='utf-8' to correctly read Vietnamese characters
                self.df = pd.read_csv(self.database_path, encoding='utf-8')
                
                # Make sure we have the required columns
                required_columns = ['student_code', 'name', 'face_path', 'embedding', 'timestamp']
                for col in required_columns:
                    if col not in self.df.columns:
                        self.df[col] = ''
                
                # Convert columns to correct types to avoid display issues
                self.df['student_code'] = self.df['student_code'].astype(str)
                self.df['name'] = self.df['name'].astype(str)
                self.df['face_path'] = self.df['face_path'].astype(str)
                
                print(f"Loaded {len(self.df)} students from database")
                
                # Initialize embeddings dictionary
                self.embeddings = {}
                
                # Load embeddings for each student
                for _, row in self.df.iterrows():
                    student_code = str(row['student_code']).strip()
                    name = str(row['name']).strip()
                    embedding_str = row['embedding']
                    try:
                        if isinstance(embedding_str, str) and len(embedding_str) > 2:
                            # Clean the embedding string and convert to numpy array
                            embedding_str = embedding_str.replace('[', '').replace(']', '')
                            embedding_array = np.fromstring(embedding_str, sep=',')
                            
                            # Ensure the embedding has the correct size (512 dimensions)
                            if len(embedding_array) > 0:
                                # Store in dictionary with proper structure
                                self.embeddings[student_code] = {
                                    'embedding': embedding_array,
                                    'name': name
                                }
                                print(f"Loaded embedding for student {student_code}: {name} - shape: {embedding_array.shape}")
                            else:
                                print(f"Warning: Empty embedding for student {student_code}")
                    except Exception as e:
                        print(f"Error loading embedding for student {student_code}: {e}")
                
                # Print how many embeddings were loaded
                print(f"Loaded {len(self.embeddings)} embeddings from database")
                
                # Print some Vietnamese names to verify encoding
                if not self.df.empty:
                    print("Sample student names from database:")
                    for _, row in self.df.head().iterrows():
                        print(f"  {row['student_code']}: {row['name']}")
                
                return True
            else:
                self.df = pd.DataFrame(columns=['student_code', 'name', 'face_path', 'embedding', 'timestamp'])
                os.makedirs(os.path.dirname(self.database_path), exist_ok=True)
                self.df.to_csv(self.database_path, index=False)
                print("Created new empty database")
            
            # Initialize embeddings dictionary
            self.embeddings = {}
            if len(self.df) > 0:
                for _, row in self.df.iterrows():
                    student_code = str(row['student_code'])
                    name = str(row['name'])
                    embedding_str = row['embedding']
                    try:
                        if isinstance(embedding_str, str) and len(embedding_str) > 2:
                            embedding_array = np.fromstring(embedding_str[1:-1], sep=' ')
                            if len(embedding_array) > 0:
                                self.embeddings[student_code] = {
                                    'embedding': embedding_array,
                                    'name': name
                                }
                    except Exception as e:
                        print(f"Error loading embedding for student {student_code}: {e}")
            
            return True
        except Exception as e:
            import traceback
            print(f"Error loading database: {e}\n{traceback.format_exc()}")
            return False

    def load_embeddings(self):
        """Load embeddings from file if exists"""
        if os.path.exists(self.embeddings_file):
            with open(self.embeddings_file, 'rb') as f:
                self.embeddings = pickle.load(f)
            print(f"Loaded {len(self.embeddings)} embeddings")
        else:
            print("No embeddings file found.")
    
    def save_embeddings(self):
        """Save embeddings to file"""
        os.makedirs(os.path.dirname(self.embeddings_file), exist_ok=True)
        with open(self.embeddings_file, 'wb') as f:
            pickle.dump(self.embeddings, f)
        print(f"Saved {len(self.embeddings)} embeddings")
    
    def extract_face(self, img):
        """Extract faces from an image and return face images"""
        try:
            # Convert to RGB if needed
            if len(img.shape) == 2:  # Grayscale
                img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
            elif img.shape[2] == 4:  # RGBA
                img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)
                
            # Use OpenCV's face detector as an alternative to MTCNN
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            
            # Convert to grayscale for face detection
            gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
            
            # Detect faces
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            result = []
            for (x, y, w, h) in faces:
                # Extract face region
                face_img = img[y:y+h, x:x+w]
                
                # Add some margin
                margin_x = int(w * 0.1)
                margin_y = int(h * 0.1)
                
                # Calculate coordinates with margin (ensuring they're within image bounds)
                x1 = max(0, x - margin_x)
                y1 = max(0, y - margin_y)
                x2 = min(img.shape[1], x + w + margin_x)
                y2 = min(img.shape[0], y + h + margin_y)
                
                # Extract face with margin
                face_with_margin = img[y1:y2, x1:x2]
                
                # Only add if dimensions are valid
                if face_with_margin.size > 0 and face_with_margin.shape[0] > 0 and face_with_margin.shape[1] > 0:
                    result.append((face_with_margin, [x1, y1, x2, y2]))
            
            return result
        except Exception as e:
            print(f"Error extracting faces: {e}")
            return []

    def get_embedding(self, face_img):
        """Get the embedding for a face image"""
        try:
            # Convert image to RGB (if grayscale)
            if len(face_img.shape) == 2:
                face_img = cv2.cvtColor(face_img, cv2.COLOR_GRAY2RGB)
            elif face_img.shape[2] == 4:  # RGBA
                face_img = cv2.cvtColor(face_img, cv2.COLOR_RGBA2RGB)
            
            # Resize image to expected dimensions
            face_img = cv2.resize(face_img, (160, 160))
            
            # Transpose dimensions for PyTorch (H,W,C) -> (C,H,W)
            face_tensor = torch.from_numpy(face_img).permute(2, 0, 1).float()
            
            # Scale pixel values to [0, 1]
            face_tensor = face_tensor / 255.0
            
            # Add batch dimension and send to device
            face_tensor = face_tensor.unsqueeze(0).to(self.device)
            
            # Get embedding from model
            with torch.no_grad():
                embedding = self.resnet(face_tensor)
                
            return embedding.detach().cpu()
        except Exception as e:
            print(f"Error in get_embedding: {e}")
            return None

    def add_student(self, student_code, name, img_path):
        """Add a student to the database with face embedding"""
        try:
            # Check if student already exists
            if student_code in self.df['student_code'].values:
                # Update existing student
                old_path = self.df[self.df['student_code'] == student_code].iloc[0]['face_path']
                if old_path != img_path and os.path.isdir(old_path):
                    import shutil
                    try:
                        shutil.rmtree(old_path)
                    except Exception as e:
                        print(f"Warning: Could not delete old images: {e}")
                
                # Remove old record
                self.df = self.df[self.df['student_code'] != student_code]
            
            # Process all collected face images
            embeddings = []
            face_files = []
            
            if os.path.isdir(img_path):
                for filename in os.listdir(img_path):
                    if filename.endswith('.jpg') or filename.endswith('.png'):
                        file_path = os.path.join(img_path, filename)
                        face_img = cv2.imread(file_path)
                        if face_img is not None:
                            face_files.append(file_path)
                            try:
                                # Get embedding for this face
                                embedding = self.get_embedding(face_img)
                                if embedding is not None:
                                    embeddings.append(embedding.numpy().flatten())
                            except Exception as e:
                                print(f"Error getting embedding for {file_path}: {e}")
            
            # Check if we got any valid embeddings
            if not embeddings:
                return False, "Could not generate face embeddings from the provided images."
            
            # Average the embeddings for more robust recognition
            avg_embedding = np.mean(embeddings, axis=0)
            
            # Store in embeddings dictionary (if it exists)
            if hasattr(self, 'embeddings'):
                self.embeddings[student_code] = avg_embedding
            
            # Add to DataFrame
            new_row = {
                'student_code': student_code,
                'name': name,
                'face_path': img_path,
                'embedding': str(avg_embedding.tolist()),  # Store as string
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Add new row to DataFrame
            self.df = pd.concat([self.df, pd.DataFrame([new_row])], ignore_index=True)
            
            # Save to CSV with error handling
            try:
                self.df.to_csv(self.database_path, index=False)
            except Exception as e:
                print(f"Error saving database: {e}")
                # Try to save to a backup location
                backup_path = self.database_path + ".backup"
                self.df.to_csv(backup_path, index=False)
                print(f"Saved database to backup location: {backup_path}")
            
            return True, f"Student {name} ({student_code}) added with {len(embeddings)} face samples."
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error in add_student: {e}\n{error_details}")
            return False, f"Error adding student: {str(e)}"
    
    def delete_student(self, student_code):
        """Delete a student from the database"""
        try:
            # Make sure student_code is a string
            student_code = str(student_code).strip()
            
            # Debug: print current student codes
            print(f"Searching for student code: '{student_code}'")
            print(f"Available student codes: {self.df['student_code'].values}")
            
            # Check if student exists - convert all to string for comparison
            student_exists = False
            student_index = -1
            
            for i, code in enumerate(self.df['student_code']):
                if str(code).strip() == student_code:
                    student_exists = True
                    student_index = i
                    break
            
            if not student_exists:
                return False, f"Student with code {student_code} not found"
            
            # Get the face path to delete face images
            student_row = self.df.iloc[student_index]
            face_path = student_row['face_path']
            name = str(student_row['name'])
            
            # Remove from DataFrame
            self.df = self.df[self.df.index != student_index]
            
            # Save updated DataFrame
            self.df.to_csv(self.database_path, index=False)
            print(f"Student {student_code} removed from database")
            
            # Remove from embeddings dictionary
            if hasattr(self, 'embeddings') and student_code in self.embeddings:
                del self.embeddings[student_code]
                print(f"Student {student_code} removed from embeddings")
            
            # Delete face images if directory exists
            if os.path.isdir(face_path):
                import shutil
                try:
                    shutil.rmtree(face_path)
                    print(f"Deleted face images at {face_path}")
                except Exception as e:
                    print(f"Warning: Could not delete face images: {e}")
            
            return True, f"Student {name} ({student_code}) has been deleted"
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error in delete_student: {e}\n{error_details}")
            return False, f"Error deleting student: {str(e)}"
    
    def recognize_face(self, face_img):
        """
        Recognize a face by comparing its embedding with stored embeddings
        Returns (student_code, name, similarity) if recognized, None otherwise
        """
        # Get face embedding
        embedding = self.get_embedding(face_img)
        if embedding is None:
            return None
        
        # Check if we have any embeddings to compare against
        if not self.embeddings:
            print("No embeddings available for comparison")
            return None
        
        # Convert embedding to numpy array
        embedding_array = embedding.numpy().flatten()
        print(f"Generated embedding for recognition, shape: {embedding_array.shape}")
        
        # Find the most similar face
        best_match = None
        highest_similarity = 0
        
        # Debug count
        compared = 0
        
        # Use the embeddings dictionary
        for student_code, data in self.embeddings.items():
            try:
                # Ensure we're getting the embedding from the correct structure
                if isinstance(data, dict) and 'embedding' in data:
                    stored_embedding = data['embedding']
                    name = data['name']
                    
                    # Make sure both embeddings have the same shape
                    if len(stored_embedding) == len(embedding_array):
                        similarity = self.cosine_similarity(embedding_array, stored_embedding)
                        compared += 1
                        
                        print(f"Comparing with {student_code}: similarity = {similarity:.4f}")
                        
                        if similarity > highest_similarity:
                            highest_similarity = similarity
                            best_match = (student_code, name)
                    else:
                        print(f"Shape mismatch for {student_code}: {len(stored_embedding)} vs {len(embedding_array)}")
                else:
                    print(f"Invalid embedding structure for {student_code}")
            except Exception as e:
                print(f"Error comparing with student {student_code}: {e}")
        
        print(f"Compared with {compared} embeddings")
        
        # Lower the threshold for better recognition (adjust as needed)
        threshold = 0.5  # Default was 0.6
        
        # Only return a match if similarity is above threshold
        if best_match and highest_similarity > threshold:
            student_code, name = best_match
            print(f"Match found: {student_code} - {name} with similarity {highest_similarity:.4f}")
            return student_code, name, highest_similarity
        
        print(f"No match found. Highest similarity: {highest_similarity:.4f}")
        return None
    
    def cosine_similarity(self, a, b):
        """Calculate cosine similarity between two vectors"""
        try:
            # Ensure both are 1D arrays of the same length
            a = np.asarray(a).flatten()
            b = np.asarray(b).flatten()
            
            if a.shape[0] != b.shape[0]:
                print(f"Shape mismatch: {a.shape} vs {b.shape}")
                return 0.0
                
            return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
        except Exception as e:
            print(f"Error in cosine similarity calculation: {e}")
            return 0.0

    def collect_faces_from_camera(self, student_code, name, num_samples=20):
        """Collect face samples from camera for registration"""
        try:
            # Open camera
            cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Use DirectShow API for better camera handling
            if not cap.isOpened():
                return False, "Cannot open camera. Please check your camera connection."
            
            # Set camera properties for better performance
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            faces_collected = 0
            max_attempts = 100  # Maximum number of frames to try
            attempts = 0
            
            # Create a folder for this student if it doesn't exist
            student_dir = os.path.join(self.data_dir, student_code)
            os.makedirs(student_dir, exist_ok=True)
            
            # For showing progress to user
            cv2.namedWindow("Face Collection", cv2.WINDOW_NORMAL)
            cv2.resizeWindow("Face Collection", 640, 480)
            
            while faces_collected < num_samples and attempts < max_attempts:
                ret, frame = cap.read()
                if not ret:
                    print("Failed to read frame from camera")
                    # Try to reinitialize camera
                    cap.release()
                    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
                    if not cap.isOpened():
                        return False, "Camera disconnected during capture"
                    continue
                
                # Make a copy for display
                display_frame = frame.copy()
                
                # Extract faces using MTCNN
                try:
                    boxes, probs, landmarks = self.mtcnn.detect(frame, landmarks=True)
                    
                    if boxes is not None and len(boxes) == 1:  # Only use frames with exactly one face
                        box = boxes[0].astype(int)
                        x1, y1, x2, y2 = box
                        
                        # Ensure coordinates are within image boundaries
                        x1, y1 = max(0, x1), max(0, y1)
                        x2, y2 = min(frame.shape[1], x2), min(frame.shape[0], y2)
                        
                        # Extract face region
                        face_img = frame[y1:y2, x1:x2]
                        
                        # Check face quality (size, clarity)
                        if face_img.shape[0] > 100 and face_img.shape[1] > 100:
                            # Draw rectangle around face
                            cv2.rectangle(display_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                            
                            # Only save every 3rd good frame to get more variations
                            if attempts % 3 == 0:
                                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                img_path = os.path.join(student_dir, f"{timestamp}_{faces_collected}.jpg")
                                cv2.imwrite(img_path, face_img)
                                faces_collected += 1
                            
                            # Show progress
                            cv2.putText(display_frame, f"Collected: {faces_collected}/{num_samples}", 
                                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                        else:
                            cv2.putText(display_frame, "Face too small or unclear", 
                                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    else:
                        if boxes is not None and len(boxes) > 1:
                            cv2.putText(display_frame, "Multiple faces detected", 
                                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                        else:
                            cv2.putText(display_frame, "No face detected", 
                                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                except Exception as e:
                    print(f"Error in face detection: {e}")
                    cv2.putText(display_frame, "Detection error", 
                            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
                # Display instructions
                cv2.putText(display_frame, "Move your face slightly for different angles", 
                        (10, display_frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                # Show the frame in a persistent window
                cv2.imshow("Face Collection", display_frame)
                
                # Process key input
                key = cv2.waitKey(100)  # Wait for 100ms
                if key == 27:  # ESC key to exit
                    break
                
                attempts += 1
            
            # Clean up
            cap.release()
            cv2.destroyAllWindows()
            
            if faces_collected == 0:
                return False, "No faces collected. Please try again with better lighting."
            
            # Process the collected faces
            img_path = student_dir  # Store the directory instead of individual images
            success, message = self.add_student(student_code, name, img_path)
            
            # Force save the database to ensure changes are persisted
            self.df.to_csv(self.database_path, index=False)
            print(f"Database saved with {len(self.df)} students")
            
            return success, f"Successfully registered {name} ({student_code}) with {faces_collected} face samples."
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error in collect_faces_from_camera: {e}\n{error_details}")
            # Make sure windows are closed
            try:
                cv2.destroyAllWindows()
            except:
                pass
            return False, f"Error collecting faces: {str(e)}"

    def process_video_feed(self, schedule_id, update_callback=None):
        """Process video feed for attendance"""
        try:
            # Open camera
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                return False, "Cannot open camera"
            
            # Initialize variables
            recognized_students = {}
            running = True
            frame_count = 0
            
            # Face detection and recognition loop
            while running and frame_count < 150:  # Process max 150 frames
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Make a copy for display
                display_frame = frame.copy()
                
                # Extract faces using OpenCV instead of MTCNN
                faces = self.extract_face(frame)
                
                # Process detected faces
                for face_img, face_box in faces:
                    # Try to recognize the face
                    match_result = self.recognize_face(face_img)
                    
                    # Draw rectangle around face
                    x1, y1, x2, y2 = face_box
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
                                'timestamp': current_time
                            }
                        else:
                            recognized_students[student_code]['count'] += 1
                            if similarity > recognized_students[student_code]['similarity']:
                                recognized_students[student_code]['similarity'] = similarity
                        
                        # Display recognition results
                        cv2.putText(display_frame, f"Student: {name}", (x1, y1 - 30), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                        cv2.putText(display_frame, f"Similarity: {similarity:.2f}", (x1, y1 - 10), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    else:
                        # Display "Unknown" for unrecognized faces
                        cv2.putText(display_frame, "Unknown", (x1, y1 - 10), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
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
                # Only count as present if recognized in multiple frames
                if data['count'] >= 3:  # Recognized in at least 3 frames
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

    def train_model(self):
        """Train or retrain the face recognition model to improve accuracy"""
        try:
            print("Starting model training...")
            
            # Count of students processed and faces loaded
            students_processed = 0
            faces_loaded = 0
            
            # Reset embeddings dictionary
            self.embeddings = {}
            
            # Process all students in the database
            for _, student in self.df.iterrows():
                student_code = str(student['student_code']).strip()
                name = str(student['name']).strip()
                face_path = student['face_path']
                
                print(f"Processing student: {student_code} - {name}")
                print(f"Face path: {face_path}")
                
                if os.path.isdir(face_path):
                    # Load all face images for this student
                    face_embeddings = []
                    
                    face_files = [f for f in os.listdir(face_path) if f.endswith(('.jpg', '.png', '.jpeg'))]
                    print(f"Found {len(face_files)} face images for student {student_code}")
                    
                    for filename in face_files:
                        img_path = os.path.join(face_path, filename)
                        face_img = cv2.imread(img_path)
                        
                        if face_img is not None:
                            # Get embedding for this face
                            embedding = self.get_embedding(face_img)
                            if embedding is not None:
                                face_embeddings.append(embedding.numpy().flatten())
                                faces_loaded += 1
                                print(f"Generated embedding for {filename}, shape: {embedding.numpy().flatten().shape}")
                            else:
                                print(f"Failed to generate embedding for {filename}")
                    
                    # If we got embeddings, calculate average and store it
                    if face_embeddings:
                        avg_embedding = np.mean(face_embeddings, axis=0)
                        
                        # Store in embeddings dictionary
                        self.embeddings[student_code] = {
                            'embedding': avg_embedding,
                            'name': name
                        }
                        
                        # Update the embedding in the DataFrame - store as comma-separated string
                        embedding_str = ','.join([str(val) for val in avg_embedding])
                        self.df.loc[self.df['student_code'] == student_code, 'embedding'] = f"[{embedding_str}]"
                        
                        students_processed += 1
                        print(f"Created average embedding for student {student_code}, shape: {avg_embedding.shape}")
                    else:
                        print(f"No valid embeddings generated for student {student_code}")
                else:
                    print(f"Warning: Face path does not exist: {face_path}")
            
            # Save updated DataFrame with new embeddings
            self.df.to_csv(self.database_path, index=False, encoding='utf-8')
            
            print(f"Model training completed: {students_processed} students processed with {faces_loaded} face images")
            return True, f"Model training completed with {students_processed} students and {faces_loaded} face images"
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error in train_model: {e}\n{error_details}")
            return False, f"Error training model: {str(e)}"

    def save_to_csv(self):
        """Save database to CSV with proper encoding for Vietnamese characters"""
        try:
            self.df.to_csv(self.database_path, index=False, encoding='utf-8')
            print(f"Database saved with proper encoding for Vietnamese characters")
            return True
        except Exception as e:
            print(f"Error saving database: {e}")
            return False

    def get_all_students(self):
        """Get all students from the database"""
        try:
            # Make sure the DataFrame is up-to-date
            if os.path.exists(self.database_path):
                self.df = pd.read_csv(self.database_path, encoding='utf-8')
            
            # Return a copy of the DataFrame
            return self.df.copy()
        except Exception as e:
            print(f"Error getting students: {e}")
            return pd.DataFrame(columns=['student_code', 'name', 'face_path', 'embedding', 'timestamp'])
