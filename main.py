import os
import sys
from PyQt5.QtWidgets import QApplication

# Add the project root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the fixed methods for class tab from gui_fix.py
from app.gui import setup_classes_tab, clear_class_form, on_class_select, add_class, update_class
from app.gui import delete_class, refresh_classes_list

def main():
    # Import the MainWindow class
    from app.gui import MainWindow
    
    # Apply our fixes by monkey patching the methods
    MainWindow.setup_classes_tab = setup_classes_tab
    MainWindow.clear_class_form = clear_class_form
    MainWindow.on_class_select = on_class_select
    MainWindow.add_class = add_class
    MainWindow.update_class = update_class
    MainWindow.delete_class = delete_class
    MainWindow.refresh_classes_list = refresh_classes_list
    
    # Start the application
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
