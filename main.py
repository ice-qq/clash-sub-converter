from flask import Flask, Response, g, request
import generate_clash
import parse_sub_yaml
import utils
import yaml
import os

app = Flask(__name__)

def get_sub_urls():
    if not os.path.exists('config/sub-urls.yaml'):
        utils.logger.error('sub-urls.yaml not found')
        raise FileNotFoundError('sub-urls.yaml not found')
    sub_urls_yaml = yaml.safe_load(utils.get_file_content('config/sub-urls.yaml'))
    urls = sub_urls_yaml['sub-urls']
    if isinstance(urls, str):
        urls = [urls]
    return urls

def get_sub_proxies(urls):
    proxies = []
    sub_infos = []
    for url in urls:
        sub_yaml, sub_info = utils.get_clash_sub_content(url)
        proxies.extend(parse_sub_yaml.get_proxy_list(sub_yaml))
        sub_infos.append(sub_info)
    return proxies, sub_infos


@app.route('/sub', methods=['GET'])
def get_sub():
    g.cache = request.args.get('cache', True)
    proxies, sub_infos = get_sub_proxies(get_sub_urls())
    clash_yaml = generate_clash.generate_clash_yaml(proxies)
    response = Response(clash_yaml, mimetype='text/html')
    response.headers['Subscription-Userinfo'] = sub_infos[0]
    return response


if __name__ == '__main__':
    # get_sub()
    app.run(host='0.0.0.0', debug=True, port=5000)