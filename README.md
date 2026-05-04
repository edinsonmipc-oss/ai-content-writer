# AI Content Writer ✍️

Generate professional content with AI — blog posts, LinkedIn content, product descriptions, emails, and Twitter threads.

## Features
- **5 Content Types**: Blog posts, LinkedIn posts, product descriptions, email newsletters, Twitter/X threads
- **AI-Powered**: Uses OpenRouter API (GPT-3.5-turbo, free tier available)
- **Mock Fallback**: Works without an API key for demo/testing
- **Stripe Payments**: Pay per piece or subscribe monthly

## Content Types & Pricing
| Type | Price |
|------|-------|
| Blog Post | $1.99 |
| LinkedIn Post | $0.99 |
| Product Description | $1.49 |
| Email Newsletter | $1.49 |
| Twitter Thread | $0.99 |
| Pro Unlimited | $14.99/mo |

## Setup
```bash
pip install -r requirements.txt
export STRIPE_PUBLISHABLE_KEY=pk_test_...
export STRIPE_SECRET_KEY=sk_test_...
export OPENROUTER_API_KEY=your_key  # Optional, works without it
gunicorn app:app
```

## Stack
- Flask (Python)
- OpenRouter API
- Stripe Checkout
- Responsive HTML/CSS
