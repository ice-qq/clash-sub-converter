import base64
from urllib.parse import unquote
import requests
from flask import g
import requests_cache
import logging

requests_cache.install_cache('clash_cache', expire_after=300)

logger = logging.getLogger('werkzeug')  # Flask 默认的日志器

def get_url_content_cached(url: str) -> str:
    if g.get("cache", True):
        return get_url_content(url)
    else:
        with requests_cache.disabled():
            return get_url_content(url)

def get_url_content(url: str) -> str:
    response = requests.get(url)
    response.raise_for_status()
    logger.info(f"url: {url}, cache:{response.from_cache}")
    return response.text

def get_clash_sub_content(url: str) -> tuple[str, {}]:
    headers = {
        'User-Agent': 'clashmeta'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    sub_info = response.headers.get('Subscription-Userinfo')
    return response.text, sub_info


def decode_base64(encoded_str: str) -> str:
    decoded_bytes = base64.b64decode(encoded_str)
    return decoded_bytes.decode('utf-8')


def encode_base64(decoded_str: str) -> str:
    encoded_bytes = base64.b64encode(decoded_str.encode('utf-8'))
    return encoded_bytes.decode('utf-8')


def get_file_content(path: str) -> str:
    with open(path, "r+", encoding='utf-8') as file:
        content = file.read()
    return content


def write_file(path: str, content: str):
    with open(path, "w", encoding='utf-8') as file:
        file.write(content)


def url_decoded(url: str) -> str:
    return unquote(url)