import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from flask import Blueprint, jsonify, request

translation_bp = Blueprint('translation', __name__)

OPENROUTER_URL = 'https://openrouter.ai/api/v1/chat/completions'
DEFAULT_MODEL = 'nvidia/nemotron-3.5-lightning:free'
PROVIDER_TIMEOUT_SECONDS = 35


def translate_texts(texts, api_key, model):
    system_message = (
        'You are a professional English and Simplified Chinese translator. Translate '
        'the supplied text into the explicitly requested target language. Preserve '
        'meaning, tone, formatting, and proper names. Output only the translation; '
        'do not add a language label, explanation, quotation marks, or the source text.'
    )
    targets = {
        key: (
            'English'
            if any('\u3400' <= character <= '\u9fff' for character in text)
            else 'Simplified Chinese'
        )
        for key, text in texts.items()
    }
    messages = [
        {'role': 'system', 'content': system_message},
    ]
    payload = {
        'model': model,
        'messages': messages,
        'reasoning': {'enabled': False},
    }
    if len(texts) == 1:
        key, text = next(iter(texts.items()))
        messages.append({
            'role': 'user',
            'content': (
                'Translate this text into {}. Return only the translated text.\n\n{}'
            ).format(targets[key], text),
        })
    else:
        prompt_data = {
            key: {'text': text, 'target_language': targets[key]}
            for key, text in texts.items()
        }
        messages.append({
            'role': 'user',
            'content': (
                'Translate each text into its target_language. Return only a JSON '
                'object with the original keys and translated string values; no '
                'additional keys or explanation.\n{}'
            ).format(json.dumps(prompt_data, ensure_ascii=False)),
        })

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
    with urlopen(req, timeout=PROVIDER_TIMEOUT_SECONDS) as response:
        provider_response = json.loads(response.read().decode('utf-8'))

    content = provider_response['choices'][0]['message']['content']
    if not isinstance(content, str) or not content.strip():
        raise ValueError('Translation provider returned empty content')
    if len(texts) == 1:
        return {next(iter(texts)): content.strip()}

    try:
        translated = json.loads(content)
    except json.JSONDecodeError:
        decoder = json.JSONDecoder()
        translated = None
        for index, character in enumerate(content):
            if character == '{':
                try:
                    translated, _ = decoder.raw_decode(content[index:])
                    break
                except json.JSONDecodeError:
                    continue

    if not isinstance(translated, dict):
        raise ValueError('Translation provider returned an invalid translation object')

    result = {}
    for key in texts:
        value = translated.get(key)
        if isinstance(value, dict):
            value = value.get('text')
        if not isinstance(value, str) or not value.strip():
            raise ValueError('Translation provider omitted a translated field')
        result[key] = value.strip()
    return result


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
