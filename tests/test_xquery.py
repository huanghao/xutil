import unittest

from lxml import etree

from xutil.xquery import XQuery


class ChainTest(unittest.TestCase):

    def test_text(self):
        x = XQuery('<R><a>1</a><a><c>4</c></a><b>3</b></R>')

        self.assertEquals('4', x.find('c').text())

    def test_text_multi(self):
        x = XQuery('<R><a>1</a><a>2</a><b>3</b></R>')

        self.assertEquals(['1', '2'],x.find('a').text())

    def test_empty_text(self):
        x = XQuery('<R><a>1</a><a><c>4</c></a><b>3</b></R>')

        self.assertEquals([], x.find('d').text())

    def test_find(self):
        x = XQuery('<R><a>1</a><a>2</a><b>3</b></R>')
        y = x.find('R').find('a').text()

        self.assertEquals(['1','2'], y)

    def test_find_multi(self):
        x = XQuery('<R><a><c>4</c></a><a>2</a><b>3</b></R>')
        y = x.find('a').find('c').text()

        self.assertEquals('4', y)

    def test_find_empty(self):
        x = XQuery('<R><a>1</a><a>2</a><b>3</b></R>')

        self.assertEquals([], x.find('c'))

    def test_append(self):
        x = XQuery('<R><a>1</a><a>2</a><b>3</b></R>')
        y = XQuery('<R><a>1<c/></a><a>2<c/></a><b>3</b></R>')
        x.find('a').append(XQuery('<c/>'))

        self.assertEquals(y, x)

    def test_append_multi(self):
        x = XQuery('<R><a>1</a><a>2</a><b>3</b></R>')
        y = XQuery('<R><a>1<c><d>6</d></c></a><a>2<c><d>6</d></c></a><b>3</b></R>')
        z = XQuery('<c><d>6</d></c>')
        x.find('a').append(z)

        self.assertEquals(y, x)

    def test_empty_append(self):
        x = XQuery('<R><a>1</a><a>2</a><b>3</b></R>')
        x.find('c').append(XQuery('<d/>'))

        self.assertEquals(XQuery('<R><a>1</a><a>2</a><b>3</b></R>'),
                          x)

    def test_chain(self):
        x = XQuery('<R><a>1</a><a>2</a><b>3</b></R>')
        x.find('a').append(XQuery('<c/>')).find('c').text("4")

        self.assertEquals(XQuery('<R><a>1<c>4</c></a><a>2<c>4</c></a><b>3</b></R>'),
                          x)

    def test_xquery_object_equals_chain(self):
        self.assertEquals(XQuery('<a/>'),
                          XQuery('<R><a/></R>').find('a'))

        self.assertEquals(XQuery('<R><a/></R>').find('a'),
                          XQuery('<a/>'))

    def test_chain_equals_chain(self):
        self.assertEquals(XQuery('<R><a/><a>2</a></R>').find('a'),
                          XQuery('<R><a/><a>2</a></R>').find('a'))

    def test_empty_chain_equals(self):
        self.assertEquals(XQuery('<R></R>').find('a'),
                          XQuery('<R></R>').find('a'))

    def test_one_element_chain(self):
        self.assertEquals(XQuery('<R><a/></R>').find('a'),
                          XQuery('<R><a/></R>').find('a'))

    def test_chain_not_equals(self):
        self.assertNotEquals(XQuery('<R><a/></R>').find('a'),
                             XQuery('<R><a/><a/></R>').find('a'))


class XQueryTest(unittest.TestCase):

    def test_find(self):
        x = XQuery('''<R><a>1</a><b>2</b></R>''')

        self.assertEquals(XQuery('<a>1</a>'),
                          x.find('a'))

    def test_find_complex(self):
        a = '''<a><b>1</b><c>2</c></a>'''
        xml = '''<R>%s<d>3</d></R>''' % a

        self.assertEquals(XQuery(a),
                          XQuery(xml).find('a'))

    def test_find_not_exists(self):
        x = XQuery('<R/>')

        self.assertEquals([], x.find('a'))

    def test_clone(self):
        x = XQuery('<R/>')
        y = x.clone()

        self.assertTrue(x == y and id(x) != id(y))

    def test_remove_child(self):
        x = XQuery('''<R><a>1</a><b><c>3</c></b></R>''')

        self.assertEquals(XQuery('<b><c>3</c></b>'),
                          x.remove('b'))
        self.assertEquals(XQuery('<R><a>1</a></R>'),
                          x)

    def test_remove_desendent(self):
        x = XQuery('''<R><a>1</a><b><c>3</c></b></R>''')

        self.assertEquals(XQuery('<c>3</c>'),
                          x.remove('c'))
        self.assertEquals(XQuery('<R><a>1</a><b></b></R>'),
                          x)

    def test_remove_multi(self):
        x = XQuery('''<R><a>1</a><b><c>3</c></b><c>4</c></R>''')

        self.assertEquals(2, len(x.remove('c')))
        self.assertEquals(XQuery('<R><a>1</a><b></b></R>'),
                          x)

    def test_remove_nothing(self):
        x = XQuery('<R><a>1</a><b><c>3</c></b></R>')

        x.remove('d')
        self.assertEquals(XQuery('<R><a>1</a><b><c>3</c></b></R>'),
                          x)

    def test_append(self):
        x = XQuery('<R><a>1</a></R>')

        self.assertEquals(XQuery('<R><a>1</a><b>2</b></R>'),
                          x.append(XQuery('<b>2</b>')))

    def test_append_multi(self):
        x = XQuery('<R><a/><c><a/></c></R>')
        x.find('a').append(XQuery('<b/>'))

        self.assertEquals(XQuery('<R><a><b/></a><c><a><b/></a></c></R>'),
                          x)

    def test_eq(self):
        self.assertEquals(XQuery('<a/>'),
                          XQuery('<a></a>'))

    def test_eq_with_return(self):
        self.assertEquals(XQuery('''<a>
<b>1</b>
<c></c>
</a>'''),
                          XQuery('<a><b>1</b><c/></a>'))


    def test_eq_cdata(self):
        x = XQuery('<a>&lt;root&gt;&lt;a&gt;1&lt;/a&gt;&lt;/root&gt;</a>')
        y = XQuery('<a><![CDATA[<root><a>1</a></root>]]></a>')
        self.assertEquals(x, y)

    def test_eq_cdata2(self):
        a = etree.Element('root')
        a.text = '<root><a>1</a></root>'

        b = etree.Element('root')
        b.text = etree.CDATA('<root><a>1</a></root>')

        self.assertTrue(XQuery.is_etree_node_eq(a, b))

    def test_text(self):
        self.assertEquals('1234',
                          XQuery('<a>1234</a>').text())

    def test_text_of_node_with_children(self):
        self.assertEquals('',
                          XQuery('<a><b/></a>').text())

    def test_text_empty(self):
        self.assertEquals('',
                          XQuery('<a/>').text())

    def test_text_modification(self):
        self.assertEquals(XQuery('<a>1</a>'),
                          XQuery('<a/>').text('1'))

    def test_text_clear(self):
        self.assertEquals(XQuery('<a></a>'),
                          XQuery('<a>1</a>').text(''))

    def test_modfity_text_of_node_that_is_not_exists(self):
        x = XQuery('<a>1</a>')
        x.find('b').text('2')

        self.assertEquals(XQuery('<a>1</a>'),
                          x)


if __name__ == '__main__':
    unittest.main()
