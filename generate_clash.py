import re
import yaml
import utils
from jinja2 import Template
import os

def _generate_proxy_groups(proxy_group, proxy_names):
    p_type = proxy_group['type']
    groups = []
    if 'proxy-groups' in proxy_group:
        groups.extend(proxy_group['proxy-groups'])
    if 'regex' in proxy_group:
        for name in proxy_names:
            if re.search(proxy_group['regex'], name):
                groups.append(name)
    if len(groups) == 0:
        return None
    if p_type == 'select':
        return {'name': proxy_group['name'], 'type': proxy_group['type'], 'proxies': groups}
    elif p_type == 'url-test':
        return {'name': proxy_group['name'], 'type': proxy_group['type'], 'proxies': groups,
                'url': proxy_group['test-url'], 'interval': proxy_group['interval'], 'tolerance': proxy_group['tolerance']}
    return None

def _generate_ruleset(ruleset):
    rules = []
    group_name = ruleset['proxy-group']
    if 'urls' in ruleset:
        urls = ruleset['urls']
        if isinstance(urls, str):
            urls = [urls]
        for url in urls:
            content = utils.get_url_content_cached(url)
            rows = content.split('\n')
            for row in rows:
                if row.startswith('#') or len(row) == 0 or row.isspace():
                    continue
                parts = row.split(',')
                if parts[0] == 'IP-CIDR':
                    rules.append([parts[0], parts[1], group_name, parts[2]])
                elif parts[0] in ['USER-AGENT', 'URL-REGEX']:
                    continue
                else:
                    rules.append([parts[0], parts[1], group_name])
    elif 'value' in  ruleset:
        value = ruleset['value']
        rules.append([value, group_name])
    return [','.join(rule) for rule in rules]

def _generate_ruleset_group(proxy_names: list):
    path = "config/ruleset_proxygroup.yaml"
    if not os.path.exists(path):
        path = "/defaults/config/ruleset_proxygroup.yaml"
    data = yaml.safe_load(utils.get_file_content(path))
    clash_rules = [rule for ruleset in data['ruleset'] for rule in _generate_ruleset(ruleset) ]
    clash_proxy_groups = [_generate_proxy_groups(proxy_group, proxy_names) for proxy_group in data['proxy-groups']]
    return clash_proxy_groups, clash_rules

class IndentDumper(yaml.SafeDumper):
    def increase_indent(self, flow=False, indentless=False):
        return super().increase_indent(flow, False)


def generate_clash_yaml(clash_proxies):
    if os.path.exists('config/clash-base-proxies.yaml'):
        local_proxies = yaml.safe_load(utils.get_file_content("config/clash-base-proxies.yaml"))
        clash_proxies.extend(local_proxies['proxies'])
    proxy_names = [proxy['name'] for proxy in clash_proxies]

    clash_proxy_groups, clash_rules = _generate_ruleset_group(proxy_names)

    path = 'config/clash-base-template.yaml'
    if not os.path.exists(path):
        path = '/defaults/config/clash-base-template.yaml'
    template = Template(utils.get_file_content(path))
    clash_proxies = yaml.dump({'proxies': clash_proxies}, allow_unicode=True, default_flow_style=False, indent=2, Dumper=IndentDumper)
    clash_proxy_groups = yaml.dump({'proxy-groups': clash_proxy_groups}, allow_unicode=True, default_flow_style=False, indent=2, Dumper=IndentDumper)
    clash_rules = yaml.dump({'rules': clash_rules}, allow_unicode=True, default_flow_style=False, indent=2, Dumper=IndentDumper)
    return template.render(proxies=clash_proxies, proxy_groups=clash_proxy_groups, rules=clash_rules)
