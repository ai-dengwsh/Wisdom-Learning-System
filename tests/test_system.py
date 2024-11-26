import pytest
from app import app, db, init_db
from models import User, Problem, Submission, LearningPath
import json
import os

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        with app.app_context():
            init_db()
            # 创建测试用户
            user = User(username='testuser', email='test@example.com')
            user.set_password('testpass')
            db.session.add(user)
            
            # 创建测试题目
            problem = Problem(
                title='测试题目',
                content='这是一个测试题目的内容',
                difficulty='medium',
                source='test',
                tags=['python', 'algorithms']
            )
            db.session.add(problem)
            
            db.session.commit()
        yield client
        
        # 清理数据库
        with app.app_context():
            db.drop_all()

def test_home_page(client):
    """测试首页"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'\xe6\x99\xba\xe8\x83\xbd\xe5\xad\xa6\xe4\xb9\xa0\xe7\xb3\xbb\xe7\xbb\x9f' in response.data  # "智能学习系统"的UTF-8编码

def test_register(client):
    """测试注册功能"""
    response = client.post('/register', json={
        'username': 'newuser',
        'email': 'new@example.com',
        'password': 'newpass'
    })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['message'] == '注册成功'
    
    # 验证用户是否创建成功
    with app.app_context():
        user = User.query.filter_by(username='newuser').first()
        assert user is not None
        assert user.email == 'new@example.com'

def test_login(client):
    """测试登录功能"""
    # 测试正确的登录信息
    response = client.post('/login', json={
        'username': 'testuser',
        'password': 'testpass'
    })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['message'] == '登录成功'
    
    # 测试错误的密码
    response = client.post('/login', json={
        'username': 'testuser',
        'password': 'wrongpass'
    })
    assert response.status_code == 401

def test_learning_path(client):
    """测试学习路径功能"""
    # 先登录
    client.post('/login', json={
        'username': 'testuser',
        'password': 'testpass'
    })
    
    # 创建学习路径
    response = client.post('/learning-paths', json={
        'name': '测试路径',
        'description': '这是一个测试学习路径',
        'topics': ['python', 'algorithms']
    })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['message'] == '创建成功'
    
    # 验证学习路径是否创建成功
    with app.app_context():
        path = LearningPath.query.filter_by(name='测试路径').first()
        assert path is not None
        assert path.description == '这是一个测试学习路径'
        assert path.topic_sequence == ['python', 'algorithms']

def test_problem_submission(client):
    """测试题目提交功能"""
    # 先登录
    client.post('/login', json={
        'username': 'testuser',
        'password': 'testpass'
    })
    
    # 获取测试题目
    with app.app_context():
        problem = Problem.query.filter_by(title='测试题目').first()
        
    # 提交答案
    response = client.post(f'/submit/{problem.id}', json={
        'is_correct': True,
        'time_spent': 300,
        'code': 'print("test")'
    })
    assert response.status_code == 200
    
    # 验证提交记录是否创建成功
    with app.app_context():
        submission = Submission.query.filter_by(
            user_id=User.query.filter_by(username='testuser').first().id,
            problem_id=problem.id
        ).first()
        assert submission is not None
        assert submission.is_correct == True
        assert submission.time_spent == 300

def test_user_statistics(client):
    """测试用户统计功能"""
    # 先登录
    client.post('/login', json={
        'username': 'testuser',
        'password': 'testpass'
    })
    
    # 获取统计信息
    response = client.get('/api/statistics')
    assert response.status_code == 200
    data = json.loads(response.data)
    
    # 验证统计信息格式
    assert 'total_time' in data
    assert 'activity_count' in data
    assert 'average_effectiveness' in data
    assert 'fatigue_level' in data

def test_error_pages(client):
    """测试错误页面"""
    # 测试404页面
    response = client.get('/nonexistent')
    assert response.status_code == 404
    assert b'404' in response.data
    assert b'\xe9\xa1\xb5\xe9\x9d\xa2\xe6\x9c\xaa\xe6\x89\xbe\xe5\x88\xb0' in response.data  # "页面未找到"的UTF-8编码
    
    # 测试无权限访问
    response = client.get('/learning-paths/999')
    assert response.status_code == 404 