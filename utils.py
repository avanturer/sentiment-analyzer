from typing import Dict, List
from datetime import datetime
import logging
from huggingface_hub import InferenceClient

logger = logging.getLogger(__name__)

class SentimentAnalysisException(Exception):
    pass


class RuBERTAnalyzer:
    def __init__(self, api_key: str = None):
        self.service_name = "Hugging Face (RuBERT)"
        self.model_id = "blanchefort/rubert-base-cased-sentiment"
        self.client = InferenceClient(token=api_key) if api_key else InferenceClient()
        
    def analyze(self, text: str) -> Dict:
        if not text or not text.strip():
            raise SentimentAnalysisException("Текст не может быть пустым")
        if len(text) > 5000:
            raise SentimentAnalysisException("Текст слишком длинный (максимум 5000 символов)")
        
        try:
            data = self.client.text_classification(text, model=self.model_id)
            if isinstance(data, list) and data:
                data = data[0]
            
            if isinstance(data, list):
                scores = {}
                for item in data:
                    label = str(item.label if hasattr(item, 'label') else item.get('label', '')).upper()
                    score = float(item.score if hasattr(item, 'score') else item.get('score', 0.0))
                    if 'POSITIVE' in label or 'POS' in label or 'LABEL_2' in label:
                        scores['POSITIVE'] = score
                    elif 'NEGATIVE' in label or 'NEG' in label or 'LABEL_0' in label:
                        scores['NEGATIVE'] = score
                    elif 'NEUTRAL' in label or 'NEU' in label or 'LABEL_1' in label:
                        scores['NEUTRAL'] = score
                sentiment = max(scores, key=scores.get) if scores else 'NEUTRAL'
                score = scores.get(sentiment, 0.5)
            else:
                label = str(data.label if hasattr(data, 'label') else data.get('label', 'NEUTRAL')).upper()
                score = float(data.score if hasattr(data, 'score') else data.get('score', 0.5))
                if 'POSITIVE' in label or 'POS' in label:
                    sentiment = 'POSITIVE'
                elif 'NEGATIVE' in label or 'NEG' in label:
                    sentiment = 'NEGATIVE'
                else:
                    sentiment = 'NEUTRAL'
            
            raw_data = {'label': str(data.label), 'score': float(data.score)} if hasattr(data, '__dict__') else data
            
            return {
                'service': self.service_name,
                'sentiment': sentiment,
                'confidence': min(score, 1.0),
                'raw_response': raw_data,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            error_msg = str(e)
            if "410" in error_msg or "Gone" in error_msg:
                raise SentimentAnalysisException(f"{self.service_name}: API изменился. Обновите библиотеку: pip install --upgrade huggingface_hub")
            elif "401" in error_msg or "Unauthorized" in error_msg or "authentication" in error_msg.lower():
                raise SentimentAnalysisException(f"{self.service_name}: Требуется API ключ. Получите бесплатный токен на https://huggingface.co/settings/tokens")
            elif "404" in error_msg or "not found" in error_msg.lower():
                raise SentimentAnalysisException(f"{self.service_name}: Модель не найдена. Проверьте модель или получите токен на https://huggingface.co/settings/tokens")
            elif "429" in error_msg or "rate limit" in error_msg.lower():
                raise SentimentAnalysisException(f"{self.service_name}: Превышен лимит запросов")
            else:
                raise SentimentAnalysisException(f"{self.service_name}: Ошибка запроса: {error_msg[:200]}")


class RuBERTTinyAnalyzer:
    def __init__(self, api_key: str = None):
        self.service_name = "Hugging Face (RuBERT Tiny)"
        self.model_id = "cointegrated/rubert-tiny-sentiment-balanced"
        self.client = InferenceClient(token=api_key) if api_key else InferenceClient()
        
    def analyze(self, text: str) -> Dict:
        if not text or not text.strip():
            raise SentimentAnalysisException("Текст не может быть пустым")
        if len(text) > 5000:
            raise SentimentAnalysisException("Текст слишком длинный (максимум 5000 символов)")
        
        try:
            data = self.client.text_classification(text, model=self.model_id)
            if isinstance(data, list) and data:
                data = data[0]
            
            if isinstance(data, list):
                scores = {}
                for item in data:
                    label = str(item.label if hasattr(item, 'label') else item.get('label', '')).upper()
                    score = float(item.score if hasattr(item, 'score') else item.get('score', 0.0))
                    if 'POSITIVE' in label or 'POS' in label:
                        scores['POSITIVE'] = score
                    elif 'NEGATIVE' in label or 'NEG' in label:
                        scores['NEGATIVE'] = score
                    else:
                        scores['NEUTRAL'] = 1.0 - max(scores.values()) if scores else 0.5
                sentiment = max(scores, key=scores.get) if scores else 'NEUTRAL'
                score = scores.get(sentiment, 0.5)
            else:
                label = str(data.label if hasattr(data, 'label') else data.get('label', 'NEUTRAL')).upper()
                score = float(data.score if hasattr(data, 'score') else data.get('score', 0.5))
                if 'POSITIVE' in label or 'POS' in label:
                    sentiment = 'POSITIVE'
                elif 'NEGATIVE' in label or 'NEG' in label:
                    sentiment = 'NEGATIVE'
                else:
                    sentiment = 'NEUTRAL'
            
            raw_data = {'label': str(data.label), 'score': float(data.score)} if hasattr(data, '__dict__') else data
            
            return {
                'service': self.service_name,
                'sentiment': sentiment,
                'confidence': min(score, 1.0),
                'raw_response': raw_data,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            error_msg = str(e)
            if "410" in error_msg or "Gone" in error_msg:
                raise SentimentAnalysisException(f"{self.service_name}: API изменился. Обновите библиотеку: pip install --upgrade huggingface_hub")
            elif "401" in error_msg or "Unauthorized" in error_msg or "authentication" in error_msg.lower():
                raise SentimentAnalysisException(f"{self.service_name}: Требуется API ключ. Получите бесплатный токен на https://huggingface.co/settings/tokens")
            elif "404" in error_msg or "not found" in error_msg.lower():
                raise SentimentAnalysisException(f"{self.service_name}: Модель не найдена. Проверьте модель или получите токен на https://huggingface.co/settings/tokens")
            elif "429" in error_msg or "rate limit" in error_msg.lower():
                raise SentimentAnalysisException(f"{self.service_name}: Превышен лимит запросов")
            else:
                raise SentimentAnalysisException(f"{self.service_name}: Ошибка запроса: {error_msg[:200]}")


class SentimentComparator:
    @staticmethod
    def normalize_sentiment(label: str) -> str:
        label = label.upper()
        if label in ['POSITIVE', 'POS', 'GOOD', 'POSITIVE_REVIEW']:
            return 'ПОЛОЖИТЕЛЬНАЯ'
        elif label in ['NEGATIVE', 'NEG', 'BAD', 'NEGATIVE_REVIEW']:
            return 'ОТРИЦАТЕЛЬНАЯ'
        return 'НЕЙТРАЛЬНАЯ'
    
    @staticmethod
    def compare_results(results: List[Dict]) -> Dict:
        if not results:
            return {}
        
        normalized = [{
            'service': r['service'],
            'sentiment': SentimentComparator.normalize_sentiment(r['sentiment']),
            'confidence': r['confidence']
        } for r in results]
        
        sentiments = set(r['sentiment'] for r in normalized)
        agreement_level = 'ВЫСОКОЕ' if len(sentiments) == 1 else 'СРЕДНЕЕ' if len(sentiments) == 2 else 'НИЗКОЕ'
        
        return {
            'results': normalized,
            'agreement_level': agreement_level,
            'average_confidence': round(sum(r['confidence'] for r in normalized) / len(normalized), 3),
            'analysis_timestamp': datetime.now().isoformat()
        }
