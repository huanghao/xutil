import unittest
import os
import imp


def load_module(path):
    module_name, _ = os.path.splitext(path)
    return imp.load_source(module_name, path)


def run_tests():
    root = os.path.dirname(os.path.realpath(__file__))

    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    
    for directory, _, files in os.walk(root):
        init = os.path.join(directory, '__init__.py')
        if not os.path.exists(init):
            continue
        
        for fn in files:
            if fn.startswith('test_') and fn.endswith('.py'):
                fname = os.path.join(directory, fn)
                mod = load_module(fname)
                suite.addTest(loader.loadTestsFromModule(mod))

    unittest.TextTestRunner(verbosity=1).run(suite)


if __name__=='__main__':
    run_tests()