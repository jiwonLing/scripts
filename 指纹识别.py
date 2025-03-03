import requests
import whois
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import json
import ssl
import socket
import re

# 禁用SSL警告
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def get_http_headers(url):
    """获取目标网站的HTTP响应头"""
    try:
        response = requests.get(url, verify=False, timeout=10)
        return response.headers
    except Exception as e:
        print(f"Error fetching headers: {str(e)}")
        return None


def analyze_headers(headers):
    """分析HTTP头指纹"""
    fingerprints = {}

    # 服务器类型识别
    server = headers.get('Server', '')
    if 'Apache' in server:
        fingerprints['web_server'] = 'Apache'
    elif 'nginx' in server:
        fingerprints['web_server'] = 'Nginx'
    elif 'IIS' in server:
        fingerprints['web_server'] = 'Microsoft IIS'

    # 后端技术识别
    powered_by = headers.get('X-Powered-By', '')
    if 'PHP' in powered_by:
        fingerprints['backend'] = 'PHP'
    elif 'ASP.NET' in powered_by:
        fingerprints['backend'] = 'ASP.NET'

    # 安全头检测
    security_headers = [
        'Content-Security-Policy',
        'X-Content-Type-Options',
        'Strict-Transport-Security'
    ]
    fingerprints['security_headers'] = {
        h: headers.get(h, 'Not Present') for h in security_headers
    }

    return fingerprints


def analyze_html_content(url):
    """分析HTML内容特征"""
    try:
        response = requests.get(url, verify=False, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        fingerprints = {}

        # Meta标签检测
        meta_generator = soup.find('meta', {'name': 'generator'})
        if meta_generator:
            fingerprints['cms'] = meta_generator.get('content', '')

        # 常见框架检测
        scripts = soup.find_all('script')
        for script in scripts:
            src = script.get('src', '')
            if 'react' in src:
                fingerprints['frontend'] = 'React'
            elif 'vue' in src:
                fingerprints['frontend'] = 'Vue.js'

        # WordPress特征检测
        if '/wp-content/' in response.text:
            fingerprints['cms'] = 'WordPress'
        elif '/media/jui/' in response.text:
            fingerprints['cms'] = 'Joomla'

        return fingerprints
    except Exception as e:
        print(f"HTML analysis error: {str(e)}")
        return {}


def check_common_paths(url):
    """检测常见路径指纹"""
    common_paths = {
        '/wp-admin': 'WordPress',
        '/administrator': 'Joomla',
        '/user/login': 'Drupal',
        '/misc/ajax.js': 'Drupal',
        '/graphql': 'Headless CMS'
    }

    base_url = urlparse(url).scheme + '://' + urlparse(url).netloc
    results = {}

    for path, cms in common_paths.items():
        try:
            response = requests.get(base_url + path, timeout=5, verify=False)
            if response.status_code == 200:
                results[cms] = path
        except:
            continue

    return {'cms_paths': results}


def get_ssl_cert(domain):
    """获取SSL证书信息"""
    context = ssl.create_default_context()
    with socket.create_connection((domain, 443)) as sock:
        with context.wrap_socket(sock, server_hostname=domain) as ssock:
            cert = ssock.getpeercert()

    issuer = dict(x[0] for x in cert['issuer'])
    subject = dict(x[0] for x in cert['subject'])

    return {
        'issuer': issuer.get('organizationName', ''),
        'subject': subject.get('commonName', ''),
        'expiration': cert['notAfter']
    }


def full_fingerprint(url):
    """综合指纹识别"""
    print(f"\n[*] Scanning {url}")

    # WHOIS信息查询
    try:
        domain_info = whois.whois(urlparse(url).netloc)
    except:
        domain_info = {}

    # 综合所有检测结果
    headers = get_http_headers(url)
    results = {
        'url': url,
        'domain_info': {
            'registrar': domain_info.get('registrar', ''),
            'creation_date': str(domain_info.get('creation_date', ''))
        },
        'server_info': analyze_headers(headers) if headers else {},
        'content_analysis': analyze_html_content(url),
        'path_checks': check_common_paths(url),
        'ssl_cert': get_ssl_cert(urlparse(url).netloc)
    }

    return results


if __name__ == '__main__':
    target_url = input("Enter target URL (e.g. https://example.com): ")

    if not re.match(r'^https?://', target_url):
        target_url = 'http://' + target_url

    print("\n[!] Legal Notice: This tool must only be used with explicit authorization")
    print("[!] 法律声明：本工具仅限授权测试使用，未经授权扫描属于违法行为\n")

    fingerprint = full_fingerprint(target_url)
    print(json.dumps(fingerprint, indent=2))
