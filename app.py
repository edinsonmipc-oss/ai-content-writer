import os
import json
import uuid
import requests
from datetime import datetime
from flask import Flask, request, jsonify, render_template
import stripe

app = Flask(__name__)
app.secret_key = os.urandom(24).hex()

# Stripe config from env vars
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY', '')
STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY', '')

# OpenRouter config (free models available)
OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY', '')
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

CONTENT_TYPES = {
    "blog_post": {
        "label": "Blog Post",
        "prompt": "Write a comprehensive, SEO-optimized blog post about: {topic}. Include an engaging title, introduction, 3-5 subheadings with detailed paragraphs, a conclusion, and meta description. Use professional tone, 800-1200 words.",
        "price": 199  # $1.99 in cents
    },
    "linkedin": {
        "label": "LinkedIn Post",
        "prompt": "Write a professional LinkedIn post about: {topic}. Make it engaging with a hook, personal insights, 3-4 key points, and a call to action. Include relevant hashtags. 150-300 words.",
        "price": 99  # $0.99
    },
    "product_desc": {
        "label": "Product Description",
        "prompt": "Write a compelling product description for: {topic}. Include features, benefits, specifications, and a persuasive call to action. Use persuasive marketing copy. 200-400 words.",
        "price": 149  # $1.49
    },
    "email": {
        "label": "Email Newsletter",
        "prompt": "Write a professional email newsletter about: {topic}. Include a catchy subject line, greeting, main content with 2-3 key points, and a clear call to action with sign-off. 300-500 words.",
        "price": 149
    },
    "twitter": {
        "label": "Twitter/X Thread",
        "prompt": "Write a Twitter/X thread about: {topic}. Start with a hook tweet, then 5-8 reply tweets with insights. Each tweet under 280 characters. Use line breaks and emojis sparingly.",
        "price": 99
    }
}

