"""
Custom SEO Tools for Google ADK Agents.
These tools perform actual SEO analysis checks on websites.
"""

import requests
import ssl
import socket
import re
import time
import logging
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from google.adk.tools import FunctionTool

import config

logger = logging.getLogger(__name__)

# Utility functions
def normalize_url(url: str) -> str:
    """Normalize URL by adding https:// if no protocol is specified."""
    url = url.strip()
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    return url


def get_base_url(url: str) -> str:
    """Get base URL (scheme + netloc)."""
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"


def fetch_page(url: str, timeout: int = None) -> Optional[requests.Response]:
    """Fetch a webpage with error handling."""
    timeout = timeout or config.REQUEST_TIMEOUT
    try:
        response = requests.get(url, timeout=timeout, allow_redirects=True)
        return response
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching {url}: {e}")
        return None


# ============================================================
# SECURITY TOOLS
# ============================================================

def check_https_security(url: str) -> Dict[str, Any]:
    """
    Check if the website uses HTTPS and if HTTP redirects to HTTPS.
    
    Args:
        url: The website URL to analyze
        
    Returns:
        Dictionary containing HTTPS security analysis results
    """
    url = normalize_url(url)
    result = {
        'tool': 'check_https_security',
        'url': url,
        'uses_https': False,
        'http_redirects_to_https': False,
        'ssl_valid': False,
        'issues': [],
        'score': 0
    }
    
    try:
        # Check if using HTTPS
        parsed = urlparse(url)
        if parsed.scheme == 'https':
            result['uses_https'] = True
            result['score'] += 40
        
        # Check HTTP to HTTPS redirect
        http_url = url.replace('https://', 'http://')
        response = fetch_page(http_url)
        if response and response.url.startswith('https://'):
            result['http_redirects_to_https'] = True
            result['score'] += 30
        else:
            result['issues'].append('HTTP does not redirect to HTTPS')
        
        # Check SSL validity
        try:
            hostname = parsed.netloc
            context = ssl.create_default_context()
            with socket.create_connection((hostname, 443), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    if cert:
                        result['ssl_valid'] = True
                        result['score'] += 30
        except Exception as ssl_error:
            result['issues'].append(f'SSL certificate issue: {str(ssl_error)}')
        
        if not result['uses_https']:
            result['issues'].append('Website does not use HTTPS')
            
    except Exception as e:
        result['error'] = str(e)
        result['issues'].append(f'Error checking security: {str(e)}')
    
    return result


def check_security_headers(url: str) -> Dict[str, Any]:
    """
    Check for important security headers on the website.
    
    Args:
        url: The website URL to analyze
        
    Returns:
        Dictionary containing security headers analysis
    """
    url = normalize_url(url)
    result = {
        'tool': 'check_security_headers',
        'url': url,
        'headers_found': {},
        'missing_headers': [],
        'score': 0
    }
    
    important_headers = [
        'Strict-Transport-Security',
        'X-Content-Type-Options',
        'X-Frame-Options',
        'X-XSS-Protection',
        'Content-Security-Policy'
    ]
    
    try:
        response = fetch_page(url)
        if response:
            for header in important_headers:
                value = response.headers.get(header)
                if value:
                    result['headers_found'][header] = value
                    result['score'] += 20
                else:
                    result['missing_headers'].append(header)
                    
    except Exception as e:
        result['error'] = str(e)
    
    return result


# ============================================================
# ON-PAGE SEO TOOLS
# ============================================================

def check_title_and_meta(url: str) -> Dict[str, Any]:
    """
    Analyze title tag and meta description of a webpage.
    
    Args:
        url: The website URL to analyze
        
    Returns:
        Dictionary containing title and meta description analysis
    """
    url = normalize_url(url)
    result = {
        'tool': 'check_title_and_meta',
        'url': url,
        'title': None,
        'title_length': 0,
        'title_optimal': False,
        'meta_description': None,
        'meta_description_length': 0,
        'meta_description_optimal': False,
        'issues': [],
        'score': 0
    }
    
    try:
        response = fetch_page(url)
        if not response or response.status_code != 200:
            result['error'] = 'Failed to fetch page'
            return result
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Check title tag
        title_tag = soup.find('title')
        if title_tag and title_tag.text:
            result['title'] = title_tag.text.strip()
            result['title_length'] = len(result['title'])
            
            if 30 <= result['title_length'] <= 60:
                result['title_optimal'] = True
                result['score'] += 25
            elif result['title_length'] < 30:
                result['issues'].append(f'Title too short ({result["title_length"]} chars, optimal: 30-60)')
            else:
                result['issues'].append(f'Title too long ({result["title_length"]} chars, optimal: 30-60)')
        else:
            result['issues'].append('Missing title tag')
        
        # Check meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            result['meta_description'] = meta_desc['content'].strip()
            result['meta_description_length'] = len(result['meta_description'])
            
            if 120 <= result['meta_description_length'] <= 160:
                result['meta_description_optimal'] = True
                result['score'] += 25
            elif result['meta_description_length'] < 120:
                result['issues'].append(f'Meta description too short ({result["meta_description_length"]} chars, optimal: 120-160)')
            else:
                result['issues'].append(f'Meta description too long ({result["meta_description_length"]} chars, optimal: 120-160)')
        else:
            result['issues'].append('Missing meta description')
        
        # Check for duplicate meta descriptions
        all_meta_desc = soup.find_all('meta', attrs={'name': 'description'})
        if len(all_meta_desc) > 1:
            result['issues'].append('Multiple meta description tags found')
            
    except Exception as e:
        result['error'] = str(e)
    
    return result


def check_heading_structure(url: str) -> Dict[str, Any]:
    """
    Analyze heading hierarchy (H1-H6) of a webpage.
    
    Args:
        url: The website URL to analyze
        
    Returns:
        Dictionary containing heading structure analysis
    """
    url = normalize_url(url)
    result = {
        'tool': 'check_heading_structure',
        'url': url,
        'h1_count': 0,
        'h1_text': [],
        'heading_hierarchy': {},
        'has_proper_hierarchy': True,
        'issues': [],
        'score': 0
    }
    
    try:
        response = fetch_page(url)
        if not response or response.status_code != 200:
            result['error'] = 'Failed to fetch page'
            return result
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Count all headings
        for i in range(1, 7):
            headings = soup.find_all(f'h{i}')
            result['heading_hierarchy'][f'h{i}'] = len(headings)
            
            if i == 1:
                result['h1_count'] = len(headings)
                result['h1_text'] = [h.get_text(strip=True)[:100] for h in headings]
        
        # Check H1
        if result['h1_count'] == 0:
            result['issues'].append('Missing H1 tag')
            result['has_proper_hierarchy'] = False
        elif result['h1_count'] == 1:
            result['score'] += 50
        else:
            result['issues'].append(f'Multiple H1 tags found ({result["h1_count"]})')
            result['has_proper_hierarchy'] = False
            result['score'] += 25
        
        # Check hierarchy (shouldn't skip levels)
        prev_level = 0
        for i in range(1, 7):
            count = result['heading_hierarchy'][f'h{i}']
            if count > 0:
                if prev_level > 0 and i > prev_level + 1:
                    result['issues'].append(f'Heading hierarchy skips from H{prev_level} to H{i}')
                    result['has_proper_hierarchy'] = False
                prev_level = i
        
        if result['has_proper_hierarchy'] and result['h1_count'] == 1:
            result['score'] += 50
            
    except Exception as e:
        result['error'] = str(e)
    
    return result


def check_image_alt_tags(url: str) -> Dict[str, Any]:
    """
    Check images for alt text attributes.
    
    Args:
        url: The website URL to analyze
        
    Returns:
        Dictionary containing image alt tag analysis
    """
    url = normalize_url(url)
    result = {
        'tool': 'check_image_alt_tags',
        'url': url,
        'total_images': 0,
        'images_with_alt': 0,
        'images_without_alt': 0,
        'empty_alt_count': 0,
        'alt_coverage_percent': 0,
        'issues': [],
        'score': 0
    }
    
    try:
        response = fetch_page(url)
        if not response or response.status_code != 200:
            result['error'] = 'Failed to fetch page'
            return result
        
        soup = BeautifulSoup(response.text, 'html.parser')
        images = soup.find_all('img')
        result['total_images'] = len(images)
        
        for img in images:
            alt = img.get('alt')
            if alt is None:
                result['images_without_alt'] += 1
            elif alt.strip() == '':
                result['empty_alt_count'] += 1
            else:
                result['images_with_alt'] += 1
        
        if result['total_images'] > 0:
            result['alt_coverage_percent'] = round(
                (result['images_with_alt'] / result['total_images']) * 100, 1
            )
            result['score'] = min(100, result['alt_coverage_percent'])
        else:
            result['score'] = 100  # No images, no issues
        
        if result['images_without_alt'] > 0:
            result['issues'].append(f'{result["images_without_alt"]} images missing alt attribute')
        if result['empty_alt_count'] > 0:
            result['issues'].append(f'{result["empty_alt_count"]} images have empty alt attribute')
            
    except Exception as e:
        result['error'] = str(e)
    
    return result


# ============================================================
# CONTENT ANALYSIS TOOLS
# ============================================================

def analyze_content_quality(url: str) -> Dict[str, Any]:
    """
    Analyze content quality including word count and readability.
    
    Args:
        url: The website URL to analyze
        
    Returns:
        Dictionary containing content quality analysis
    """
    url = normalize_url(url)
    result = {
        'tool': 'analyze_content_quality',
        'url': url,
        'word_count': 0,
        'paragraph_count': 0,
        'avg_paragraph_length': 0,
        'has_sufficient_content': False,
        'issues': [],
        'score': 0
    }
    
    try:
        response = fetch_page(url)
        if not response or response.status_code != 200:
            result['error'] = 'Failed to fetch page'
            return result
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for element in soup(['script', 'style', 'nav', 'footer', 'header']):
            element.decompose()
        
        # Get text content
        text = soup.get_text(separator=' ', strip=True)
        words = text.split()
        result['word_count'] = len(words)
        
        # Count paragraphs
        paragraphs = soup.find_all('p')
        result['paragraph_count'] = len(paragraphs)
        
        if result['paragraph_count'] > 0:
            result['avg_paragraph_length'] = round(result['word_count'] / result['paragraph_count'], 1)
        
        # Scoring based on word count
        if result['word_count'] >= 300:
            result['has_sufficient_content'] = True
            if result['word_count'] >= 1000:
                result['score'] = 100
            elif result['word_count'] >= 500:
                result['score'] = 75
            else:
                result['score'] = 50
        else:
            result['issues'].append(f'Low word count ({result["word_count"]}). Aim for 300+ words for better SEO.')
            result['score'] = 25
            
    except Exception as e:
        result['error'] = str(e)
    
    return result


def check_internal_links(url: str) -> Dict[str, Any]:
    """
    Analyze internal linking structure of a webpage.
    
    Args:
        url: The website URL to analyze
        
    Returns:
        Dictionary containing internal links analysis
    """
    url = normalize_url(url)
    base_url = get_base_url(url)
    result = {
        'tool': 'check_internal_links',
        'url': url,
        'total_links': 0,
        'internal_links': 0,
        'external_links': 0,
        'broken_internal_links': [],
        'has_good_internal_linking': False,
        'issues': [],
        'score': 0
    }
    
    try:
        response = fetch_page(url)
        if not response or response.status_code != 200:
            result['error'] = 'Failed to fetch page'
            return result
        
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a', href=True)
        result['total_links'] = len(links)
        
        for link in links:
            href = link['href']
            
            # Skip anchor links and javascript
            if href.startswith('#') or href.startswith('javascript:'):
                continue
            
            # Check if internal or external
            if href.startswith('/') or href.startswith(base_url):
                result['internal_links'] += 1
            elif href.startswith('http'):
                result['external_links'] += 1
        
        # Score based on internal links
        if result['internal_links'] >= 5:
            result['has_good_internal_linking'] = True
            result['score'] = 100
        elif result['internal_links'] >= 3:
            result['score'] = 75
        elif result['internal_links'] >= 1:
            result['score'] = 50
            result['issues'].append('Consider adding more internal links')
        else:
            result['issues'].append('No internal links found. Internal linking is important for SEO.')
            result['score'] = 25
            
    except Exception as e:
        result['error'] = str(e)
    
    return result


# ============================================================
# PERFORMANCE TOOLS
# ============================================================

def check_page_performance(url: str) -> Dict[str, Any]:
    """
    Check basic page performance metrics.
    
    Args:
        url: The website URL to analyze
        
    Returns:
        Dictionary containing performance analysis
    """
    url = normalize_url(url)
    result = {
        'tool': 'check_page_performance',
        'url': url,
        'response_time_ms': 0,
        'page_size_kb': 0,
        'is_fast': False,
        'issues': [],
        'score': 0
    }
    
    try:
        start_time = time.time()
        response = requests.get(url, timeout=30, allow_redirects=True)
        end_time = time.time()
        
        result['response_time_ms'] = round((end_time - start_time) * 1000)
        result['page_size_kb'] = round(len(response.content) / 1024, 1)
        
        # Score based on response time
        if result['response_time_ms'] < 1000:
            result['is_fast'] = True
            result['score'] = 100
        elif result['response_time_ms'] < 2000:
            result['score'] = 75
        elif result['response_time_ms'] < 3000:
            result['score'] = 50
            result['issues'].append('Page load time is slow (2-3 seconds)')
        else:
            result['score'] = 25
            result['issues'].append(f'Page load time is very slow ({result["response_time_ms"]/1000:.1f} seconds)')
        
        # Check page size
        if result['page_size_kb'] > 3000:
            result['issues'].append(f'Large page size ({result["page_size_kb"]} KB). Consider optimizing.')
            result['score'] = max(0, result['score'] - 25)
            
    except Exception as e:
        result['error'] = str(e)
    
    return result


def check_mobile_friendly(url: str) -> Dict[str, Any]:
    """
    Check for mobile-friendly indicators in the page.
    
    Args:
        url: The website URL to analyze
        
    Returns:
        Dictionary containing mobile-friendliness analysis
    """
    url = normalize_url(url)
    result = {
        'tool': 'check_mobile_friendly',
        'url': url,
        'has_viewport_meta': False,
        'has_responsive_design_hints': False,
        'issues': [],
        'score': 0
    }
    
    try:
        response = fetch_page(url)
        if not response or response.status_code != 200:
            result['error'] = 'Failed to fetch page'
            return result
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Check for viewport meta tag
        viewport = soup.find('meta', attrs={'name': 'viewport'})
        if viewport:
            result['has_viewport_meta'] = True
            result['score'] += 50
        else:
            result['issues'].append('Missing viewport meta tag for mobile responsiveness')
        
        # Check for responsive hints in CSS
        style_tags = soup.find_all('style')
        link_tags = soup.find_all('link', rel='stylesheet')
        
        page_content = response.text.lower()
        if '@media' in page_content or 'responsive' in page_content:
            result['has_responsive_design_hints'] = True
            result['score'] += 50
        
        if not result['has_viewport_meta'] and not result['has_responsive_design_hints']:
            result['issues'].append('No responsive design indicators found')
            
    except Exception as e:
        result['error'] = str(e)
    
    return result


# ============================================================
# INDEXABILITY TOOLS
# ============================================================

def check_robots_and_sitemap(url: str) -> Dict[str, Any]:
    """
    Check robots.txt and sitemap.xml presence and validity.
    
    Args:
        url: The website URL to analyze
        
    Returns:
        Dictionary containing robots.txt and sitemap analysis
    """
    url = normalize_url(url)
    base_url = get_base_url(url)
    result = {
        'tool': 'check_robots_and_sitemap',
        'url': url,
        'has_robots_txt': False,
        'robots_allows_crawling': True,
        'has_sitemap': False,
        'sitemap_url': None,
        'issues': [],
        'score': 0
    }
    
    try:
        # Check robots.txt
        robots_url = f"{base_url}/robots.txt"
        robots_response = fetch_page(robots_url)
        
        if robots_response and robots_response.status_code == 200:
            result['has_robots_txt'] = True
            result['score'] += 25
            
            content = robots_response.text.lower()
            if 'disallow: /' in content and 'disallow: /?' not in content:
                if 'user-agent: *' in content:
                    result['robots_allows_crawling'] = False
                    result['issues'].append('robots.txt may be blocking crawlers')
            
            # Check for sitemap in robots.txt
            for line in robots_response.text.split('\n'):
                if line.lower().startswith('sitemap:'):
                    result['sitemap_url'] = line.split(':', 1)[1].strip()
                    result['has_sitemap'] = True
        else:
            result['issues'].append('No robots.txt found')
        
        # Check sitemap.xml if not found in robots.txt
        if not result['has_sitemap']:
            sitemap_url = f"{base_url}/sitemap.xml"
            sitemap_response = fetch_page(sitemap_url)
            
            if sitemap_response and sitemap_response.status_code == 200:
                result['has_sitemap'] = True
                result['sitemap_url'] = sitemap_url
            else:
                result['issues'].append('No sitemap.xml found')
        
        if result['has_sitemap']:
            result['score'] += 50
        
        if result['robots_allows_crawling']:
            result['score'] += 25
            
    except Exception as e:
        result['error'] = str(e)
    
    return result


def check_meta_robots(url: str) -> Dict[str, Any]:
    """
    Check meta robots tag for indexing directives.
    
    Args:
        url: The website URL to analyze
        
    Returns:
        Dictionary containing meta robots analysis
    """
    url = normalize_url(url)
    result = {
        'tool': 'check_meta_robots',
        'url': url,
        'has_meta_robots': False,
        'is_indexable': True,
        'is_followable': True,
        'robots_content': None,
        'issues': [],
        'score': 100
    }
    
    try:
        response = fetch_page(url)
        if not response or response.status_code != 200:
            result['error'] = 'Failed to fetch page'
            return result
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Check meta robots tag
        meta_robots = soup.find('meta', attrs={'name': 'robots'})
        if meta_robots:
            result['has_meta_robots'] = True
            content = meta_robots.get('content', '').lower()
            result['robots_content'] = content
            
            if 'noindex' in content:
                result['is_indexable'] = False
                result['issues'].append('Page has noindex directive - will not appear in search results')
                result['score'] -= 50
            
            if 'nofollow' in content:
                result['is_followable'] = False
                result['issues'].append('Page has nofollow directive - links will not pass authority')
                result['score'] -= 25
        
        # Check X-Robots-Tag header
        x_robots = response.headers.get('X-Robots-Tag', '').lower()
        if x_robots:
            if 'noindex' in x_robots:
                result['is_indexable'] = False
                result['issues'].append('X-Robots-Tag header contains noindex')
                result['score'] -= 50
                
    except Exception as e:
        result['error'] = str(e)
    
    return result


# ============================================================
# REGISTER TOOLS FOR ADK
# ============================================================

# Create FunctionTool instances for each tool
security_https_tool = FunctionTool(check_https_security)
security_headers_tool = FunctionTool(check_security_headers)

title_meta_tool = FunctionTool(check_title_and_meta)
heading_structure_tool = FunctionTool(check_heading_structure)
image_alt_tool = FunctionTool(check_image_alt_tags)

content_quality_tool = FunctionTool(analyze_content_quality)
internal_links_tool = FunctionTool(check_internal_links)

performance_tool = FunctionTool(check_page_performance)
mobile_friendly_tool = FunctionTool(check_mobile_friendly)

robots_sitemap_tool = FunctionTool(check_robots_and_sitemap)
meta_robots_tool = FunctionTool(check_meta_robots)


# Tool collections by category
SECURITY_TOOLS = [security_https_tool, security_headers_tool]
ONPAGE_SEO_TOOLS = [title_meta_tool, heading_structure_tool, image_alt_tool]
CONTENT_TOOLS = [content_quality_tool, internal_links_tool]
PERFORMANCE_TOOLS = [performance_tool, mobile_friendly_tool]
INDEXABILITY_TOOLS = [robots_sitemap_tool, meta_robots_tool]

ALL_SEO_TOOLS = (
    SECURITY_TOOLS + 
    ONPAGE_SEO_TOOLS + 
    CONTENT_TOOLS + 
    PERFORMANCE_TOOLS + 
    INDEXABILITY_TOOLS
)
