from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from models import db, User, Problem, Submission, LearningPath
from services import UserService, ProblemService, RecommendationService
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    data = request.get_json()
    user = User.query.filter_by(username=data.get('username')).first()
    
    if user and user.check_password(data.get('password')):
        UserService.update_last_login(user)
        login_user(user, remember=data.get('remember-me', False))
        return jsonify({'message': '登录成功'})
    return jsonify({'message': '用户名或密码错误'}), 401

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    
    data = request.get_json()
    if User.query.filter_by(username=data.get('username')).first():
        return jsonify({'message': '用户名已存在'}), 400
    if User.query.filter_by(email=data.get('email')).first():
        return jsonify({'message': '邮箱已被注册'}), 400
    
    user = User(username=data.get('username'), email=data.get('email'))
    user.set_password(data.get('password'))
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': '注册成功'})

@app.route('/learning-paths', methods=['GET', 'POST'])
@login_required
def learning_paths():
    if request.method == 'GET':
        paths = LearningPath.query.all()
        return render_template('learning_paths.html', paths=paths)
    
    data = request.get_json()
    path = LearningPath(
        name=data.get('name'),
        description=data.get('description'),
        topic_sequence=data.get('topics', [])
    )
    db.session.add(path)
    db.session.commit()
    return jsonify({'message': '创建成功'})

@app.route('/learning-paths/<int:path_id>')
@login_required
def learning_path_detail(path_id):
    path = LearningPath.query.get_or_404(path_id)
    return render_template('learning_path_detail.html', path=path)

@app.route('/submit/<int:problem_id>', methods=['POST'])
@login_required
def submit_solution(problem_id):
    data = request.get_json()
    problem = Problem.query.get_or_404(problem_id)
    
    submission = Submission(
        user_id=current_user.id,
        problem_id=problem_id,
        code=data.get('code'),
        is_correct=data.get('is_correct'),
        time_spent=data.get('time_spent')
    )
    db.session.add(submission)
    db.session.commit()
    return jsonify({'message': '提交成功'})

@app.route('/api/statistics')
@login_required
def get_statistics():
    stats = UserService.get_user_statistics(current_user)
    return jsonify(stats)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True) 