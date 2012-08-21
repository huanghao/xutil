import urlparse


class SafeURL(object):

    def __init__(self, url, user=None, passwd=None):
        self.components, inline_user, inline_passwd = strip_auth_info(url)
        self.cleaned_url = urlparse.urlunsplit(self.components)

        if inline_user and user or inline_passwd and passwd:
            raise ValueError('Duplication of auth item for %s' % str(self))
        self.user = inline_user or user
        self.passwd = inline_passwd or passwd

    def __str__(self):
        return self.cleaned_url

    @property
    def host
    @property
    def with_auth(self):
        pass


