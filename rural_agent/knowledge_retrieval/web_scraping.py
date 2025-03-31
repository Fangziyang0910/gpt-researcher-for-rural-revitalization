import requests
from bs4 import BeautifulSoup
import re
from typing import Tuple, List, Dict, Any
from urllib.parse import urljoin, urlparse

class WebScraperInterface:
    """网页内容抓取接口，基于BeautifulSoup实现"""
    
    def __init__(self, user_agent: str = None):
        """
        初始化网页抓取接口
        
        参数:
            user_agent: 自定义User-Agent字符串，用于HTTP请求
        """
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": user_agent or "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        })
    
    def scrape(self, url: str) -> Tuple[str, List[Dict[str, Any]], str]:
        """
        抓取指定URL的网页内容
        
        参数:
            url: 要抓取的网页URL
            
        返回:
            元组 (内容文本, 图片URL列表, 页面标题)
        """
        try:
            response = self.session.get(url, timeout=15)
            soup = BeautifulSoup(response.content, "lxml", from_encoding=response.encoding)
            
            # 清理网页内容
            soup = self._clean_soup(soup)
            
            # 提取文本内容
            content = self._get_text_from_soup(soup)
            
            # 提取相关图片
            image_urls = self._get_relevant_images(soup, url)
            
            # 提取标题
            title = self._extract_title(soup)
            
            return content, image_urls, title
            
        except Exception as e:
            print(f"抓取网页时发生错误：{str(e)}")
            return "", [], ""
    
    def scrape_multiple(self, urls: List[str]) -> List[Dict[str, Any]]:
        """
        抓取多个URL的内容
        
        参数:
            urls: URL列表
            
        返回:
            字典列表，每个字典包含url、raw_content、image_urls和title字段
        """
        results = []
        for url in urls:
            content, images, title = self.scrape(url)
            if content and len(content) > 100:  # 只保留有效内容
                results.append({
                    "url": url,
                    "raw_content": content,
                    "image_urls": images,
                    "title": title
                })
        return results
    
    def _clean_soup(self, soup: BeautifulSoup) -> BeautifulSoup:
        """清理BeautifulSoup对象，移除无关内容"""
        # 移除脚本、样式、页脚、页眉等标签
        for tag in soup.find_all([
            "script", "style", "footer", "header", 
            "nav", "menu", "sidebar", "svg"
        ]):
            tag.decompose()
        
        # 移除具有特定class的标签
        disallowed_class_set = {"nav", "menu", "sidebar", "footer", "ad", "advertisement"}
        for tag in soup.find_all(attrs={"class": lambda x: x and any(c in disallowed_class_set for c in x.split())}):
            tag.decompose()
            
        return soup
    
    def _get_text_from_soup(self, soup: BeautifulSoup) -> str:
        """从BeautifulSoup对象提取文本内容"""
        text = soup.get_text(strip=True, separator="\n")
        # 移除多余的空白
        text = re.sub(r"\s{2,}", " ", text)
        return text
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """提取网页标题"""
        return soup.title.string if soup.title else ""
    
    def _get_relevant_images(self, soup: BeautifulSoup, url: str) -> List[Dict[str, Any]]:
        """提取网页中的相关图片"""
        image_urls = []
        
        try:
            # 查找所有img标签
            all_images = soup.find_all('img', src=True)
            
            for img in all_images:
                img_src = urljoin(url, img['src'])
                if img_src.startswith(('http://', 'https://')):
                    score = 0
                    # 根据class判断相关性
                    if any(cls in img.get('class', []) for cls in ['header', 'featured', 'hero', 'thumbnail', 'main', 'content']):
                        score = 4  # 高分
                    # 根据尺寸判断相关性
                    elif img.get('width') and img.get('height'):
                        width = self._parse_dimension(img['width'])
                        height = self._parse_dimension(img['height'])
                        if width and height:
                            if width >= 2000 and height >= 1000:
                                score = 3  # 中高分（非常大的图片）
                            elif width >= 1600 or height >= 800:
                                score = 2  # 中分
                            elif width >= 800 or height >= 500:
                                score = 1  # 低分
                            else:
                                continue  # 跳过小图片
                    
                    image_urls.append({'url': img_src, 'score': score})
            
            # 按得分排序（从高到低）
            sorted_images = sorted(image_urls, key=lambda x: x['score'], reverse=True)
            
            return sorted_images[:5]  # 最多返回5张图片
        
        except Exception as e:
            print(f"提取图片时发生错误：{str(e)}")
            return []
    
    def _parse_dimension(self, value: str) -> int:
        """解析尺寸值，处理px单位"""
        if isinstance(value, str) and value.lower().endswith('px'):
            value = value[:-2]  # 移除'px'后缀
        try:
            return int(value)
        except (ValueError, TypeError):
            return None 