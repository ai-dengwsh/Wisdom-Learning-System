from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, UTC
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    # 用户能力指标
    skill_level = db.Column(db.Float, default=0.5)  # 0.0-1.0
    learning_speed = db.Column(db.Float, default=0.5)  # 0.0-1.0
    problem_solving_ability = db.Column(db.Float, default=0.5)  # 0.0-1.0
    
    # 学习偏好
    preferred_difficulty = db.Column(db.String(20), default='medium')  # easy, medium, hard
    daily_goal = db.Column(db.Integer, default=5)  # 每日目标题数
    
    # 关联
    submissions = db.relationship('Submission', backref='user', lazy=True)
    learning_paths = db.relationship('LearningPath', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

class Problem(db.Model):
    __tablename__ = 'problems'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)  # easy, medium, hard
    source = db.Column(db.String(50))  # leetcode, nowcoder等
    tags = db.Column(db.JSON)  # ['array', 'dynamic-programming']等
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    
    # 统计信息
    submission_count = db.Column(db.Integer, default=0)
    success_rate = db.Column(db.Float, default=0.0)
    average_time = db.Column(db.Float, default=0.0)  # 平均解题时间
    
    # 关联
    submissions = db.relationship('Submission', backref='problem', lazy=True)

class Submission(db.Model):
    __tablename__ = 'submissions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    problem_id = db.Column(db.Integer, db.ForeignKey('problems.id'), nullable=False)
    code = db.Column(db.Text)
    language = db.Column(db.String(20), default='python')
    is_correct = db.Column(db.Boolean, nullable=False)
    time_spent = db.Column(db.Integer)  # 以秒为单位
    submitted_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    
    user = db.relationship('User', backref=db.backref('submissions', lazy=True))
    problem = db.relationship('Problem', backref=db.backref('submissions', lazy=True))

class LearningPath(db.Model):
    __tablename__ = 'learning_paths'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    topic_sequence = db.Column(db.JSON)  # ['arrays', 'linked-lists', 'trees']等
    current_stage = db.Column(db.Integer, default=0)
    completion_rate = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))
    daily_problems = db.Column(db.Integer, default=5)
    
    # 关联
    submissions = db.relationship('Submission', backref='learning_path', lazy=True)

class UserActivity(db.Model):
    __tablename__ = 'user_activities'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)  # 活动类型（做题、复习等）
    activity_data = db.Column(db.JSON)  # 活动详细数据
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 活动效果评估
    effectiveness_score = db.Column(db.Float)  # 活动效果评分
    time_spent = db.Column(db.Integer)  # 花费时间（分钟）
    fatigue_level = db.Column(db.Float)  # 疲劳度
