from models import db, User, Problem, Submission, LearningPath, UserActivity
from datetime import datetime, timedelta, UTC
import json
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy import func

class UserService:
    @staticmethod
    def create_user(username, email, password):
        """创建新用户"""
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user
    
    @staticmethod
    def authenticate_user(username, password):
        """用户认证"""
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            user.last_login = datetime.utcnow()
            db.session.commit()
            return user
        return None
    
    @staticmethod
    def update_user_profile(user_id, data):
        """更新用户资料"""
        user = User.query.get(user_id)
        if user:
            for key, value in data.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            db.session.commit()
            return user
        return None
    
    @staticmethod
    def update_last_login(user):
        user.last_login = datetime.now(UTC)
        db.session.commit()
    
    @staticmethod
    def get_user_statistics(user):
        # 获取最近24小时的提交记录
        recent_time = datetime.now(UTC) - timedelta(hours=24)
        recent_submissions = Submission.query.filter(
            Submission.user_id == user.id,
            Submission.submitted_at >= recent_time
        ).all()
        
        # 计算统计数据
        total_time = sum(s.time_spent for s in recent_submissions) if recent_submissions else 0
        correct_submissions = [s for s in recent_submissions if s.is_correct]
        activity_count = len(recent_submissions)
        average_effectiveness = len(correct_submissions) / activity_count if activity_count > 0 else 0
        
        # 计算疲劳度 (基于连续答题时间和正确率)
        fatigue_level = min(1.0, (total_time / 3600) * (1 - average_effectiveness))
        
        return {
            'total_time': total_time,
            'activity_count': activity_count,
            'average_effectiveness': average_effectiveness,
            'fatigue_level': fatigue_level
        }

class ProblemService:
    @staticmethod
    def import_problems_from_json(json_file):
        """从JSON文件导入题目"""
        with open(json_file, 'r', encoding='utf-8') as f:
            problems = json.load(f)
            
        for p in problems:
            problem = Problem(
                title=p['title'],
                content=p['content'],
                difficulty=p['difficulty'],
                source=p['source'],
                url=p.get('url'),
                tags=p.get('tags', [])
            )
            db.session.add(problem)
        
        db.session.commit()
    
    @staticmethod
    def get_problem_by_id(problem_id):
        """获取题目详情"""
        return Problem.query.get(problem_id)
    
    @staticmethod
    def get_problems_by_difficulty(difficulty):
        """获取指定难度的题目"""
        return Problem.query.filter_by(difficulty=difficulty).all()

class RecommendationService:
    def __init__(self):
        self.scaler = StandardScaler()
    
    def get_user_features(self, user):
        """获取用户特征向量"""
        submissions = Submission.query.filter_by(user_id=user.id).all()
        if not submissions:
            return np.zeros(4)
        
        # 计算用户特征
        accuracy = sum(1 for s in submissions if s.is_correct) / len(submissions)
        avg_time = sum(s.time_spent for s in submissions) / len(submissions)
        consistency = self._calculate_consistency(submissions)
        difficulty_handling = self._calculate_difficulty_handling(submissions)
        
        return np.array([accuracy, avg_time, consistency, difficulty_handling])
    
    def _calculate_consistency(self, submissions):
        """计算学习一致性"""
        if len(submissions) < 2:
            return 0
        
        times = [s.time_spent for s in submissions]
        return 1 - np.std(times) / np.mean(times)
    
    def _calculate_difficulty_handling(self, submissions):
        """计算难度适应性"""
        if not submissions:
            return 0
            
        difficulty_scores = {
            'easy': 1,
            'medium': 2,
            'hard': 3
        }
        
        correct_by_difficulty = {
            'easy': [],
            'medium': [],
            'hard': []
        }
        
        for s in submissions:
            difficulty = s.problem.difficulty
            correct_by_difficulty[difficulty].append(1 if s.is_correct else 0)
        
        scores = []
        for difficulty, results in correct_by_difficulty.items():
            if results:
                avg_score = sum(results) / len(results)
                scores.append(avg_score * difficulty_scores[difficulty])
        
        return sum(scores) / len(scores) if scores else 0
    
    def recommend_problems(self, user, count=5):
        """推荐题目"""
        # 获取用户最近完成的题目
        completed_problems = Submission.query.filter_by(
            user_id=user.id,
            is_correct=True
        ).with_entities(Submission.problem_id).all()
        completed_ids = [p[0] for p in completed_problems]
        
        # 根据用户能力水平选择适当难度的题目
        if user.skill_level < 0.3:
            difficulty = 'easy'
        elif user.skill_level < 0.7:
            difficulty = 'medium'
        else:
            difficulty = 'hard'
            
        # 推荐未完成的题目
        recommended = Problem.query.filter(
            Problem.difficulty == difficulty,
            ~Problem.id.in_(completed_ids)
        ).limit(count).all()
        
        return recommended

class LearningPathService:
    @staticmethod
    def create_learning_path(user_id, name, description, topics):
        """创建学习路径"""
        path = LearningPath(
            user_id=user_id,
            name=name,
            description=description,
            topic_sequence=topics,
            difficulty_curve=LearningPathService._generate_difficulty_curve(len(topics))
        )
        db.session.add(path)
        db.session.commit()
        return path
    
    @staticmethod
    def _generate_difficulty_curve(n_stages):
        """生成难度曲线"""
        return {
            'initial_difficulty': 1,
            'max_difficulty': 3,
            'stages': n_stages,
            'curve_type': 'exponential'
        }
    
    @staticmethod
    def update_progress(path_id, completed_stage):
        """更新学习进度"""
        path = LearningPath.query.get(path_id)
        if path:
            path.current_stage = completed_stage
            path.completion_rate = completed_stage / len(path.topic_sequence)
            path.last_updated = datetime.utcnow()
            db.session.commit()
            return path
        return None

class ActivityTrackingService:
    @staticmethod
    def record_activity(user_id, activity_type, activity_data, time_spent):
        """记录用户活动"""
        activity = UserActivity(
            user_id=user_id,
            activity_type=activity_type,
            activity_data=activity_data,
            time_spent=time_spent
        )
        
        # 计算疲劳度
        recent_activities = UserActivity.query.filter_by(user_id=user_id)\
            .filter(UserActivity.created_at >= datetime.utcnow() - timedelta(hours=24))\
            .all()
            
        total_time = sum(a.time_spent for a in recent_activities)
        activity.fatigue_level = min(total_time / 480, 1.0)  # 假设每天最多学习8小时
        
        # 计算活动效果
        if activity_type == 'problem_solving':
            problem_id = activity_data.get('problem_id')
            is_correct = activity_data.get('is_correct')
            avg_time = Problem.query.get(problem_id).average_time
            
            if is_correct:
                time_factor = min(avg_time / time_spent, 1.0)
                activity.effectiveness_score = 0.7 + 0.3 * time_factor
            else:
                activity.effectiveness_score = 0.3
        
        db.session.add(activity)
        db.session.commit()
        return activity
    
    @staticmethod
    def get_daily_statistics(user_id, date):
        """获取每日统计"""
        activities = UserActivity.query.filter_by(user_id=user_id)\
            .filter(UserActivity.created_at >= date)\
            .filter(UserActivity.created_at < date + timedelta(days=1))\
            .all()
            
        return {
            'total_time': sum(a.time_spent for a in activities),
            'average_effectiveness': sum(a.effectiveness_score for a in activities) / len(activities) if activities else 0,
            'activity_count': len(activities),
            'fatigue_level': max(a.fatigue_level for a in activities) if activities else 0
        } 