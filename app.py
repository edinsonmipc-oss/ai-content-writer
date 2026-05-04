     1|import os
     2|import json
     3|import uuid
     4|from flask import Flask, request, jsonify, render_template
     5|import stripe
     6|import urllib.request
     7|import urllib.parse
     8|
     9|app = Flask(__name__)
    10|
    11|stripe.api_key = os.environ.get('STRIPE_SECRET_KEY', '')
    12|STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY', '')
    13|
    14|FREE_GENERATIONS = 3
    15|users = {}
    16|
    17|def generate_content(topic, content_type, tone, language):
    18|    prompt_map = {
    19|        'blog': 'Write a professional blog post about: ' + topic + '. Tone: ' + tone + '. Language: ' + language + '. Format with headings and paragraphs.',
    20|        'linkedin': 'Write a LinkedIn post about: ' + topic + '. Tone: ' + tone + '. Language: ' + language + '. Professional, engaging, with hashtags.',
    21|        'product': 'Write a product description for: ' + topic + '. Tone: ' + tone + '. Language: ' + language + '. Include features, benefits, specifications.',
    22|        'email': 'Write a marketing email about: ' + topic + '. Tone: ' + tone + '. Language: ' + language + '. Include subject line, body, CTA.',
    23|        'social': 'Write a social media caption for: ' + topic + '. Tone: ' + tone + '. Language: ' + language + '. Short, engaging, with emojis.'
    24|    }
    25|    
    26|    prompt = prompt_map.get(content_type, prompt_map['blog'])
    27|    
    28|    # Try OpenRouter free model
    29|    api_key = os.environ.get('OPENROUTER_API_KEY', '')
    30|    if api_key:
    31|        try:
    32|            data = json.dumps({
    33|                "model": "meta-llama/llama-3.2-3b-instruct:free",
    34|                "messages": [{"role": "user", "content": prompt}],
    35|                "max_tokens": 1000
    36|            }).encode()
    37|            req = urllib.request.Request(
    38|                "https://openrouter.ai/api/v1/chat/completions",
    39|                data=data,
    40|                headers={
    41|                    "Authorization": "Bearer " + api_key,
    42|                    "Content-Type": "application/json",
    43|                    "HTTP-Referer": "https://aicontentwriter.pro"
    44|                }
    45|            )
    46|            with urllib.request.urlopen(req, timeout=30) as resp:
    47|                result = json.loads(resp.read())
    48|                return result['choices'][0]['message']['content']
    49|        except Exception as e:
    50|            return "AI generation unavailable: " + str(e) + "\n\nHere's a template for your content about: " + topic
    51|    
    52|    return "Topic: " + topic + "\n\nThis is a professional " + content_type + " about " + topic + " generated in " + tone + " tone in " + language + ".\n\nContact us to unlock full AI-powered content generation with multiple templates."
    53|
    54|@app.route('/')
    55|def index():
    56|    return render_template('index.html', stripe_key=STRIPE_PUBLISHABLE_KEY)
    57|
    58|@app.route('/generate', methods=['POST'])
    59|def generate():
    60|    data = request.json
    61|    topic = data.get('topic', '')
    62|    content_type = data.get('type', 'blog')
    63|    tone = data.get('tone', 'professional')
    64|    language = data.get('language', 'English')
    65|    session_id = request.cookies.get('session_id', 'anon')
    66|    
    67|    if session_id not in users:
    68|        users[session_id] = {'generations': 0}
    69|    
    70|    if users[session_id]['generations'] >= FREE_GENERATIONS:
    71|        return jsonify({'error': 'Free limit reached. Please subscribe.', 'requires_payment': True}), 402
    72|    
    73|    content = generate_content(topic, content_type, tone, language)
    74|    users[session_id]['generations'] += 1
    75|    
    76|    return jsonify({
    77|        'success': True,
    78|        'content': content,
    79|        'generations_remaining': FREE_GENERATIONS - users[session_id]['generations'],
    80|        'word_count': len(content.split())
    81|    })
    82|
    83|@app.route('/create-checkout', methods=['POST'])
    84|def create_checkout():
    85|    try:
    86|        session = stripe.checkout.Session.create(
    87|            payment_method_types=['card'],
    88|            line_items=[{
    89|                'price_data': {
    90|                    'currency': 'aud',
    91|                    'product_data': {'name': 'AI Content Writer Pro - Monthly'},
    92|                    'unit_amount': 999,
    93|                    'recurring': {'interval': 'month'},
    94|                },
    95|                'quantity': 1,
    96|            }],
    97|            mode='subscription',
    98|            success_url=request.host_url,
    99|            cancel_url=request.host_url,
   100|        )
   101|        return jsonify({'url': session.url})
   102|    except Exception as e:
   103|        return jsonify({'error': str(e)}), 400
   104|
   105|if __name__ == '__main__':
   106|    port = int(os.environ.get('PORT', 5001))
   107|    app.run(host='0.0.0.0', port=port)
   108|