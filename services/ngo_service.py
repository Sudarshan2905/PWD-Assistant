from models.database import db
from models.student import NGOStudent
from flask import current_app
import os
from werkzeug.utils import secure_filename
from datetime import datetime

class NGOStudentService:
    
    @staticmethod
    def get_all_students(ngo_id):
        """Get all students for an NGO"""
        return NGOStudent.query.filter_by(ngo_id=ngo_id).all()
    
    @staticmethod
    def get_student(student_id, ngo_id):
        """Get a specific student"""
        return NGOStudent.query.filter_by(id=student_id, ngo_id=ngo_id).first()
    
    @staticmethod
    def add_student(ngo_id, name, age, certificate_file=None):
        """Add a new student"""
        student = NGOStudent(
            ngo_id=ngo_id,
            name=name,
            age=age,
            certificate_file=certificate_file
        )
        
        try:
            db.session.add(student)
            db.session.commit()
            return student, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def update_student(student_id, ngo_id, name, age, certificate_file=None):
        """Update student information"""
        student = NGOStudent.query.filter_by(id=student_id, ngo_id=ngo_id).first()
        
        if not student:
            return None, 'Student not found'
        
        student.name = name
        student.age = age
        if certificate_file:
            student.certificate_file = certificate_file
        
        try:
            db.session.commit()
            return student, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def delete_student(student_id, ngo_id):
        """Delete a student"""
        student = NGOStudent.query.filter_by(id=student_id, ngo_id=ngo_id).first()
        
        if not student:
            return False, 'Student not found'
        
        try:
            db.session.delete(student)
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, str(e)
    
    @staticmethod
    def save_certificate(file):
        """Save uploaded certificate file"""
        if not file:
            return None
        
        if file.filename == '':
            return None
        
        if file and NGOStudentService.allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_filename = f"{timestamp}_{filename}"
            
            upload_path = os.path.join(
                current_app.config['UPLOAD_FOLDER'],
                'certificates',
                unique_filename
            )
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(upload_path), exist_ok=True)
            
            file.save(upload_path)
            return unique_filename
        
        return None
    
    @staticmethod
    def allowed_file(filename):
        """Check if file extension is allowed"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']