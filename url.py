import os
import sys
import pycurl


CONNECT_TIMEOUT = 10


def urlgrab(url_and_fnames, connect_timeout=CONNECT_TIMEOUT):
    def show_code(c):
        print c.getinfo(pycurl.HTTP_CODE), c.getinfo(pycurl.EFFECTIVE_URL)

    opts = []
    fps = []
    try:
        for url, fname in url_and_fnames:
            fps.append(open(fname, 'w'))
            opt = {
                pycurl.URL: url.url,
                pycurl.SSL_VERIFYPEER: 0,
                pycurl.SSL_VERIFYHOST: 0,
                pycurl.FOLLOWLOCATION: 1,
                pycurl.CONNECTTIMEOUT: connect_timeout,
                pycurl.WRITEDATA: fps[-1],
                'callback': show_code,
                }
            if url.userpwd:
                opt[pycurl.USERPWD] = url.userpwd
            opts.append(opt)
        return poll(opts)
    except:
        raise
    finally:
        for fp in fps:
            fp.close()


def urlexists(urls, connect_timeout=CONNECT_TIMEOUT):
    exists = {}
    def check_200(url):
        def callback(c):
            code = c.getinfo(pycurl.HTTP_CODE)
            print code, c.getinfo(pycurl.EFFECTIVE_URL)
            exists[url] = (code == 200)
        return callback

    opts = []
    for url in urls:
        opt = {
            pycurl.URL: url.url,
            pycurl.SSL_VERIFYPEER: 0,
            pycurl.SSL_VERIFYHOST: 0,
            pycurl.FOLLOWLOCATION: 1,
            pycurl.CONNECTTIMEOUT: connect_timeout,
            pycurl.NOBODY: 1,
            'callback': check_200(url),
            }
        if url.userpwd:
            opt[pycurl.USERPWD] = url.userpwd
        opts.append(opt)

    poll(opts)
    return exists


def poll(opts, timeout=1):
    def create_multi():
        m = pycurl.CurlMulti()
        m.handles = []

        for opt in opts:
            c = pycurl.Curl()
            for key, val in opt.iteritems():
                if key == 'callback':
                    c.callback = val
                else:
                    c.setopt(key, val)
            m.add_handle(c)
            m.handles.append(c)
        return m

    def loop(m):
        num_handles = len(m.handles)
        while num_handles:
            while 1:
                ret, num_handles = m.perform()
                if ret != pycurl.E_CALL_MULTI_PERFORM:
                    break

            # show progress
            sys.stdout.write('.')
            sys.stdout.flush()

            try:
                m.select(timeout)
            except KeyboardInterrupt:
                print 'User press CTRL-C'
                raise # or break
        print

    def callback(m):
        for c in m.handles:
            if hasattr(c, 'callback'):
                c.callback(c)

    def cleanup(m):
        for c in m.handles:
            m.remove_handle(c)
            c.close()
        del m.handles

    m = create_multi()
    try:
        loop(m)
    except:
        raise
    finally:
        callback(m)
        cleanup(m)


class URL(object):

    def __init__(self, url, user=None, passwd=None):
        self.url = url
        self.user = user
        self.passwd = passwd

    @property
    def userpwd(self):
        if not self.user:
            return ''
        if not self.passwd:
            return self.user
        return ':'.join([self.user, self.passwd])

    def __hash__(self):
        return hash(self.url)

    def __str__(self):
        return self.url


def test_head():
    urls =  [ URL(i) for i in ['http://www.baidu.com',
        'http://www.google.com',
        'http://www.cnn.com',
        'http://www.xxxxxxxxxxxx12341234123412341234.com',
        ]]

    for url, status in urlexists(urls).iteritems():
        print 'exists:', status, url

def test_fetch():
    urls =  [ URL(i) for i in ['http://www.baidu.com',
        'http://www.google.com',
        'http://www.cnn.com',
        'http://www.xxxxxxxxxxxx12341234123412341234.com',
        ]]

    url_and_fnames = [ (url, os.path.join('download', os.path.basename(url.url))) for url in urls ]
    urlgrab(url_and_fnames)


if __name__ == '__main__':
    test_head()
    test_fetch()
