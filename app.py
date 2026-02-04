"""
Study Planner Application - With Timer Functionality and Tab Navigation
"""
import tkinter as tk
from tkinter import messagebox, ttk, Canvas

class StudyPlannerApp:
    def __init__(self):
        """Initialize the Study Planner App"""
        self.root = tk.Tk()
        self.root.title("FocusFlow")
        self.root.geometry("800x600")

    def run(self):
        """run app"""
        self.root.mainloop()

if __name__ == "__main__":
    app = StudyPlannerApp()
    app.run()