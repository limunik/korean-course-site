from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


# ===========================
# Model 1: Announcement
# ===========================
class Announcement(db.Model):
    __tablename__ = "announcements"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    published_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Announcement id={self.id} title='{self.title}'>"

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "published_at": self.published_at.strftime("%d.%m.%Y %H:%M"),
        }


# ===========================
# Model 2: StudyGroup
# ===========================
class StudyGroup(db.Model):
    __tablename__ = "study_groups"

    id = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.String(100), nullable=False)       # e.g. "Beginner A1", "Intermediate B1"
    schedule = db.Column(db.String(200), nullable=False)    # e.g. "Mon/Wed 18:00–19:30"
    available_spots = db.Column(db.Integer, nullable=False, default=10)

    # Relationship: one group → many registrations
    registrations = db.relationship("Registration", backref="group", lazy=True)

    def __repr__(self):
        return f"<StudyGroup id={self.id} level='{self.level}' spots={self.available_spots}>"

    def to_dict(self):
        return {
            "id": self.id,
            "level": self.level,
            "schedule": self.schedule,
            "available_spots": self.available_spots,
        }


# ===========================
# Model 3: Registration
# ===========================
class Registration(db.Model):
    __tablename__ = "registrations"

    # Status constants
    STATUS_PENDING  = "pending"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"

    ALLOWED_STATUSES = [STATUS_PENDING, STATUS_APPROVED, STATUS_REJECTED]

    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(30), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey("study_groups.id"), nullable=False)
    status = db.Column(
        db.String(20),
        nullable=False,
        default=STATUS_PENDING
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return (
            f"<Registration id={self.id} "
            f"student='{self.student_name}' "
            f"status='{self.status}'>"
        )

    def to_dict(self):
        return {
            "id": self.id,
            "student_name": self.student_name,
            "phone": self.phone,
            "group_id": self.group_id,
            "status": self.status,
            "created_at": self.created_at.strftime("%d.%m.%Y %H:%M"),
        }


# ===========================
# DB Initializer Helper
# ===========================
def init_db(app):
    """
    Bind the SQLAlchemy instance to the Flask app
    and create all tables if they don't exist yet.

    Usage in app.py:
        from models.database import init_db
        init_db(app)
    """
    db.init_app(app)
    with app.app_context():
        db.create_all()