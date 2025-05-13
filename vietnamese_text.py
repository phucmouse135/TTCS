"""
Script to test and fix Vietnamese text display in OpenCV
"""
import cv2
import numpy as np
import os
import sys

def test_vietnamese_display():
    """Test and demonstrate Vietnamese text display in OpenCV"""
    # Create a blank image
    img = np.zeros((400, 800, 3), np.uint8)
    img.fill(255)  # White background
    
    # Test Vietnamese text
    vietnamese_text = "Xin chào - Tiếng Việt - Học sinh: Nguyễn Văn A"
    
    # Method 1: Standard cv2.putText (limited Vietnamese support)
    cv2.putText(img, f"Standard: {vietnamese_text}", (20, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1)
    
    # Method 1b: Different font
    cv2.putText(img, f"Complex: {vietnamese_text}", (20, 100), 
                cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 0, 255), 1)
    
    # Method 2: Use PIL for better unicode support
    try:
        from PIL import Image, ImageDraw, ImageFont
        import numpy as np
        
        # Create a PIL Image
        pil_img = Image.fromarray(img)
        draw = ImageDraw.Draw(pil_img)
        
        # Load a font that supports Vietnamese
        try:
            # Try to use a system font that supports Vietnamese
            font_path = "C:\\Windows\\Fonts\\Arial.ttf"
            if not os.path.exists(font_path):
                font_path = "C:\\Windows\\Fonts\\segoeui.ttf"  # Fallback to Segoe UI
            
            font = ImageFont.truetype(font_path, 20)
            draw.text((20, 150), f"PIL (TrueType): {vietnamese_text}", font=font, fill=(0, 0, 0))
        except Exception as e:
            print(f"Error loading TrueType font: {e}")
            # Fallback to default
            draw.text((20, 150), f"PIL (Default): {vietnamese_text}", fill=(0, 0, 0))
        
        # Convert back to OpenCV format
        img = np.array(pil_img)
    except ImportError:
        cv2.putText(img, "PIL not available - can't show better Vietnamese text", 
                   (20, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 1)
    
    # Draw a line to separate examples
    cv2.line(img, (0, 200), (800, 200), (0, 0, 0), 2)
    
    # Practical usage example for face recognition
    cv2.rectangle(img, (50, 220), (150, 320), (0, 255, 0), 2)  # Face rectangle
    
    # Method 1: Direct OpenCV text
    cv2.putText(img, "Học sinh: Nguyễn Văn A", (50, 350), 
                cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.8, (255, 0, 0), 2)
    cv2.putText(img, "Similarity: 0.85", (50, 380), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
    
    # Show the result
    cv2.imshow("Vietnamese Text Test", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    return True

def fix_vietnamese_in_app():
    """Apply fixes for Vietnamese text display in the application"""
    # Check and install PIL if needed
    try:
        import pip
        import importlib
        
        # Check if PIL/Pillow is installed
        try:
            importlib.import_module('PIL')
            print("PIL/Pillow is already installed")
        except ImportError:
            print("Installing Pillow for better Vietnamese text support...")
            pip.main(['install', 'Pillow'])
            print("Pillow installed successfully")
    except Exception as e:
        print(f"Error checking/installing PIL: {e}")
    
    # Create helper function files
    helper_file = "d:\\ProjectTTCS\\app\\vietnamese_helper.py"
    with open(helper_file, 'w', encoding='utf-8') as f:
        f.write("""# Helper functions for Vietnamese text display
import numpy as np

def put_vietnamese_text(img, text, position, font_scale=0.7, color=(0, 0, 0), thickness=1):
    \"\"\"Draw text with Vietnamese characters support\"\"\"
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Convert OpenCV image to PIL Image
        pil_img = Image.fromarray(img.copy())
        draw = ImageDraw.Draw(pil_img)
        
        # Try to use a system font that supports Vietnamese
        font_path = "C:\\\\Windows\\\\Fonts\\\\Arial.ttf"
        import os
        if not os.path.exists(font_path):
            font_path = "C:\\\\Windows\\\\Fonts\\\\segoeui.ttf"  # Fallback to Segoe UI
        
        # Calculate appropriate font size from OpenCV font_scale
        font_size = int(font_scale * 20)
        
        try:
            font = ImageFont.truetype(font_path, font_size)
        except:
            # Fallback to default font
            font = ImageFont.load_default()
        
        # Draw the text
        draw.text(position, text, font=font, fill=color[::-1])  # Convert BGR to RGB
        
        # Convert back to OpenCV format
        result_img = np.array(pil_img)
        return result_img
    except Exception as e:
        # Fallback to standard OpenCV putText
        import cv2
        cv2.putText(img, text, position, cv2.FONT_HERSHEY_COMPLEX_SMALL, 
                    font_scale, color, thickness)
        return img
""")
    
    print(f"Created Vietnamese text helper at {helper_file}")
    print("Use this helper in your code for better Vietnamese text display")
    
    return True

if __name__ == "__main__":
    test_vietnamese_display()
    fix_vietnamese_in_app()
    print("\nVietnamese text display test complete.")
    print("Run your application now to see improved Vietnamese character support.")
