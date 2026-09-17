"""
AI Hashtag Generator - Flask Backend
Micro-SaaS for Instagram & YouTube Creators
"""
import os
import json
import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory, g

app = Flask(__name__, static_folder='.')
DATABASE = os.environ.get(
    'DATABASE_PATH',
    '/var/www/hashtag-tool/analytics.db' if os.path.exists('/var/www/hashtag-tool') else os.path.join(os.path.dirname(__file__), 'analytics.db')
)

# ─── Hashtag Generation Logic ────────────────────────────────────────────────

HASHTAG_SEEDS = {
    "fitness": ["fitness", "gym", "workout", "fitfam", "fitnessmotivation", "health", "fit", "training", "bodybuilding", "fitnessjourney", "gymlife", "strength", "cardio", "nutrition", "healthylifestyle", "muscle", "fitnessmodel", "gymmotivation", "fitlife", "weightloss", "fitnessgoals", "personaltrainer", "fitnessaddict", "gymrat", "crossfit", "yoga", "fitnessinspo", "workoutmotivation", "fitspiration", "healthylife"],
    "food": ["foodie", "foodporn", "food", "cooking", "recipe", "foodphotography", "yummy", "delicious", "homemade", "foodblogger", "foodstagram", "instafood", "chef", "baking", "tasty", "dinner", "lunch", "breakfast", "healthyfood", "foodlover", "eeeeats", "forkyeah", "foodgasm", "buzzfeast", "dailyfoodfeed", "food Gram", "recipeshare", "homecook", "eatclean", "fooddiary"],
    "travel": ["travel", "travelgram", "wanderlust", "travelphotography", "travelblogger", "explore", "vacation", "adventure", "instatravel", "traveling", "travelling", "holiday", "trip", "traveladdict", "traveltheworld", "traveler", "tourism", "passport", "wanderer", "traveldiaries", "travelholic", "travelingram", "globetrotter", "travelbugs", "instavacation", "travelphotographer", "exploremore", "travelmoment", "getaway"],
    "fashion": ["fashion", "style", "ootd", "fashionblogger", "instafashion", "outfit", "fashionista", "styleinspo", "streetstyle", "fashionstyle", "stylish", "lookbook", "whatiwore", "fashionable", "outfitoftheday", "fashiondiaries", "styleblogger", "fashionaddict", "fashiondaily", "instastyle", "fashionlover", "fashionweek", "outfitinspiration", "fashionlife", "styleicon", "fashionforward", "dailyfashion", "fashiongram", "trendy"],
    "tech": ["tech", "technology", "coding", "programming", "developer", "software", "webdev", "python", "javascript", "startup", "innovation", "ai", "machinelearning", "datascience", "techie", "devlife", "programminglife", "coder", "techcommunity", "code", "developerlife", "webdeveloper", "appdevelopment", "technews", "gadgets", "techlover", "digital", "cybersecurity", "cloudcomputing"],
    "beauty": ["beauty", "makeup", "skincare", "beautyblogger", "mua", "makeupartist", "beautytips", "hairstyle", "hair", "cosmetics", "beautygram", "makeuplover", "skincareroutine", "beautycommunity", "glowup", "naturalbeauty", "beautyproducts", "makeuptutorial", "skincareaddict", "beautyhacks", "lipstick", "eyemakeup", "nailart", "beautyreview", "beautycare", "selfcare", "pamper", "beautyqueen", "flawless"],
    "gaming": ["gaming", "gamer", "videogames", "twitch", "streamer", "gamelife", "ps5", "xbox", "pcgaming", "nintendo", "gamingcommunity", "gamers", "gamingmemes", "esports", "gameplay", "gaminglife", "fortnite", "minecraft", "gamingsetup", "playstation", "gamerlife", "twitchstreamer", "game", "gamedev", "indiegame", "mobilegaming", "gamingfun", "levelup", "gg"],
    "photography": ["photography", "photo", "photographer", "photooftheday", "portrait", "landscape", "canon", "nikon", "photoart", "photographylovers", "streetphotography", "naturephotography", "portraitphotography", "photoshoot", "photographydaily", "visualsoflife", "photographyaddict", "artistic", "capture", "shotoniphone", "lightroom", "photographytips", "moodygrams", "visualambassadors", "agameoftones", "creativephotography", "photoideas", "picoftheday"],
    "business": ["business", "entrepreneur", "startup", "success", "motivation", "marketing", "businessowner", "smallbusiness", "entrepreneurship", "businessmindset", "hustle", "ceo", "networking", "branding", "leadership", "businessgrowth", "sales", "investing", "wealth", "money", "passiveincome", "sidehustle", "businesstips", "entrepreneurlife", "mindset", "goals", "businessstrategy", "successmindset", "workfromhome"],
    "lifestyle": ["lifestyle", "lifestyleblogger", "daily", "life", "instadaily", "love", "happy", "inspiration", "motivation", "positivevibes", "selfcare", "wellness", "mindfulness", "selflove", "growth", "goals", "dailyinspiration", "positivethinking", "livewell", "goodvibes", "lifestyle", "healthymind", "lifestylecoach", "balance", "peace", "joy", "lifestyle", "bestlife", "vibes", "goodlife"],
}

