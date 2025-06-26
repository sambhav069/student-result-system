# database.py - Database operations using SQLite
import sqlite3
import pandas as pd
from typing import List, Dict, Optional, Tuple
import os

class StudentDatabase:
    def __init__(self, db_name: str = "student_results.db"):
        self.db_name = db_name
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_name)
    
    def init_database(self):
        """Initialize database with required tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Students table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                class TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Subjects table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subjects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                max_marks INTEGER NOT NULL DEFAULT 100,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Results table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                subject_name TEXT NOT NULL,
                marks INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE,
                FOREIGN KEY (subject_name) REFERENCES subjects (name) ON DELETE CASCADE,
                UNIQUE(student_id, subject_name)
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Initialize with sample data if tables are empty
        self.init_sample_data()
    
    def init_sample_data(self):
        """Initialize with sample data if database is empty"""
        if self.get_student_count() == 0:
            # Add sample subjects
            sample_subjects = [
                ("Mathematics", 100),
                ("English", 100),
                ("Science", 100),
                ("History", 100)
            ]
            
            for subject_name, max_marks in sample_subjects:
                self.add_subject(subject_name, max_marks)
            
            # Add sample students
            sample_students = [
                ("S001", "John Doe", "10th Grade"),
                ("S002", "Jane Smith", "10th Grade"),
                ("S003", "Mike Johnson", "10th Grade")
            ]
            
            for student_id, name, class_name in sample_students:
                self.add_student(student_id, name, class_name)
    
    # Student operations
    def add_student(self, student_id: str, name: str, class_name: str) -> bool:
        """Add a new student"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO students (id, name, class) VALUES (?, ?, ?)",
                (student_id, name, class_name)
            )
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def get_all_students(self) -> List[Dict]:
        """Get all students"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, class FROM students ORDER BY name")
        students = [{"id": row[0], "name": row[1], "class": row[2]} for row in cursor.fetchall()]
        conn.close()
        return students
    
    def get_student_count(self) -> int:
        """Get total number of students"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM students")
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def delete_student(self, student_id: str) -> bool:
        """Delete a student and their results"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
            conn.commit()
            conn.close()
            return True
        except:
            return False
    
    def clear_all_students(self):
        """Clear all students and their results"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM students")
        cursor.execute("DELETE FROM results")
        conn.commit()
        conn.close()
    
    # Subject operations
    def add_subject(self, name: str, max_marks: int) -> bool:
        """Add a new subject"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO subjects (name, max_marks) VALUES (?, ?)",
                (name, max_marks)
            )
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def get_all_subjects(self) -> List[Dict]:
        """Get all subjects"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name, max_marks FROM subjects ORDER BY name")
        subjects = [{"name": row[0], "max_marks": row[1]} for row in cursor.fetchall()]
        conn.close()
        return subjects
    
    def get_subject_count(self) -> int:
        """Get total number of subjects"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM subjects")
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def delete_subject(self, name: str) -> bool:
        """Delete a subject and related results"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM subjects WHERE name = ?", (name,))
            conn.commit()
            conn.close()
            return True
        except:
            return False
    
    def clear_all_subjects(self):
        """Clear all subjects and results"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM subjects")
        cursor.execute("DELETE FROM results")
        conn.commit()
        conn.close()
    
    # Results operations
    def save_marks(self, student_id: str, subject_name: str, marks: int) -> bool:
        """Save or update marks for a student in a subject"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO results (student_id, subject_name, marks)
                VALUES (?, ?, ?)
            ''', (student_id, subject_name, marks))
            conn.commit()
            conn.close()
            return True
        except:
            return False
    
    def get_student_results(self, student_id: str) -> Dict[str, int]:
        """Get all results for a specific student"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT subject_name, marks FROM results WHERE student_id = ?",
            (student_id,)
        )
        results = {row[0]: row[1] for row in cursor.fetchall()}
        conn.close()
        return results
    
    def get_all_results(self) -> pd.DataFrame:
        """Get all results as a DataFrame"""
        conn = self.get_connection()
        query = '''
            SELECT s.id, s.name, s.class, r.subject_name, r.marks, sub.max_marks
            FROM students s
            LEFT JOIN results r ON s.id = r.student_id
            LEFT JOIN subjects sub ON r.subject_name = sub.name
            ORDER BY s.name, r.subject_name
        '''
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    
    # Statistics and analytics
    def get_dashboard_stats(self) -> Dict:
        """Get dashboard statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Total students and subjects
        cursor.execute("SELECT COUNT(*) FROM students")
        total_students = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM subjects")
        total_subjects = cursor.fetchone()[0]
        
        # Average marks and pass rate
        cursor.execute('''
            SELECT AVG(CAST(marks AS FLOAT)) as avg_marks,
                   COUNT(CASE WHEN marks >= 60 THEN 1 END) * 100.0 / COUNT(*) as pass_rate
            FROM results
        ''')
        result = cursor.fetchone()
        avg_marks = round(result[0], 1) if result[0] else 0
        pass_rate = round(result[1], 1) if result[1] else 0
        
        conn.close()
        
        return {
            "total_students": total_students,
            "total_subjects": total_subjects,
            "avg_marks": avg_marks,
            "pass_rate": pass_rate
        }
    
    def get_grade(self, percentage: float) -> str:
        """Calculate grade based on percentage"""
        if percentage >= 90:
            return 'A'
        elif percentage >= 80:
            return 'B'
        elif percentage >= 70:
            return 'C'
        elif percentage >= 60:
            return 'D'
        else:
            return 'F'
    
    def generate_student_report(self, student_id: str) -> Dict:
        """Generate detailed report for a student"""
        student_info = None
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get student info
        cursor.execute("SELECT id, name, class FROM students WHERE id = ?", (student_id,))
        student_row = cursor.fetchone()
        if not student_row:
            return None
        
        student_info = {
            "id": student_row[0],
            "name": student_row[1],
            "class": student_row[2]
        }
        
        # Get results with subject details
        cursor.execute('''
            SELECT r.subject_name, r.marks, s.max_marks
            FROM results r
            JOIN subjects s ON r.subject_name = s.name
            WHERE r.student_id = ?
            ORDER BY r.subject_name
        ''', (student_id,))
        
        results = []
        total_marks = 0
        total_max_marks = 0
        
        for row in cursor.fetchall():
            subject_name, marks, max_marks = row
            percentage = (marks / max_marks) * 100
            grade = self.get_grade(percentage)
            
            results.append({
                "subject": subject_name,
                "marks": marks,
                "max_marks": max_marks,
                "percentage": round(percentage, 1),
                "grade": grade
            })
            
            total_marks += marks
            total_max_marks += max_marks
        
        conn.close()
        
        # Calculate overall performance
        overall_percentage = (total_marks / total_max_marks * 100) if total_max_marks > 0 else 0
        overall_grade = self.get_grade(overall_percentage)
        
        return {
            "student": student_info,
            "results": results,
            "summary": {
                "total_marks": total_marks,
                "total_max_marks": total_max_marks,
                "overall_percentage": round(overall_percentage, 1),
                "overall_grade": overall_grade
            }
        }

# Example usage and testing
if __name__ == "__main__":
    db = StudentDatabase()
    
    # Test adding a student
    success = db.add_student("S004", "Alice Brown", "10th Grade")
    print(f"Add student: {success}")
    
    # Test getting all students
    students = db.get_all_students()
    print(f"Students: {students}")
    
    # Test adding marks
    db.save_marks("S001", "Mathematics", 85)
    db.save_marks("S001", "English", 78)
    
    # Test getting student results
    results = db.get_student_results("S001")
    print(f"S001 Results: {results}")
    
    # Test dashboard stats
    stats = db.get_dashboard_stats()
    print(f"Dashboard stats: {stats}")
    
    # Test report generation
    report = db.generate_student_report("S001")
    print(f"Report: {report}")
