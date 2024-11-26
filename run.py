import threading
from education_spider import EducationSpider
from app import app

def run_spider():
    """运行爬虫定期更新题库"""
    spider = EducationSpider()
    spider.update_question_database()

def main():
    # 启动爬虫线程
    spider_thread = threading.Thread(target=run_spider)
    spider_thread.daemon = True
    spider_thread.start()
    
    # 启动Flask应用
    app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == '__main__':
    main() 