def generate_hashtags(niche, count=30):
    """Generate hashtags based on niche input."""
    niche_lower = niche.lower().strip()
    
    # Direct match
    if niche_lower in HASHTAG_SEEDS:
        base = HASHTAG_SEEDS[niche_lower]
        extra = [f"{niche_lower}life", f"{niche_lower}gram", f"{niche_lower}community", f"{niche_lower}lover", f"{niche_lower}goals", f"{niche_lower}daily", f"{niche_lower}style", f"{niche_lower}world", f"{niche_lower}time", f"{niche_lower}posts"]
        hashtags = base + [t for t in extra if t not in base]
    else:
        # Fuzzy generate from keyword
        words = niche_lower.split()
        hashtags = []
        for word in words:
            if word in HASHTAG_SEEDS:
                hashtags.extend(HASHTAG_SEEDS[word][:10])
        if not hashtags:
            # Generic creative hashtags
            base_tags = ["trending", "viral", "explore", "explorepage", "instagood", "photooftheday", "instadaily", "instamood", "trendingnow", "viralpost"]
            niche_part = niche_lower.replace(" ", "").replace("-", "")
            hashtags = [f"{niche_part}"] * 5 + base_tags + [f"{niche_part}content", f"{niche_part}creator", f"{niche_part}life", f"{niche_part}world", f"{niche_part}daily", f"{niche_part}style", f"{niche_part}goals", f"{niche_part}lover", f"{niche_part}community", f"{niche_part}gram", f"{niche_part}time", f"{niche_part}posts", f"{niche_part}content", f"{niche_part}addict", f"{niche_part}inspo", f"{niche_part}motivation", f"{niche_part}inspiration"]
    
    # Dedupe and trim to count
    seen = set()
    result = []
    for h in hashtags:
        if h not in seen:
            seen.add(h)
            result.append(h)
        if len(result) >= count:
            break
    
    # Fill if still short
    while len(result) < count:
        idx = len(result)
        result.append(f"{niche_lower.replace(' ', '')}{idx}")
        if len(result) >= count:
            break
    
    return result[:count]

# ─── Analytics ──────────────────────────────────────────────────────────────

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

def init_db():
    os.makedirs(os.path.dirname(DATABASE), exist_ok=True)
    db = sqlite3.connect(DATABASE)
    db.execute('''CREATE TABLE IF NOT EXISTS analytics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event TEXT NOT NULL,
        niche TEXT,
        hashtag_count INTEGER,
        ip_hash TEXT,
        user_agent TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    db.execute('''CREATE TABLE IF NOT EXISTS page_views (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ip_hash TEXT,
        referrer TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    db.commit()
    db.close()

@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def log_event(event, niche=None, hashtag_count=None):
    try:
        db = get_db()
        ip_hash = hash(request.remote_addr) if request.remote_addr else 'local'
        user_agent = request.headers.get('User-Agent', '')[:200]
        db.execute(
            'INSERT INTO analytics (event, niche, hashtag_count, ip_hash, user_agent) VALUES (?, ?, ?, ?, ?)',
            (event, niche, hashtag_count, str(ip_hash), user_agent)
        )
        db.commit()
    except Exception:
        pass

# ─── Routes ─────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/sales')
def sales():
    sales_path = '/var/www/hashtag-tool-sales/index.html'
    if os.path.exists(sales_path):
        with open(sales_path, 'r', encoding='utf-8') as f:
            return f.read(), 200, {'Content-Type': 'text/html'}
    return "Sales page not found", 404

@app.route('/api/generate', methods=['POST'])
def generate():
    data = request.get_json()
    niche = data.get('niche', '').strip()
    
    if not niche:
        return jsonify({'error': 'Please enter a niche or topic'}), 400
    
    if len(niche) > 100:
        return jsonify({'error': 'Niche is too long'}), 400
    
    hashtags = generate_hashtags(niche)
    log_event('generate', niche=niche, hashtag_count=len(hashtags))
    
    return jsonify({
        'success': True,
        'niche': niche,
        'hashtags': hashtags,
        'count': len(hashtags)
    })

@app.route('/api/analytics', methods=['GET'])
def analytics():
    """Simple analytics - total views and generations."""
    try:
        db = get_db()
        views = db.execute('SELECT COUNT(*) as c FROM page_views').fetchone()['c']
        gens = db.execute("SELECT COUNT(*) as c FROM analytics WHERE event='generate'").fetchone()['c']
        return jsonify({'views': views, 'generations': gens})
    except Exception as e:
        return jsonify({'views': 0, 'generations': 0, 'error': str(e)})

@app.route('/api/track-view', methods=['POST'])
def track_view():
    try:
        db = get_db()
        ip_hash = hash(request.remote_addr) if request.remote_addr else 'local'
        referrer = request.headers.get('Referer', '')[:200]
        db.execute('INSERT INTO page_views (ip_hash, referrer) VALUES (?, ?)', (str(ip_hash), referrer))
        db.commit()
    except Exception:
        pass
    return jsonify({'ok': True})

# Payment placeholder endpoints (Razorpay/Stripe ready)
@app.route('/api/create-checkout-session', methods=['POST'])
def create_checkout():
    """Placeholder for Razorpay/Stripe checkout session creation."""
    return jsonify({
        'url': '#payment-placeholder',
        'message': 'Payment integration ready - connect Razorpay or Stripe keys'
    })

@app.route('/api/webhook', methods=['POST'])
def webhook():
    """Placeholder for payment webhook."""
    return jsonify({'received': True})

# ─── Init ────────────────────────────────────────────────────────────────────

init_db()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
