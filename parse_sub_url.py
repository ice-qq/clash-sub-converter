import re
from urllib.parse import urlparse, parse_qs
import json
import yaml
import utils
from jinja2 import Environment, FileSystemLoader

def _parse_host(hostname: str) -> {}:
    pattern = r"^(.*?)@(.*?):(.*)$"
    match = re.match(pattern, hostname)

    if match:
        uuid, host, port = match.groups()
        return uuid, host, port
    else:
        return None, hostname, None

def parse_url(proxy_url: str) -> {}:
    if proxy_url.startswith('vmess://'):
        proxy = utils.decode_base64(proxy_url.removeprefix('vmess://'))
        proxy = json.loads(proxy)
        return {'type': 'vmess', 'name': proxy['ps'], 'json': proxy}
    else:
        parsed_url = urlparse(proxy_url)
        uuid, host, port = _parse_host(parsed_url.netloc)
        params = parse_qs(parsed_url.query)
        if parsed_url.scheme == 'ss':
            parts = utils.decode_base64(uuid).split(":")
            proxy_info = {'type': parsed_url.scheme, 'name': parsed_url.fragment,
                    'json': {'name': parsed_url.fragment, 'uuid': parts[1], 'host': host,
                             'port': parsed_url.port, 'path': parsed_url.path,
                             'cipher': parts[0]}}
        else:
            proxy_info = {'type': parsed_url.scheme, 'name': parsed_url.fragment, 'json': {'name': parsed_url.fragment, 'uuid': uuid, 'host': host,
                                   'port': parsed_url.port, 'path': parsed_url.path}}
        proxy_info['json'].update({f"params.{k}": v for k, v in params.items()})
        return proxy_info

env = Environment(loader=FileSystemLoader('template'))

_clash_vmess_template = env.get_template("clash_vmess.j2")

def _generate_vmess(name, p_type, json):
    vmess_yaml =  _clash_vmess_template.render(name=name, p_type=p_type, json=json)
    return yaml.safe_load(vmess_yaml)

_clash_ss_template = env.get_template("clash_ss.j2")

def _generate_ss(name, p_type, json):
    return yaml.safe_load(_clash_ss_template.render(name=name, p_type=p_type, json=json))

_clash_trojan_template = env.get_template("clash_trojan.j2")

def _generate_trojan(name, p_type, json):
    return yaml.safe_load(_clash_trojan_template.render(name=name, p_type=p_type, json=json))

_clash_hysteria_template = env.get_template("clash_hysteria.j2")

def _generate_hysteria(name, p_type, json):
    return yaml.safe_load(_clash_hysteria_template.render(name=name, p_type=p_type, json=json))

_clash_hysteria2_template = env.get_template("clash_hysteria2.j2")


def _generate_hysteria2(name, p_type, json):
    return yaml.safe_load(_clash_hysteria2_template.render(name=name, p_type=p_type, json=json))

_clash_ssr_template = env.get_template("clash_ssr.j2")

def _generate_ssr(name, p_type, json):
    return yaml.safe_load(_clash_ssr_template.render(name=name, p_type=p_type, json=json))

_clash_vless_template = env.get_template("clash_vless.j2")


def _generate_vless(name, p_type, json):
    return {'name': name, 'server': json['host'], 'port': json['port'], 'type': p_type, 'uuid': json['uuid'],
            'client-fingerprint': json['fp'], 'servername': json['spx'],
            'reality-opts': {
                'public-key': json['pbk'],
                'short-id': json['sid']}
            }


def _generate_proxy(proxy):
    p_type = proxy['type']
    json = proxy['json']
    name = proxy['name']
    if p_type == 'ss':
        return _generate_ss(name, p_type, json)
    elif p_type == 'vmess':
        return _generate_vmess(name, p_type, json)
    elif p_type == 'trojan':
        return _generate_trojan(name, p_type, json)
    elif p_type == 'hysteria':
        return _generate_hysteria(name, p_type, json)
    elif p_type == 'hysteria2':
        return _generate_hysteria2(name, p_type, json)
    elif p_type == 'ssr':
        return _generate_ssr(name, p_type, json)
    elif p_type == 'vless':
        return _generate_vless(name, p_type, json)
    else:
        return None


def get_proxies_list() -> list:
    proxies = utils.decode_base64(utils.get_file_content("template/update.dat"))
    proxies = proxies.split('\r\n')
    proxy_list = []
    for proxy in proxies:
        if len(proxy) == 0:
            continue
        proxy = utils.unquote(proxy)
        proxy = parse_url(proxy)
        proxy = _generate_proxy(proxy)
        proxy_list.append(proxy)
    return proxy_list