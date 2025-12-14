import os
import sys
from dotenv import load_dotenv
from utils import RuBERTAnalyzer, RuBERTTinyAnalyzer, SentimentAnalysisException

load_dotenv()

def test_analyzer(analyzer, name, test_text):
    try:
        result = analyzer.analyze(test_text)
        print(f"\n{name}: {result['sentiment']} ({result['confidence']:.1%})")
        return True
    except SentimentAnalysisException as e:
        print(f"\n{name}: Ошибка - {str(e)}")
        return False
    except Exception as e:
        print(f"\n{name}: Ошибка - {str(e)}")
        return False

def main():
    test_text = "Это замечательный продукт! Я очень доволен."
    huggingface_key = os.environ.get('HUGGINGFACE_API_KEY', '')
    
    if not huggingface_key:
        print("HUGGINGFACE_API_KEY не установлен")
    
    results = []
    for analyzer_class, name in [(RuBERTAnalyzer, "RuBERT"), 
                                 (RuBERTTinyAnalyzer, "RuBERT Tiny")]:
        try:
            analyzer = analyzer_class(huggingface_key)
            results.append(test_analyzer(analyzer, name, test_text))
        except Exception as e:
            print(f"\n{name}: Ошибка создания - {e}")
    
    success = sum(results)
    print(f"\nРезультат: {success}/{len(results)}")
    return 0 if success == len(results) else 1

if __name__ == '__main__':
    sys.exit(main())

