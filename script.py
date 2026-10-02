import feedparser
import requests
import time
import os
import sys
from datetime import datetime, timedelta

# --- CONFIGURATION ---

# Méthode 1 : Variables d'environnement (Recommandé pour GitHub)
# Si ces variables ne sont pas définies, le script utilise les valeurs par défaut
PUSHBULLET_KEY = os.environ.get('PUSHBULLET_KEY', 'o.UlyBqVIMmt3xLOvaBj7hAlZ1MTHfF0Kb')
QUERY = os.environ.get('QUERY', 'Paul Vaillant Couturier Villejuif')

# URL du flux RSS Google News
RSS_URL = f"https://news.google.com/rss/search?q={QUERY.replace(' ', '+')}&hl=fr&gl=FR&ceid=FR:fr"

# Fichier pour mémoriser les articles déjà envoyés (Anti-doublon)
ARTICLES_SEEN_FILE = 'articles_seen.txt'

def load_seen_articles():
    try:
        with open(ARTICLES_SEEN_FILE, 'r') as f:
            return set(f.read().splitlines())
    except FileNotFoundError:
        return set()

def save_seen_articles(articles):
    with open(ARTICLES_SEEN_FILE, 'w') as f:
        f.write('\n'.join(articles))

def send_notification(title, link, key):
    msg = {
        "type": "link",
        "title": "📰 Nouvel article",
        "body": title,
        "url": link
    }
    try:
        response = requests.post(
            "https://api.pushbullet.com/v2/pushes",
            auth=(key, ""),
            json=msg
        )
        if response.status_code == 200:
            print(f"✅ Envoyé : {title}")
        else:
            print(f"❌ Erreur Pushbullet : {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur d'envoi : {e}")

def main():
    # Chargement des articles déjà traités
    seen = load_seen_articles()
    
    print(f"🔍 Recherche : {QUERY}")
    feed = feedparser.parse(RSS_URL)
    now = datetime.now()
    limit_time = now - timedelta(hours=24)
    
    count = 0
    for entry in feed.entries:
        try:
            published_dt = datetime(*entry.published_parsed[:6])
            
            # Vérification : Moins de 24h ET Nouveau
            if published_dt > limit_time and entry.link not in seen:
                send_notification(entry.title, entry.link, PUSHBULLET_KEY)
                seen.add(entry.link)
                count += 1
        except Exception as e:
            print(f"⚠️ Erreur de lecture article : {e}")
    
    # Sauvegarde de la liste mise à jour
    save_seen_articles(seen)
    print(f"🏁 Vérification terminée. {count} nouvel(s) article(s).")

if __name__ == "__main__":
    main()