def generate_content(topic, content_type):
    """Generate content using OpenRouter with a free model."""
    config = CONTENT_TYPES.get(content_type, CONTENT_TYPES["blog_post"])
    prompt = config["prompt"].format(topic=topic)
    
    if not OPENROUTER_API_KEY:
        # Fallback mock content for demo/testing when no API key
        return generate_mock_content(topic, content_type)
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "openai/gpt-3.5-turbo",  # Free tier available
        "messages": [
            {"role": "system", "content": "You are a professional content writer. Write high-quality, engaging content."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 2000,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=30)
        if response.status_code == 200:
            data = response.json()
            return data["choices"][0]["message"]["content"]
        else:
            return generate_mock_content(topic, content_type)  # Fallback
    except Exception:
        return generate_mock_content(topic, content_type)  # Fallback

def generate_mock_content(topic, content_type):
    """Generate sample content when no API key is configured."""
    config = CONTENT_TYPES.get(content_type, CONTENT_TYPES["blog_post"])
    label = config["label"]
    
    samples = {
        "blog_post": f"""# {topic}: The Ultimate Guide

## Introduction
{topic} has become an increasingly important topic in today's fast-paced digital landscape. Whether you're a seasoned professional or just getting started, understanding the fundamentals is crucial for success.

## Why {topic} Matters
In 2026, the landscape of {topic} continues to evolve at a rapid pace. Businesses and individuals alike are discovering new ways to leverage its power for growth and innovation. The key is to stay informed and adaptable.

## Key Strategies
1. **Research thoroughly** - Understanding your audience and market is the foundation of success
2. **Implement systematically** - Break down your approach into manageable steps
3. **Measure and optimize** - Use data to continuously improve your results

## Best Practices
When working with {topic}, always start with a clear goal in mind. Define what success looks like and work backward from there. This approach ensures every action you take is aligned with your objectives.

## Common Pitfalls to Avoid
Many people make the mistake of trying to do everything at once. Instead, focus on mastering one aspect at a time. Patience and persistence are your greatest assets.

## Conclusion
{topic} offers tremendous opportunities for those willing to put in the work. Start small, stay consistent, and never stop learning.

---

*Meta Description: Discover everything you need to know about {topic}. From fundamentals to advanced strategies, this comprehensive guide covers it all.*""",
        "linkedin": f"""💡 **{topic}: My Top Insights**

After years of experience in this space, here's what I've learned:

1️⃣ **Start with Why** - Before diving into {topic}, understand your purpose. Clarity drives results.

2️⃣ **Focus on Value** - Everything you do should add value to your audience. Quality over quantity, every time.

3️⃣ **Build Relationships** - In the world of {topic}, who you know matters as much as what you know.

4️⃣ **Stay Consistent** - Success doesn't happen overnight. Consistency beats intensity.

5️⃣ **Keep Learning** - The landscape changes fast. Stay curious and keep upgrading your skills.

What's your biggest takeaway from working with {topic}? Share below! 👇

#{topic.replace(' ', '')} #BusinessGrowth #ProfessionalDevelopment #SuccessTips""",
        "product_desc": f"""## {topic}

**Revolutionize Your Workflow with {topic}**

### Overview
{topic} is the solution you've been waiting for. Designed with precision and built for performance, it delivers exceptional results every time.

### Key Features
✨ **Premium Quality** - Crafted with the highest standards in mind
⚡ **Lightning Fast** - Optimized for maximum efficiency
🔒 **Secure & Reliable** - Your safety is our priority
🎯 **User-Friendly** - Intuitive design for seamless experience

### Benefits
- Save hours of manual work each week
- Achieve professional-grade results
- Reduce costs without compromising quality
- Scale your efforts effortlessly

### Specifications
- Format: Digital download
- Instant access upon purchase
- Regular updates included
- Lifetime support

### Why Choose {topic}?
Thousands of satisfied customers trust {topic} for their needs. Join them today and experience the difference.

**Get started now and transform the way you work! 🚀**

[Call to Action: Buy Now — Limited Time Offer]""",
        "email": f"""**Subject:** Your Guide to {topic} — Everything You Need to Know

**Hi there!**

I hope this email finds you well. Today, I want to share something valuable with you — a complete guide to {topic}.

**Why {topic} Matters Now**
The landscape is shifting, and those who understand {topic} will have a significant advantage. Whether you're looking to grow your business, improve your skills, or stay ahead of the curve, this knowledge is essential.

**Here's What You'll Learn:**
✅ The fundamentals of {topic} explained simply
✅ Proven strategies that work in 2026
✅ Common mistakes and how to avoid them
✅ Actionable steps you can take today

**Your Next Step**
Don't let this opportunity pass you by. Start implementing these insights today and see the difference for yourself.

**Ready to dive deeper?** Reply to this email and let me know what specific aspect of {topic} interests you most. I'd love to help!

To your success,
The Content Team

P.S. — Share this with a friend who could benefit from learning about {topic}!""",
        "twitter": f"""🧵 {topic}: A Complete Thread 🧵

1/ This is your sign to learn about {topic}.

2/ Most people overlook {topic}. Big mistake.

Here's why it matters👇

3/ First, {topic} helps you stand out.

In a crowded market, being different = being remembered.

4/ Second, it's a force multiplier.

A small investment in {topic} yields outsized returns.

5/ Third, it's not going away.

Early adopters win. Late adopters play catch-up.

6/ Here's how to get started:

• Pick one aspect to focus on
• Spend 30 min/day learning
• Apply what you learn immediately

7/ The best time to start was yesterday.

The second best time is NOW.

8/ Found this helpful? Retweet the first tweet to help others discover {topic} too!

Follow @yourhandle for more insights daily. 💪"""
    }
    
    return samples.get(content_type, samples["blog_post"])

@app.route('/')
def index():
    return render_template('index.html', 
                         stripe_key=STRIPE_PUBLISHABLE_KEY,
                         content_types=CONTENT_TYPES)

@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    topic = data.get('topic', '').strip()
    content_type = data.get('content_type', 'blog_post')
    
    if not topic:
        return jsonify({"error": "Please enter a topic"}), 400
    
    if content_type not in CONTENT_TYPES:
        return jsonify({"error": "Invalid content type"}), 400
    
    try:
        content = generate_content(topic, content_type)
        return jsonify({
            "success": True,
            "content": content,
            "topic": topic,
            "content_type": CONTENT_TYPES[content_type]["label"]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/create-checkout', methods=['POST'])
def create_checkout():
    try:
        data = request.get_json()
        content_type = data.get('content_type', 'blog_post')
        config = CONTENT_TYPES.get(content_type, CONTENT_TYPES["blog_post"])
        
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'aud',
                    'product_data': {'name': f'AI Content Writer - {config["label"]}'},
                    'unit_amount': config['price'],
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.host_url.rstrip('/') + '?success=1',
            cancel_url=request.host_url.rstrip('/') + '?canceled=1',
        )
        return jsonify({'url': session.url})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/create-subscription', methods=['POST'])
def create_subscription():
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'aud',
                    'product_data': {'name': 'AI Content Writer Pro - Monthly'},
                    'unit_amount': 1499,  # $14.99
                    'recurring': {'interval': 'month'},
                },
                'quantity': 1,
            }],
            mode='subscription',
            success_url=request.host_url.rstrip('/') + '?success=1',
            cancel_url=request.host_url.rstrip('/') + '?canceled=1',
        )
        return jsonify({'url': session.url})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port)
