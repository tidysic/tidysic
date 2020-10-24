from unittest import TestCase

#######################################################
# See https://docs.python.org/3/library/unittest.html # 
#######################################################

class ExampleTest(TestCase):

    def test_example(self):
        self.assertEqual('foo'.upper(), 'FOO')
