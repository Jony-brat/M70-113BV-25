import unittest
from unittest.mock import patch
from io import StringIO


class TestMain(unittest.TestCase):
    
    def test_main_function_calls_run(self):
           with patch('src.db.__main__.run') as mock_run:
            from src.db.__main__ import main
            main()
            mock_run.assert_called_once()
    
    def test_main_executes_when_script(self):
        with patch('src.db.__main__.main') as mock_main:
            
            import src.db.__main__ as main_module
            original_name = main_module.__name__
            
            try:
               
                main_module.__name__ = '__main__'
                
             
                with patch('sys.stdout', new_callable=StringIO):
                    import importlib
                    importlib.reload(main_module)
                
                mock_main.assert_called_once()
            finally:
              
                main_module.__name__ = original_name


if __name__ == "__main__":
    unittest.main()