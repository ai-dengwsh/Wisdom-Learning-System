import math
import time
from datetime import datetime

class KnowledgeGraph:
    def __init__(self):
        self.graph = {}
        self.node_weights = {}  # 节点权重
        self.edge_types = {}    # 边的类型
        
    def add_node(self, node, weight=1.0):
        """添加带权重的节点"""
        if node not in self.graph:
            self.graph[node] = []
            self.node_weights[node] = weight
            
    def add_edge(self, from_node, to_node, edge_type="related"):
        """添加带类型的边"""
        if from_node in self.graph:
            self.graph[from_node].append(to_node)
            if from_node not in self.edge_types:
                self.edge_types[from_node] = {}
            self.edge_types[from_node][to_node] = edge_type
            
    def get_prerequisites(self, node):
        """获取指定节点的所有前置知识点"""
        prerequisites = []
        for from_node, to_nodes in self.graph.items():
            if node in to_nodes:
                if self.edge_types[from_node][node] == "prerequisite":
                    prerequisites.append(from_node)
        return prerequisites
    
    def find_learning_path(self, start_node, end_node):
        """使用广度优先搜索找到最短学习路径"""
        if start_node not in self.graph or end_node not in self.graph:
            return None
            
        visited = {start_node}
        queue = [(start_node, [start_node])]
        
        while queue:
            vertex, path = queue.pop(0)
            for next_node in self.graph[vertex]:
                if next_node == end_node:
                    return path + [next_node]
                if next_node not in visited:
                    visited.add(next_node)
                    queue.append((next_node, path + [next_node]))
        return None

