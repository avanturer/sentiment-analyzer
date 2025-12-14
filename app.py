from flask import Flask, render_template, request, jsonify
from config import Config, DevelopmentConfig
from utils import (
    RuBERTAnalyzer, 
    RuBERTTinyAnalyzer, 
    SentimentComparator,
    SentimentAnalysisException
)
import os
import logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

env = os.environ.get('FLASK_ENV', 'development')
if env == 'production':
    app.config.from_object(Config)
else:
    app.config.from_object(DevelopmentConfig)

huggingface_key = app.config.get('HUGGINGFACE_API_KEY', '')

app.logger.info('Используются две разные Hugging Face модели для анализа тональности: RuBERT и RuBERT Tiny')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({'error': 'Пожалуйста, введите текст для анализа'}), 400
        
        if len(text) > 5000:
            return jsonify({'error': 'Текст не должен превышать 5000 символов'}), 400
        
        results = []
        errors = []
        
        for analyzer_class, name in [(RuBERTAnalyzer, "Hugging Face (RuBERT)"), 
                                     (RuBERTTinyAnalyzer, "Hugging Face (RuBERT Tiny)")]:
            try:
                analyzer = analyzer_class(huggingface_key)
                results.append(analyzer.analyze(text))
            except SentimentAnalysisException as e:
                errors.append(str(e))
                logger.warning(f"{name}: {str(e)}")
            except Exception as e:
                errors.append(f"{name}: Ошибка при выполнении запроса")
                logger.error(f"{name}: {str(e)}")
        
        if not results:
            return jsonify({
                'error': 'Не удалось выполнить анализ ни одного сервиса',
                'details': errors
            }), 500
        
        comparison = SentimentComparator.compare_results(results)
        
        response = {
            'individual_results': results,
            'comparison': comparison,
            'input_text': text[:100] + '...' if len(text) > 100 else text,
            'analysis_timestamp': datetime.now().isoformat()
        }
        if errors:
            response['partial_errors'] = errors
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Unexpected error in /api/analyze: {str(e)}")
        return jsonify({'error': 'Внутренняя ошибка сервера'}), 500


@app.route('/api/demo', methods=['GET'])
def demo():
    demo_texts = [
        "Это невероятно замечательный продукт! Я очень доволен покупкой.",
        "Ужасное качество. Совершенно разочарован товаром.",
        "Продукт нормальный, ничего особенного.",
        "Не могу поверить, как хорошо это работает!",
        "Не рекомендую. Деньги выброшены на ветер."
    ]
    return jsonify({'demo_samples': demo_texts})


@app.route('/api/status', methods=['GET'])
def status():
    return jsonify({
        'status': 'running',
        'services': {
            'huggingface_rubert': {
                'available': True,
                'name': 'Hugging Face (RuBERT)',
                'requires_key': True,
                'model': 'blanchefort/rubert-base-cased-sentiment'
            },
            'huggingface_rubert_tiny': {
                'available': True,
                'name': 'Hugging Face (RuBERT Tiny)',
                'requires_key': True,
                'model': 'cointegrated/rubert-tiny-sentiment-balanced'
            }
        },
        'version': '1.0.0',
        'note': 'Требуется бесплатный API ключ от Hugging Face'
    })


@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Страница не найдена'}), 404

@app.errorhandler(500)
def internal_error(e):
    logger.error(f"Ошибка сервера: {str(e)}")
    return jsonify({'error': 'Внутренняя ошибка сервера'}), 500


if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'], host='0.0.0.0', port=5000)
