import itertools

from lxml import etree
from lxml.cssselect import CSSSelector



class XQuery(object):

    def __init__(self, xml):
        '''
        create a XML node instance from XML string or lxml.etree Element
        '''
        if isinstance(xml, basestring):
            self.root = etree.fromstring(xml)
        else: # it's an etree Element
            self.root = xml

    def find(self, sel):
        '''
        find node using CSS selector string
        '''
        return Chain([ XQuery(i) for i in CSSSelector(sel)(self.root) ])

    @staticmethod
    def is_etree_node_eq(left, right):
        if left.tag != right.tag:
            return False

        left_len = len(left)
        if left_len != len(right):
            return False

        if left_len == 0:
            ret = left.text == right.text
            if not ret and left.text in (None, '') and \
                right.text in (None, ''):
                ret = True
            return ret

        rchildren = list(right)
        for i, child in enumerate(list(left)):
            if not XQuery.is_etree_node_eq(child, rchildren[i]):
                return False
        return True

    def __eq__(self, right):
        if isinstance(right, Chain):
            if len(right) != 1:
                return False
            right = right[0]
        return XQuery.is_etree_node_eq(self.root, right.root)

    def dumps(self):
        return etree.tostring(self.root)
    
    def inner_dumps(self):
        return ''.join([ etree.tostring(child) for child in self.root ])

    def clone(self):
        return self.__class__(self.dumps())

    def remove(self, sel):
        '''
        remove elements that match CSS selector string
        return the elements deleted
        '''
        backup = []
        for i in self.find(sel):
            backup.append(i)
            i.root.getparent().remove(i.root)
        return Chain(backup)

    def append(self, xquery_node):
        self.root.append(xquery_node.clone().root)
        return self

    #FIXME: text is a property of etree Element
    # we should support this syntax: element.text = 'xxx'
    # now we can only call with element.text('xxx')
    def text(self, value=None):
        if value is None:
            txt = self.root.text
            return '' if txt is None else txt

        if value == '':
            self.clear()
        else:
            self.root.text = value
        return self
    
    def clear(self):
        return self.root.clear()


class ChainMetaClass(type):

    def __new__(mcs, name, bases, attrs):
        def make_wrapper(api):
            def wrapper(self, *args, **kw):
                if len(self) == 1:
                    return getattr(self[0], api)(*args, **kw)
                return Chain([ getattr(x, api)(*args, **kw) for x in self ])
            return wrapper

        attrs.update([(api, make_wrapper(api)) for api in ('dumps',
            'append', 'text', 'clone', 'clear', 'inner_dumps')])

        return type.__new__(mcs, name, bases, attrs)


class Chain(list):

    __metaclass__ = ChainMetaClass

    def find(self, *args, **kw):
        if len(self) == 1:
            return self[0].find(*args, **kw)
        return Chain(itertools.chain(*[ x.find(*args, **kw) for x in self ]))