class AdaptiveLearningSystem:
    def __init__(self):
        self.learning_patterns = {}
        self.content_difficulty = {}
        self.user_profiles = {}
        self.knowledge_graph = KnowledgeGraph()
        self.learning_sessions = {}  # 记录学习会话
    
    class UserProfile:
        def __init__(self):
            self.strengths = {}  # 强项领域
            self.weaknesses = {}  # 弱项领域
            self.learning_speed = {}  # 各领域学习速度
            self.preferred_times = []  # 最佳学习时间
            self.attention_span = {}  # 专注时长
            self.learning_style = None  # 学习风格
            self.fatigue_pattern = {}  # 疲劳度模式
            self.forgetting_curves = {}  # 遗忘曲线
            self.best_learning_hours = []  # 最佳学习时间段
    
    def analyze_learning_ability(self, user_id, topic_data):
        profile = self.user_profiles.get(user_id)
        
        # 分析学习能力指标
        ability_metrics = {
            'comprehension_speed': self._calculate_comprehension_speed(topic_data),
            'accuracy_rate': self._calculate_accuracy(topic_data),
            'consistency': self._analyze_learning_consistency(topic_data),
            'difficulty_handling': self._analyze_difficulty_adaptation(topic_data),
            'fatigue_level': self._analyze_fatigue_level(topic_data),
            'retention_rate': self._calculate_retention_rate(user_id, topic_data)
        }
        
        # 更新用户画像
        self._update_user_profile(profile, ability_metrics)
        return ability_metrics
    
    def _calculate_comprehension_speed(self, topic_data):
        """计算理解速度"""
        total_time = topic_data.get('completion_time', 0)
        correct_count = sum(1 for attempt in topic_data['exercise_attempts'] if attempt['correct'])
        if total_time > 0:
            return correct_count / total_time
        return 0
    
    def _calculate_accuracy(self, topic_data):
        """计算准确率"""
        attempts = topic_data['exercise_attempts']
        if not attempts:
            return 0
        correct_count = sum(1 for attempt in attempts if attempt['correct'])
        return correct_count / len(attempts)
    
    def _analyze_learning_consistency(self, topic_data):
        """分析学习一致性"""
        times = [attempt['time_spent'] for attempt in topic_data['exercise_attempts']]
        if not times:
            return 0
        avg_time = sum(times) / len(times)
        variance = sum((t - avg_time) ** 2 for t in times) / len(times)
        return 1 / (1 + variance)  # 归一化处理
    
    def _analyze_difficulty_adaptation(self, topic_data):
        """分析难度适应性"""
        return topic_data.get('correct_rate', 0)
    
    def _analyze_fatigue_level(self, topic_data):
        """分析学习疲劳度"""
        attempts = topic_data['exercise_attempts']
        if not attempts:
            return 0
            
        # 分析答题时间变化趋势
        times = [attempt['time_spent'] for attempt in attempts]
        if len(times) < 2:
            return 0
            
        # 计算时间增长率
        time_increases = [times[i+1] - times[i] for i in range(len(times)-1)]
        avg_increase = sum(time_increases) / len(time_increases)
        
        # 计算正确率变化
        correct_trend = [1 if attempt['correct'] else 0 for attempt in attempts]
        correct_changes = [correct_trend[i+1] - correct_trend[i] for i in range(len(correct_trend)-1)]
        avg_correct_change = sum(correct_changes) / len(correct_changes)
        
        # 综合评估疲劳度
        fatigue_score = (avg_increase * 0.6 + (-avg_correct_change) * 0.4)
        return min(max(fatigue_score, 0), 1)  # 归一化到0-1范围
    
    def _calculate_retention_rate(self, user_id, topic_data):
        """计算知识点保留率（基于艾宾浩斯遗忘曲线）"""
        if user_id not in self.learning_sessions:
            return 1.0
            
        topic_id = topic_data['topic_id']
        current_time = time.time()
        last_review_time = self.learning_sessions.get(user_id, {}).get(topic_id, current_time)
        hours_passed = (current_time - last_review_time) / 3600
        
        # 使用艾宾浩斯遗忘曲线公式
        retention_rate = math.exp(-0.1 * hours_passed)
        return retention_rate
    
    def analyze_best_learning_time(self, user_id, performance_history):
        """分析用户最佳学习时间段"""
        if not performance_history:
            return []
            
        # 按小时统计学习效果
        hourly_performance = {}
        for record in performance_history:
            hour = record['timestamp'].hour
            if hour not in hourly_performance:
                hourly_performance[hour] = []
            hourly_performance[hour].append(record['performance_score'])
        
        # 计算每个小时的平均表现
        best_hours = []
        for hour, scores in hourly_performance.items():
            avg_score = sum(scores) / len(scores)
            best_hours.append((hour, avg_score))
        
        # 返回表现最好的3个时间段
        best_hours.sort(key=lambda x: x[1], reverse=True)
        return [hour for hour, _ in best_hours[:3]]
    
    def recommend_next_steps(self, user_id):
        profile = self.user_profiles[user_id]
        current_progress = self.learning_patterns[user_id]
        
        # 考虑疲劳度和最佳学习时间
        current_fatigue = self._analyze_current_fatigue(user_id)
        current_hour = datetime.now().hour
        
        # 基于多个因素的综合推荐
        recommendations = {
            'immediate_next': self._find_optimal_next_topic(profile),
            'weak_areas': self._identify_weak_areas(profile),
            'reinforcement': self._get_reinforcement_content(profile),
            'challenge': self._suggest_challenge_content(profile),
            'break_needed': current_fatigue > 0.7,
            'best_time_to_study': current_hour in profile.best_learning_hours
        }
        
        # 动态调整建议
        if current_fatigue > 0.7:
            recommendations['suggested_break_duration'] = self._calculate_break_duration(current_fatigue)
        
        return recommendations
    
    def _analyze_current_fatigue(self, user_id):
        """分析当前疲劳度"""
        if user_id not in self.learning_sessions:
            return 0.0
            
        recent_sessions = self.learning_sessions[user_id].get('recent_activities', [])
        if not recent_sessions:
            return 0.0
            
        # 计算最近学习时长和强度
        total_duration = sum(session['duration'] for session in recent_sessions[-5:])
        avg_intensity = sum(session['intensity'] for session in recent_sessions[-5:]) / 5
        
        # 综合评估疲劳度
        fatigue = (total_duration * 0.7 + avg_intensity * 0.3) / 100
        return min(fatigue, 1.0)
    
    def _calculate_break_duration(self, fatigue_level):
        """根据疲劳度计算建议休息时长（分钟）"""
        base_duration = 15
        return int(base_duration * (1 + fatigue_level))
    
    def track_progress(self, user_id, topic_id, performance_data):
        """跟踪学习进度并动态调整推荐"""
        profile = self.user_profiles[user_id]
        
        # 更新学习会话记录
        if user_id not in self.learning_sessions:
            self.learning_sessions[user_id] = {}
        self.learning_sessions[user_id][topic_id] = time.time()
        
        # 更新学习模式和进度
        if user_id not in self.learning_patterns:
            self.learning_patterns[user_id] = {}
        self.learning_patterns[user_id][topic_id] = performance_data
        
        # 更新疲劳度模式
        current_fatigue = self._analyze_fatigue_level(performance_data)
        if 'fatigue_pattern' not in profile.__dict__:
            profile.fatigue_pattern = {}
        profile.fatigue_pattern[topic_id] = current_fatigue
        
        # 分析表现并调整策略
        adjustments = {
            'difficulty_change': self._adjust_difficulty(performance_data),
            'pace_change': self._adjust_learning_pace(performance_data),
            'focus_areas': self._identify_focus_areas(performance_data),
            'revision_needs': self._assess_revision_needs(performance_data),
            'fatigue_status': {
                'level': current_fatigue,
                'break_recommended': current_fatigue > 0.7,
                'suggested_break': self._calculate_break_duration(current_fatigue)
            }
        }
        
        return adjustments
    
    def _adjust_difficulty(self, performance_data):
        """调整难度"""
        return 0.1 if performance_data['accuracy'] > 0.8 else -0.1
    
    def _adjust_learning_pace(self, performance_data):
        """调整学习节奏"""
        return 'increase' if performance_data['completion_rate'] > 0.9 else 'maintain'
    
    def _identify_focus_areas(self, performance_data):
        """识别重点领域"""
        return ['problem_solving'] if performance_data['accuracy'] < 0.7 else []
    
    def _assess_revision_needs(self, performance_data):
        """评估复习需求"""
        return performance_data['accuracy'] < 0.6
    
    def _update_user_profile(self, profile, metrics):
        """更新用户画像"""
        if not profile:
            return
        
        # 基于新的度量更新用户能力指标
        if 'learning_speed' not in profile.__dict__:
            profile.learning_speed = {'current': 0}
        profile.learning_speed['current'] = metrics['comprehension_speed']
        
        if 'strengths' not in profile.__dict__:
            profile.strengths = {}
        if 'accuracy_history' not in profile.strengths:
            profile.strengths['accuracy_history'] = []
        profile.strengths['accuracy_history'].append(metrics['accuracy_rate'])
    
    def generate_personalized_plan(self, user_id):
        profile = self.user_profiles[user_id]
        current_state = self.learning_patterns[user_id]
        
        # 生成个性化学习计划
        plan = {
            'recommended_topics': self._get_recommended_topics(profile),
            'daily_schedule': self._create_optimal_schedule(profile),
            'content_format': self._adapt_content_format(profile.learning_style),
            'difficulty_progression': self._calculate_difficulty_curve(profile)
        }
        
        return plan
    
    def _adapt_content_format(self, learning_style):
        formats = {
            'visual': ['图表', '视频', '思维导图'],
            'auditory': ['音频讲解', '口头练习', '讨论'],
            'kinesthetic': ['实践项目', '动手实验', '角色扮演']
        }
        return formats.get(learning_style, formats['visual'])
    
    def _get_recommended_topics(self, profile):
        """获取推荐主题"""
        return ['math_101', 'physics_102']  # 示例推荐
    
    def _create_optimal_schedule(self, profile):
        """创建最优学习计划"""
        return {
            'morning': ['math_101'],
            'afternoon': ['physics_102'],
            'evening': ['review']
        }
    
    def _calculate_difficulty_curve(self, profile):
        """计算难度曲线"""
        return {
            'initial': 0.5,
            'increment': 0.1,
            'max_difficulty': 0.9
        }
    
    def _analyze_knowledge_gaps(self, profile):
        """分析知识缺口"""
        return ['algebra_basics', 'geometry_concepts']
    
    def _evaluate_learning_readiness(self, profile):
        """评估学习准备度"""
        return 0.8
    
    def _select_best_topic(self, gaps, readiness):
        """选择最佳主题"""
        return gaps[0] if gaps else None
    
    def _calculate_learning_time(self, profile):
        """计算学习时间"""
        return 45  # 示例：45分钟
    
    def _check_prerequisites(self):
        """检查前置条件"""
        return ['basic_math']
    
    def _customize_resources(self, learning_style):
        """自定义学习资源"""
        return ['video_tutorials', 'interactive_exercises']
    
    def _find_optimal_next_topic(self, profile):
        """找到最佳下一个主题"""
        # 实现最佳主题推荐算法
        pass
    
    def _identify_weak_areas(self, profile):
        """识别薄弱领域"""
        # 实现薄弱领域识别算法
        pass
    
    def _get_reinforcement_content(self, profile):
        """获取强化内容"""
        # 实现强化内容推荐算法
        pass
    
    def _suggest_challenge_content(self, profile):
        """建议挑战内容"""
        # 实现挑战内容推荐算法
        pass

