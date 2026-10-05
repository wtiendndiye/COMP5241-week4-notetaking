import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from flask import Blueprint, jsonify, request

translation_bp = Blueprint('translation', __name__)

OPENROUTER_URL = 'https://openrouter.ai/api/v1/chat/completions'
DEFAULT_MODEL = 'nvidia/nemotron-3.5-lightning:free'


def translate_texts(texts, api_key, model):
    system_message = (
        'You are a professional translator. Detect whether each input is English or '
        'Simplified Chinese and translate it into the other language. Preserve the '
        'meaning, tone, formatting, and proper names. Return only the translation. '
        'For a JSON object input, return a JSON object with the same keys and only '
        'the translated values.'
    )
    prompt = json.dumps(texts, ensure_ascii=False) if len(texts) > 1 else next(iter(texts.values()))
    messages = [
        {'role': 'system', 'content': system_message},
        {'role': 'user', 'content': prompt},
    ]
    payload = {
        'model': model,
        'messages': messages,
        'reasoning': {'enabled': True},
    }
    if len(texts) > 1:
        messages[1]['content'] = (
            'Translate each value in this JSON object and return a JSON object '
            'with the same keys:\n' + prompt
        )

    req = Request(
        OPENROUTER_URL,
        data=json.dumps(payload).encode('utf-8'),
        headers={
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'HTTP-Referer': 'http://localhost:5001',
            'X-Title': 'NoteTaker',
        },
        method='POST',
    )
    with urlopen(req, timeout=45) as response:
        provider_response = json.loads(response.read().decode('utf-8'))

    content = provider_response['choices'][0]['message']['content']
    if not isinstance(content, str) or not content.strip():
        raise ValueError('Translation provider returned empty content')
    if len(texts) == 1:
        return {next(iter(texts)): content.strip()}

    translated = json.loads(content)
    if not isinstance(translated, dict) or any(
        key not in translated or not isinstance(translated[key], str)
        for key in texts
    ):
        raise ValueError('Translation provider returned an invalid translation object')
    return {key: translated[key] for key in texts}


@translation_bp.route('/translate', methods=['POST'])
def translate():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({'error': 'A JSON request body is required'}), 400

    field = data.get('field')
    if field not in ('title', 'content', 'all'):
        return jsonify({'error': 'Field must be title, content, or all'}), 400

    fields = ('title', 'content') if field == 'all' else (field,)
    if any(key in data and not isinstance(data[key], str) for key in fields):
        return jsonify({'error': 'Title and content must be strings'}), 400

    texts = {
        key: data.get(key, '').strip()
        for key in fields
        if data.get(key, '').strip()
    }
    if not texts:
        return jsonify({'error': 'Enter text to translate'}), 400

    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        return jsonify({
            'error': 'Translation is not configured. Set the OPENROUTER_API_KEY environment variable.'
        }), 503

    model = os.getenv('OPENROUTER_MODEL', DEFAULT_MODEL)
    try:
        return jsonify(translate_texts(texts, api_key, model))
    except HTTPError as error:
        if error.code == 402:
            return jsonify({
                'error': (
                    'OpenRouter returned HTTP 402 (Payment Required). Check your '
                    'account credits, billing status, and spending limits. The '
                    'selected model may require paid credits.'
                )
            }), 502
        return jsonify({
            'error': f'Translation provider returned HTTP {error.code}. Check your OpenRouter API key and model access.'
        }), 502
    except URLError as error:
        return jsonify({
            'error': f'Could not connect to the translation provider: {error.reason}'
        }), 502
    except TimeoutError:
        return jsonify({'error': 'The translation provider timed out. Please try again.'}), 504
    except (KeyError, IndexError, TypeError, UnicodeDecodeError, json.JSONDecodeError, ValueError):
        return jsonify({'error': 'The translation provider returned an invalid response.'}), 502
