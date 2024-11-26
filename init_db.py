from app import app, db
from models import User, Problem, LearningPath
import json
import os

def init_db():
    with app.app_context():
        # 创建所有表
        db.create_all()
        
        # 如果没有管理员用户，创建一个
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@example.com'
            )
            admin.set_password('admin123')
            db.session.add(admin)
        
        # 如果存在示例题目数据，导入它们
        if os.path.exists('example_problems.json'):
            with open('example_problems.json', 'r', encoding='utf-8') as f:
                problems_data = json.load(f)
                for data in problems_data:
                    if not Problem.query.filter_by(title=data['title']).first():
                        problem = Problem(
                            title=data['title'],
                            content=data['content'],
                            difficulty=data['difficulty'],
                            source=data.get('source', 'system'),
                            tags=data.get('tags', [])
                        )
                        db.session.add(problem)
        
        # 创建默认学习路径
        if not LearningPath.query.filter_by(name='Python基础学习路径').first():
            basic_path = LearningPath(
                name='Python基础学习路径',
                description='适合Python初学者的基础学习路径，包含基本语法、数据结构和算法入门。',
                topic_sequence=['python-basics', 'data-structures', 'basic-algorithms'],
                daily_problems=3
            )
            db.session.add(basic_path)
        
        if not LearningPath.query.filter_by(name='算法进阶学习路径').first():
            advanced_path = LearningPath(
                name='算法进阶学习路径',
                description='适合有一定基础的开发者，专注于算法和数据结构的深入学习。',
                topic_sequence=['advanced-algorithms', 'dynamic-programming', 'graph-theory'],
                daily_problems=5
            )
            db.session.add(advanced_path)
        
        # 提交所有更改
        db.session.commit()

if __name__ == '__main__':
    init_db()
    print('数据库初始化完成！') 