class TestAdaptiveLearningSystem:
    def __init__(self):
        self.learning_system = AdaptiveLearningSystem()
        
    def run_all_tests(self):
        """运行所有测试用例"""
        print("开始测试自适应学习系统...")
        self.test_user_profile_creation()
        self.test_learning_ability_analysis()
        self.test_personalized_plan()
        self.test_progress_tracking()
        self.test_knowledge_graph()
        self.test_fatigue_analysis()
        self.test_best_learning_time()
        
    def test_user_profile_creation(self):
        """测试用户画像创建"""
        print("\n1. 测试用户画像创建...")
        
        # 创建测试用户
        user_id = "test_user_001"
        self.learning_system.user_profiles[user_id] = self.learning_system.UserProfile()
        profile = self.learning_system.user_profiles[user_id]
        
        # 设置初始测试数据
        profile.learning_style = "visual"
        profile.strengths = {"数学": 0.8, "物理": 0.7}
        profile.weaknesses = {"化学": 0.4}
        profile.learning_speed = {"数学": 1.2, "物理": 1.0, "化学": 0.8}
        
        print(f"用户画像创建成功: {profile.__dict__}")
        
    def test_learning_ability_analysis(self):
        """测试学习能力分析"""
        print("\n2. 测试学习能力分析...")
        
        # 模拟学习数据
        topic_data = {
            "topic_id": "math_101",
            "completion_time": 45,  # 分钟
            "correct_rate": 0.85,
            "exercise_attempts": [
                {"question_id": 1, "time_spent": 5, "correct": True},
                {"question_id": 2, "time_spent": 8, "correct": False},
                {"question_id": 3, "time_spent": 6, "correct": True}
            ]
        }
        
        metrics = self.learning_system.analyze_learning_ability("test_user_001", topic_data)
        print(f"学习能力分析结果: {metrics}")
        
    def test_personalized_plan(self):
        """测试个性化学习计划生成"""
        print("\n3. 测试个性化学习计划生成...")
        
        # 初始化学习模式数据
        self.learning_system.learning_patterns["test_user_001"] = {
            "current_topic": "math_101",
            "progress": 0.6,
            "recent_performance": [0.85, 0.90, 0.82]
        }
        
        plan = self.learning_system.generate_personalized_plan("test_user_001")
        print(f"生成的个性化学习计划: {plan}")
        
    def test_progress_tracking(self):
        """测试学习进度追踪"""
        print("\n4. 测试学习进度追踪...")
        
        # 模拟性能数据
        performance_data = {
            "topic_id": "math_101",
            "completion_rate": 0.9,
            "accuracy": 0.85,
            "time_spent": 45,
            "difficulty_level": 3,
            "engagement_level": 0.8
        }
        
        adjustments = self.learning_system.track_progress(
            "test_user_001", 
            "math_101", 
            performance_data
        )
        print(f"进度追踪调整结果: {adjustments}")
    
    def test_knowledge_graph(self):
        """测试知识图谱功能"""
        print("\n5. 测试知识图谱...")
        
        # 创建测试知识图谱
        self.learning_system.knowledge_graph.add_node("algebra_basics", weight=1.0)
        self.learning_system.knowledge_graph.add_node("linear_equations", weight=0.8)
        self.learning_system.knowledge_graph.add_edge("algebra_basics", "linear_equations", "prerequisite")
        
        # 测试路径查找
        path = self.learning_system.knowledge_graph.find_learning_path("algebra_basics", "linear_equations")
        print(f"学习路径: {path}")
        
        # 测试前置知识查找
        prereqs = self.learning_system.knowledge_graph.get_prerequisites("linear_equations")
        print(f"前置知识: {prereqs}")
    
    def test_fatigue_analysis(self):
        """测试疲劳度分析"""
        print("\n6. 测试疲劳度分析...")
        
        # 模拟学习数据
        topic_data = {
            "topic_id": "math_101",
            "exercise_attempts": [
                {"time_spent": 5, "correct": True},
                {"time_spent": 6, "correct": True},
                {"time_spent": 8, "correct": False},
                {"time_spent": 10, "correct": False}
            ]
        }
        
        fatigue_level = self.learning_system._analyze_fatigue_level(topic_data)
        print(f"疲劳度分析结果: {fatigue_level}")
    
    def test_best_learning_time(self):
        """测试最佳学习时间分析"""
        print("\n7. 测试最佳学习时间分析...")
        
        # 模拟历史表现数据
        performance_history = [
            {"timestamp": datetime.now().replace(hour=9), "performance_score": 0.9},
            {"timestamp": datetime.now().replace(hour=14), "performance_score": 0.7},
            {"timestamp": datetime.now().replace(hour=20), "performance_score": 0.8}
        ]
        
        best_hours = self.learning_system.analyze_best_learning_time("test_user_001", performance_history)
        print(f"最佳学习时间段: {best_hours}")

if __name__ == "__main__":
    test_system = TestAdaptiveLearningSystem()
    test_system.run_all_tests() 