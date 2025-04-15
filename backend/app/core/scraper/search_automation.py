import asyncio
import logging
import logging.handlers
import os
from difflib import SequenceMatcher
from dataclasses import dataclass
from functools import lru_cache
from datetime import datetime, timedelta
from playwright.async_api import async_playwright
from typing import List, Tuple, Optional, Dict
from urllib.parse import quote
import argparse
from rich.console import Console
from rich.table import Table
from rich.progress import Progress
from rich.prompt import Prompt
from rich import print as rprint

# 更新日志配置
def setup_logging():
    logger = logging.getLogger('ecloud_searcher')
    
    # 防止重复添加 handlers
    if logger.handlers:
        return logger
        
    logger.setLevel(logging.DEBUG)
    
    # 创建日志目录
    log_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
        'logs'
    )
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, 'search_automation.log')
    
    # 文件处理器 - 按天切割日志
    file_handler = logging.handlers.TimedRotatingFileHandler(
        filename=log_file,  # 使用绝对路径
        when='midnight',
        interval=1,
        backupCount=7,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # 格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# 使用单例模式管理 logger
logger = setup_logging()

@dataclass
class SearchResult:
    title: str
    content: str
    url: str
    score: float = 0.0

@dataclass
class SearchConfig:
    base_url: str
    timeout: int
    max_results: int
    cache_ttl: int
    min_score: float
    
    @classmethod
    def from_file(cls, filename: str) -> "SearchConfig":
        # 从配置文件加载配置
        pass

class ECloudSearcher:
    def __init__(self):
        # 直接使用全局 logger，不再创建新实例
        self.logger = logging.getLogger('ecloud_searcher')
        self.base_url = "https://ecloud.10086.cn"
        self.help_center_url = "https://ecloud.10086.cn/op-help-center"
        self.search_url = "https://ecloud.10086.cn/op-help-center/search-engine/search/"
        self.doc_article_url = "https://ecloud.10086.cn/op-help-center/doc/article/"
        self.timeout = 30000
        self.cache = {}
        self.cache_ttl = timedelta(hours=24)

    def _get_cache_key(self, query: str) -> str:
        return query.lower().strip()

    def _get_cached_result(self, query: str) -> Optional[List[SearchResult]]:
        cache_key = self._get_cache_key(query)
        if cache_key in self.cache:
            timestamp, results = self.cache[cache_key]
            if datetime.now() - timestamp < self.cache_ttl:
                return results
        return None

    def _build_full_url(self, result_link: str) -> str:
        """根据不同类型的result_link构建完整的URL"""
        if result_link.isdigit():
            return f"{self.doc_article_url}{result_link}"
        elif result_link.startswith("/op-help-center"):
            return f"{self.base_url}{result_link}"
        return result_link

    def _calculate_similarity(self, query: str, text: str) -> float:
        """改进的相似度计算，增加多维度匹配"""
        self.logger.debug(f"计算相似度 - 查询词长度: {len(query)}, 文本长度: {len(text)}")
        if not text:
            return 0.0
        
        # 预处理文本
        query = query.lower().strip()
        text = text.lower().strip()
        
        # 1. 精确匹配检查 (20% 权重)
        exact_match_score = 1.0 if query in text else 0.0
        
        # 2. 分词处理和TF-IDF计算 (35% 权重)
        query_words = set(query.split())
        text_words = set(text.split())
        
        # 计算词频和权重
        word_weights = {}
        for word in query_words:
            # 计算词在文本中的频率
            word_count = text.count(word)
            # 长词给予更高权重
            length_boost = len(word) / len(max(query_words, key=len))
            word_weights[word] = (1 + (0.5 * word_count)) * length_boost
        
        # 计算加权匹配分数
        common_words = query_words & text_words
        weighted_matches = sum(word_weights.get(word, 0) for word in common_words)
        total_weight = sum(word_weights.values()) or 1
        tfidf_score = weighted_matches / total_weight
        
        # 3. 序列匹配 (25% 权重)
        sequence_score = SequenceMatcher(None, query, text).ratio()
        
        # 4. N-gram 匹配 (20% 权重)
        def get_ngrams(text: str, n: int) -> set:
            return set(text[i:i+n] for i in range(len(text)-n+1))
        
        # 使用bi-grams和tri-grams
        query_bigrams = get_ngrams(query, 2)
        text_bigrams = get_ngrams(text, 2)
        query_trigrams = get_ngrams(query, 3)
        text_trigrams = get_ngrams(text, 3)
        
        bigram_similarity = (
            len(query_bigrams & text_bigrams) / 
            (len(query_bigrams | text_bigrams) or 1)
        )
        trigram_similarity = (
            len(query_trigrams & text_trigrams) / 
            (len(query_trigrams | text_trigrams) or 1)
        )
        ngram_score = (bigram_similarity + trigram_similarity) / 2
        
        # 计算最终得分
        final_score = (
            exact_match_score * 0.20 +
            tfidf_score * 0.35 +
            sequence_score * 0.25 +
            ngram_score * 0.20
        )
        
        # 根据文本长度进行惩罚
        length_ratio = min(len(text) / len(query), 5.0) / 5.0
        final_score *= (0.8 + 0.2 * length_ratio)
        
        self.logger.debug(
            f"相似度计算结果:\n"
            f"- 精确匹配得分: {exact_match_score:.4f}\n"
            f"- TF-IDF得分: {tfidf_score:.4f}\n"
            f"- 序列匹配得分: {sequence_score:.4f}\n"
            f"- N-gram得分: {ngram_score:.4f}\n"
            f"- 最终得分: {final_score:.4f}"
        )
        
        return final_score

    async def _extract_result_details(self, result_element) -> SearchResult:
        """提取搜索结果的详细信息"""
        try:
            self.logger.debug("开始提取结果详情")
            # 更灵活的选择器链
            title_selectors = [
                "h3",
                ".title",
                ".heading",
                "a >> text",
                "[class*='title']"
            ]
            
            # 修复标题提取逻辑
            title = ""
            for selector in title_selectors:
                try:
                    title_elements = await result_element.locator(selector).all()
                    if title_elements:  # 检查是否找到了元素
                        title = await title_elements[0].inner_text()
                        title = title.strip()
                        if title:  # 如果找到有效标题就退出循环
                            break
                except Exception as e:
                    self.logger.debug(f"使用选择器 {selector} 提取标题失败: {str(e)}")
                    continue
                    
            if not title:
                title = await result_element.inner_text()
                
            # 修复内容提取逻辑
            content_selectors = [
                ".description",
                ".summary",
                ".content",
                "p",
                "[class*='content']"
            ]
            
            content = ""
            for selector in content_selectors:
                try:
                    content_elements = await result_element.locator(selector).all()
                    if content_elements:  # 检查是否找到了元素
                        content = await content_elements[0].inner_text()
                        content = content.strip()
                        if content:  # 如果找到有效内容就退出循环
                            break
                except Exception as e:
                    self.logger.debug(f"使用选择器 {selector} 提取内容失败: {str(e)}")
                    continue
                    
            if not content:
                content = await result_element.inner_text()
                if title in content:
                    content = content.replace(title, "").strip()
            
            # 修复链接提取逻辑
            try:
                link_elements = await result_element.locator("a").all()
                link = await link_elements[0].get_attribute("href") if link_elements else ""
                full_url = self._build_full_url(link) if link else ""
            except Exception as e:
                self.logger.error(f"提取链接失败: {str(e)}")
                full_url = ""
            
            self.logger.debug(f"成功提取结果: {title[:30]}...")
            return SearchResult(
                title=title or "无标题",
                content=content or "无内容",
                url=full_url or "",
                score=0.0
            )
        except Exception as e:
            self.logger.error(f"提取结果详情失败: {str(e)}", exc_info=True)
            return SearchResult(
                title="解析错误",
                content=str(e),
                url="",
                score=0.0
            )

    async def _do_search(self, query: str, max_results: int = 10) -> List[SearchResult]:
        """执行搜索并返回多个结果"""
        self.logger.debug(f"开始执行搜索，查询词: {query}, 最大结果数: {max_results}")
        browser = None  # 初始化browser变量
        
        async with async_playwright() as p:
            try:
                # 添加浏览器安装检查
                try:
                    browser = await p.chromium.launch(headless=True)
                except Exception as browser_error:
                    self.logger.error("浏览器启动失败，尝试安装浏览器")
                    import subprocess
                    try:
                        subprocess.run(["python3", "-m", "playwright", "install", "chromium"])
                    except Exception as e:
                        self.logger.error(f"安装 Playwright 失败: {e}")
                        raise
                    browser = await p.chromium.launch(headless=True)
                
                self.logger.debug("浏览器已启动")
                
                context = await browser.new_context()
                page = await context.new_page()
                
                encoded_query = quote(query)
                search_page_url = f"{self.search_url}?q={encoded_query}"
                self.logger.info(f"访问搜索页面: {search_page_url}")
                
                await page.goto(search_page_url, timeout=self.timeout)
                await page.wait_for_load_state("networkidle")
                self.logger.debug("页面加载完成")
                
                selectors = [
                    ".search-result-item",
                    ".result-item",
                    ".search-list li",
                    ".list-item",
                    "div[class*='result']"
                ]
                
                results = []
                for selector in selectors:
                    if await page.locator(selector).count() > 0:
                        elements = await page.locator(selector).all()
                        # 只获取指定数量的结果
                        results = elements[:max_results]
                        break
                
                if not results:
                    self.logger.info("未找到相关结果")
                    return [SearchResult(
                        title="未找到相关结果",
                        content="",
                        url="",
                        score=0.0
                    )]
                
                self.logger.info(f"找到 {len(results)} 个搜索结果")
                # 获取详细结果并计算相关性得分
                search_results = []
                for result in results:
                    result_details = await self._extract_result_details(result)
                    
                    # 分别计算标题和内容的相关性得分
                    title_score = self._calculate_similarity(query, result_details.title)
                    content_score = self._calculate_similarity(query, result_details.content)
                    
                    # 根据内容长度调整内容得分权重
                    content_length = len(result_details.content)
                    if content_length < 50:  # 内容过短可能不够相关
                        content_weight = 0.2
                    elif content_length > 500:  # 内容较长可能更相关
                        content_weight = 0.4
                    else:
                        content_weight = 0.3
                        
                    # 计算综合得分
                    title_weight = 1 - content_weight
                    result_details.score = (title_score * title_weight + 
                                          content_score * content_weight)
                    
                    search_results.append(result_details)
                
                # 按相关性得分排序
                search_results.sort(key=lambda x: x.score, reverse=True)
                return search_results
                
            except Exception as e:
                self.logger.error(f"搜索过程出错: {str(e)}", exc_info=True)
                return [SearchResult(
                    title=f"搜索出错: {str(e)}",
                    content="",
                    url="",
                    score=0.0
                )]
            finally:
                if browser:
                    await browser.close()
                    self.logger.debug("浏览器已关闭")

    async def search(self, query: str, max_retries: int = 3) -> List[SearchResult]:
        """添加重试机制的搜索方法"""
        self.logger.info(f"开始搜索: {query}")
        cached_result = self._get_cached_result(query)
        if cached_result:
            return cached_result

        for attempt in range(max_retries):
            try:
                results = await self._do_search(query)
                cache_key = self._get_cache_key(query)
                self.cache[cache_key] = (datetime.now(), results)
                return results
            except Exception as e:
                if attempt == max_retries - 1:
                    self.logger.error(f"搜索失败，已重试{max_retries}次: {str(e)}", exc_info=True)
                    raise
                await asyncio.sleep(1 * (attempt + 1))  # 指数退避

    async def get_best_answer(self, query: str) -> dict:
        """获取最佳答案并分析"""
        self.logger.info(f"开始获取最佳答案，查询词: {query}")
        start_time = datetime.now()
        
        search_results = await self.search(query)
        best_result = search_results[0] if search_results else None
        
        if best_result:
            self.logger.info(
                f"找到最佳匹配 - 标题: {best_result.title[:30]}... "
                f"相关度: {best_result.score:.4f}"
            )
        else:
            self.logger.warning("未找到匹配结果")
            
        processing_time = (datetime.now() - start_time).total_seconds()
        self.logger.info(f"处理完成，耗时: {processing_time:.2f}秒")
        
        analyzed_result = {
            "question": query,
            "answer": best_result.content if best_result else "未找到相关结果",
            "title": best_result.title if best_result else "",
            "source_url": best_result.url if best_result else "",
            "confidence": best_result.score if best_result else 0.0,
            "alternative_results": [
                {
                    "title": r.title,
                    "url": r.url,
                    "score": r.score
                } for r in search_results[1:3]  # 包含2个备选结果
            ] if len(search_results) > 1 else []
        }
        return analyzed_result

class ECloudSearcherCLI:
    def __init__(self):
        self.console = Console()
        self.searcher = ECloudSearcher()

    def display_results(self, result: dict):
        """使用 Rich 库美化结果显示"""
        # 创建主要结果表格
        table = Table(title="搜索结果", show_header=True, header_style="bold magenta")
        table.add_column("字段", style="cyan")
        table.add_column("内容", style="green")
        
        table.add_row("问题", result['question'])
        table.add_row("答案", result['answer'])
        table.add_row("标题", result['title'])
        table.add_row("来源", result['source_url'])
        table.add_row("置信度", f"{result['confidence']:.4f}")
        
        self.console.print(table)
        
        # 显示备选结果
        if result['alternative_results']:
            alt_table = Table(title="备选结果", show_header=True, header_style="bold blue")
            alt_table.add_column("标题", style="cyan")
            alt_table.add_column("相关度", style="green")
            alt_table.add_column("URL", style="yellow")
            
            for alt in result['alternative_results']:
                alt_table.add_row(
                    alt['title'],
                    f"{alt['score']:.4f}",
                    alt['url']
                )
            
            self.console.print(alt_table)

    async def interactive_mode(self):
        """交互式搜索模式"""
        self.console.print("[bold green]欢迎使用移动云帮助中心搜索工具[/bold green]")
        self.console.print("输入 'quit' 或 'exit' 退出程序\n")
        
        while True:
            try:
                query = Prompt.ask("[bold cyan]请输入搜索问题[/bold cyan]")
                if query.lower() in ('quit', 'exit'):
                    break
                
                # 修复进度条实现
                with Progress(
                    "[progress.description]{task.description}",
                    transient=True
                ) as progress:
                    # 设置具体的total值，避免None
                    task = progress.add_task("[cyan]搜索中...", total=100)
                    result = await self.searcher.get_best_answer(query)
                    # 完成后更新进度
                    progress.update(task, completed=100)
                
                self.display_results(result)
                print("\n" + "="*50 + "\n")
                
            except KeyboardInterrupt:
                self.console.print("\n[yellow]程序已终止[/yellow]")
                break
            except Exception as e:
                self.logger.error(f"搜索出错: {str(e)}", exc_info=True)
                self.console.print(f"[bold red]错误: {str(e)}[/bold red]")

async def main():
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='移动云帮助中心搜索工具')
    parser.add_argument('-q', '--query', help='要搜索的问题')
    parser.add_argument('-i', '--interactive', action='store_true', help='启动交互式模式')
    args = parser.parse_args()
    
    cli = ECloudSearcherCLI()
    
    try:
        if args.interactive or not args.query:
            await cli.interactive_mode()
        else:
            with Progress() as progress:
                task = progress.add_task("[cyan]搜索中...", total=None)
                result = await cli.searcher.get_best_answer(args.query)
                progress.update(task, completed=100)
            cli.display_results(result)
            
    except Exception as e:
        cli.console.print(f"[bold red]错误: {str(e)}[/bold red]")

if __name__ == "__main__":
    asyncio.run(main())
