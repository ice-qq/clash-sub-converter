import yaml

import utils


def get_proxy_list(sub_yaml):
    sub_yaml = yaml.safe_load(sub_yaml)
    return sub_yaml['proxies']