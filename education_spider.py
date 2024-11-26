import asyncio
from playwright.async_api import async_playwright
import json
import time

class EducationSpider:
    def __init__(self):
        self.questions_db = []
        
    async def setup_browser(self):
        """设置浏览器"""
        self.playwright = await async_playwright().start()
        # 使用Edge浏览器
        self.browser = await self.playwright.chromium.launch(
            channel='msedge',  # 使用Edge浏览器
            headless=False,    # 设置为False可以看到浏览过程
            args=[
                '--start-maximized',  # 最大化窗口
                '--disable-blink-features=AutomationControlled'  # 禁用自动化检测
            ]
        )
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},  # 设置视窗大小
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0'
        )
        self.page = await self.context.new_page()
        
        # 设置超时时间
        self.page.set_default_timeout(30000)  # 30秒
        
        # 启用JavaScript
        await self.context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
    async def fetch_leetcode_problems(self, page=1, limit=50):
        """获取LeetCode题目列表"""
        try:
            print("正在获取LeetCode题目...")
            await self.page.goto('https://leetcode.cn/problemset/all/')
            
            # 等待页面加载完成
            await self.page.wait_for_load_state('networkidle')
            await asyncio.sleep(2)  # 额外等待
            
            # 等待题目列表加载
            await self.page.wait_for_selector('.odd\\:bg-layer-1')
            
            # 滚动页面以加载更多内容
            for _ in range(3):
                await self.page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                await asyncio.sleep(1)
            
            questions = []
            # 获取题目列表
            problem_items = await self.page.query_selector_all('.odd\\:bg-layer-1')
            
            for item in problem_items[:limit]:
                try:
                    # 提取题目信息
                    title_element = await item.query_selector('a.h-5')
                    title_text = await title_element.text_content() if title_element else "未知标题"
                    
                    difficulty_element = await item.query_selector('.difficulty')
                    difficulty_text = await difficulty_element.text_content() if difficulty_element else "medium"
                    
                    # 获取题目链接
                    href = await title_element.get_attribute('href') if title_element else None
                    
                    question = {
                        'title': title_text.strip(),
                        'difficulty': self._convert_leetcode_difficulty(difficulty_text.strip()),
                        'source': 'leetcode',
                        'tags': ['算法', '编程'],
                        'url': f"https://leetcode.cn{href}" if href else None,
                        'content': await self._fetch_leetcode_problem_content(href if href else None)
                    }
                    
                    questions.append(question)
                    print(f"成功获取LeetCode题目: {title_text.strip()}")
                    await asyncio.sleep(0.5)  # 防止请求过快
                    
                except Exception as e:
                    print(f"处理题目时出错: {str(e)}")
                    continue
                
            return questions
        except Exception as e:
            print(f"获取LeetCode题目列表失败: {str(e)}")
            return []
        
    async def fetch_nowcoder_problems(self, page=1, limit=50):
        """获取牛客网题目列表"""
        try:
            print("正在获取牛客网题目...")
            await self.page.goto('https://www.nowcoder.com/exam/company')
            
            # 等待页面加载完成
            await self.page.wait_for_load_state('networkidle')
            await asyncio.sleep(2)  # 额外等待
            
            # 等待题目列表加载
            await self.page.wait_for_selector('.question-item')
            
            # 滚动页面以加载更多内容
            for _ in range(3):
                await self.page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                await asyncio.sleep(1)
            
            questions = []
            # 获取题目列表
            problem_items = await self.page.query_selector_all('.question-item')
            
            for item in problem_items[:limit]:
                try:
                    # 提取题目信息
                    title_element = await item.query_selector('.question-title')
                    title_text = await title_element.text_content() if title_element else "未知标题"
                    
                    company_element = await item.query_selector('.company-name')
                    company_text = await company_element.text_content() if company_element else "未知公司"
                    
                    # 获取题目链接
                    href = await title_element.get_attribute('href') if title_element else None
                    
                    question = {
                        'title': title_text.strip(),
                        'difficulty': 'medium',
                        'source': 'nowcoder',
                        'tags': ['面试题', company_text.strip()],
                        'url': f"https://www.nowcoder.com{href}" if href else None,
                        'content': f"题目：{title_text.strip()}\n请访问牛客网查看完整题目内容。"
                    }
                    
                    questions.append(question)
                    print(f"成功获取牛客网题目: {title_text.strip()}")
                    await asyncio.sleep(0.5)  # 防止请求过快
                    
                except Exception as e:
                    print(f"处理题目时出错: {str(e)}")
                    continue
                
            return questions
        except Exception as e:
            print(f"获取牛客网题目列表失败: {str(e)}")
            return []
    
    async def _fetch_leetcode_problem_content(self, href):
        """获取LeetCode题目详情"""
        if not href:
            return "题目链接获取失败"
            
        try:
            # 创建新标签页访问题目详情
            page = await self.context.new_page()
            await page.goto(f"https://leetcode.cn{href}")
            await page.wait_for_load_state('networkidle')
            await asyncio.sleep(3)  # 等待内容加载
            
            try:
                # 尝试获取题目内容
                content_element = await page.wait_for_selector('.content__1Y2H', timeout=5000)
                if content_element:
                    content_text = await content_element.text_content()
                else:
                    # 如果找不到指定选择器，尝试获取整个题目区域
                    content_text = await page.evaluate('''() => {
                        const content = document.querySelector('[role="main"]');
                        return content ? content.innerText : "题目内容获取失败";
                    }''')
            except Exception as e:
                print(f"使用主选择器获取内容失败，尝试备用方法: {str(e)}")
                try:
                    # 备用方法：获取题目描述区域
                    content_text = await page.evaluate('''() => {
                        const elements = Array.from(document.querySelectorAll('div[class*="description"]'));
                        return elements.map(el => el.innerText).join('\\n');
                    }''')
                except Exception as e2:
                    print(f"备用方法也失败了: {str(e2)}")
                    content_text = "题目内容获取失败"
            
            await page.close()
            return content_text.strip() if content_text else "题目内容获取失败"
        except Exception as e:
            print(f"获取题目详情失败: {str(e)}")
            return "题目内容获取失败"
    
    def _convert_leetcode_difficulty(self, difficulty):
        """转换LeetCode难度等级"""
        difficulty = difficulty.lower()
        if '简单' in difficulty or 'easy' in difficulty:
            return 'easy'
        elif '中等' in difficulty or 'medium' in difficulty:
            return 'medium'
        else:
            return 'hard'
    
    def save_questions(self, filename='questions_db.json'):
        """保存题目到文件"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.questions_db, f, ensure_ascii=False, indent=2)
        print(f"已保存 {len(self.questions_db)} 道题目到 {filename}")
    
    def load_questions(self, filename='questions_db.json'):
        """从文件加载题目"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                self.questions_db = json.load(f)
            print(f"已加载 {len(self.questions_db)} 道题目")
        except FileNotFoundError:
            self.questions_db = []
            print("题目数据库文件不存在，将创建新的数据库")
    
    async def update_question_database(self):
        """更新题目数据库"""
        print("开始更新题目数据库...")
        
        try:
            # 设置浏览器
            await self.setup_browser()
            
            # 加载现有题目
            self.load_questions()
            
            # 获取新题目
            leetcode_questions = await self.fetch_leetcode_problems(limit=10)  # 先获取10道题测试
            await asyncio.sleep(2)  # 等待一下再获取下一个网站的题目
            nowcoder_questions = await self.fetch_nowcoder_problems(limit=10)  # 先获取10道题测试
            
            # 更新数据库
            new_questions = leetcode_questions + nowcoder_questions
            
            # 去重（基于标题）
            existing_titles = {q['title'] for q in self.questions_db}
            unique_new_questions = [q for q in new_questions if q['title'] not in existing_titles]
            
            # 添加新题目
            self.questions_db.extend(unique_new_questions)
            
            # 保存更新后的数据库
            self.save_questions()
            
            print(f"数据库更新完成，新增 {len(unique_new_questions)} 道题目")
            return len(unique_new_questions)
        finally:
            # 关闭浏览器
            await self.browser.close()
            await self.playwright.stop()

async def main():
    spider = EducationSpider()
    await spider.update_question_database()

if __name__ == "__main__":
    asyncio.run(main()) 