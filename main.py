import twint

crawler_username_list = [
    'DavidSpaceDuck',
    'DmitryDeceiver',
    'umaaaaaa',
    'yg_fool',
    'antonkudin',
]

def crawl_image(username):
    crawler_username = username
    c = twint.Config()
    c.Username = crawler_username
    c.Media = True

    # c.Limit = 20 # 先限制20个
    c.Proxy_host = '127.0.0.1'
    c.Proxy_port = '7890'
    c.Proxy_type = 'HTTP'
    c.Database = crawler_username + '.db'

    twint.run.Search(c)

if __name__ == '__main__':
    for username in crawler_username_list:
        crawl_image(username)
