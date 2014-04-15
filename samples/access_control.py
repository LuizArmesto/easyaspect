import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from easyaspect import Aspect, Pointcut, around


class Repository(object):
    def __init__(self):
        self.content = {
            'index': 'Index Content',
            'page A': 'Page A Content',
            'page B': 'Page B Content'
        }

    def read(self, req):
        page = req.get('page', None)
        return self.content.get(page, 'Not Found')


class AccessControl(Aspect):
    protected_pages = ['page A']
    allowed_users = ['admin']

    read = Pointcut('Repository.read')

    @around(read)
    def check_read_permission(cls, method_name, next, obj, req):
        page = req.get('page', None)
        user = req.get('user', None)
        if page not in cls.protected_pages or user in cls.allowed_users:
            return next(obj, req)
        else:
            return 'You don\'t have permission to read "{}"'.format(page)


if __name__ == '__main__':
    repo = Repository()

    print 'Reading index:', repo.read({'page': 'index'})
    print 'Reading page A:', repo.read({'page': 'page A'})
    print 'Reading page B:', repo.read({'page': 'page B'})
    """
    output:

        Reading index: Index Content
        Reading page A: You don't have permission to read "pageA"
        Reading page B: Page B Content
    """

    print 'Reading page A as admin:', repo.read(
        {'page': 'page A', 'user': 'admin'})
    """
    output:

        Reading page A as admin: Page A Content
    """
