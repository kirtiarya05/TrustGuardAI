import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import VotingClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.metrics import accuracy_score, classification_report
import os
import requests
import io
import nltk
from nltk.corpus import stopwords
import re

nltk.download('stopwords')
STOPWORDS = set(stopwords.words('english'))

def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = str(text).lower()
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    text = re.sub(r'<.*?>+', '', text)
    text = re.sub(r'[%s]' % re.escape(r'!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'), '', text)
    text = re.sub(r'\n', '', text)
    text = re.sub(r'\w*\d\w*', '', text)
    text = " ".join([w for w in text.split() if w not in STOPWORDS])
    return text

def download_and_cache(url, filename):
    cache_path = os.path.join('../data', filename)
    if os.path.exists(cache_path):
        print(f"  [CACHED] {filename}")
        try:
            if filename.endswith('.tsv'):
                return pd.read_csv(cache_path, sep='\t', header=None, on_bad_lines='skip')
            return pd.read_csv(cache_path, on_bad_lines='skip')
        except Exception as e:
            print(f"  [ERROR reading cache] {e}")
            return None

    print(f"  [DOWNLOADING] {filename}...")
    try:
        response = requests.get(url, timeout=120, stream=True)
        response.raise_for_status()
        content = response.content
        with open(cache_path, 'wb') as f:
            f.write(content)
        if filename.endswith('.tsv'):
            return pd.read_csv(io.BytesIO(content), sep='\t', header=None, on_bad_lines='skip')
        return pd.read_csv(io.BytesIO(content), on_bad_lines='skip')
    except Exception as e:
        print(f"  [FAILED] {filename}: {e}")
        return None

def add_dataset(all_dfs, df, name, content_col, label_col=None, label_map=None):
    """Helper to normalize and add a dataset."""
    if df is None or len(df) == 0:
        return
    try:
        df = df.copy()
        if label_map:
            df['label'] = df[label_col].map(label_map)
            df = df.dropna(subset=['label'])
            df['label'] = df['label'].astype(int)
        elif label_col:
            df['label'] = df[label_col].astype(int)

        if isinstance(content_col, list):
            df['content'] = df[content_col[0]].fillna('') + ' ' + df[content_col[1]].fillna('')
        else:
            df['content'] = df[content_col].fillna('')

        subset = df[['content', 'label']].copy()
        subset = subset[subset['content'].str.len() > 10]
        all_dfs.append(subset)
        print(f"  [OK] {name}: {len(subset)} records added")
    except Exception as e:
        print(f"  [ERROR] {name}: {e}")

def train():
    all_dfs = []
    data_dir = '../data'
    os.makedirs(data_dir, exist_ok=True)

    print("=" * 60)
    print("  TRUSTGUARD AI — MEGA TRAINING PROTOCOL")
    print("  Aggregating datasets from across the globe...")
    print("=" * 60)

    # ─────────────────────────────────────────────────────────
    # 1. ISOT Dataset (~45k) — Local
    # ─────────────────────────────────────────────────────────
    print("\n[1/10] ISOT Fake/Real News Dataset")
    fake_path = os.path.join(data_dir, 'Fake.csv')
    true_path = os.path.join(data_dir, 'True.csv')
    if os.path.exists(fake_path) and os.path.exists(true_path):
        f_df = pd.read_csv(fake_path)
        t_df = pd.read_csv(true_path)
        f_df['label'] = 1
        t_df['label'] = 0
        isot = pd.concat([f_df, t_df])
        add_dataset(all_dfs, isot, "ISOT", ['title', 'text'], 'label')
    else:
        print("  [SKIP] Local ISOT data not found.")

    # ─────────────────────────────────────────────────────────
    # 2. WELFake Dataset (~72k) — Zenodo
    # ─────────────────────────────────────────────────────────
    print("\n[2/10] WELFake Dataset (Zenodo)")
    welfake_url = "https://zenodo.org/record/4561253/files/WELFake_Dataset.csv"
    welfake_df = download_and_cache(welfake_url, "WELFake_Dataset.csv")
    if welfake_df is not None:
        # WELFake: 1=Real, 0=Fake → flip to 0=Real, 1=Fake
        welfake_df['label'] = welfake_df['label'].apply(lambda x: 1 if x == 0 else 0)
        add_dataset(all_dfs, welfake_df, "WELFake", ['title', 'text'], 'label')

    # ─────────────────────────────────────────────────────────
    # 3. LIAR Dataset (~12k) — GitHub
    # ─────────────────────────────────────────────────────────
    print("\n[3/10] LIAR Dataset (PolitiFact)")
    liar_url = "https://raw.githubusercontent.com/thiagorainmaker77/liar_dataset/master/train.tsv"
    liar_df = download_and_cache(liar_url, "liar_train.tsv")
    if liar_df is not None:
        liar_df['label'] = liar_df[1].apply(lambda x: 1 if x in ['pants-fire', 'false', 'barely-true'] else 0)
        liar_df['content'] = liar_df[2].fillna('')
        all_dfs.append(liar_df[['content', 'label']])
        print(f"  [OK] LIAR: {len(liar_df)} records added")

    # Also grab LIAR test + valid sets
    for split in ['test', 'valid']:
        url = f"https://raw.githubusercontent.com/thiagorainmaker77/liar_dataset/master/{split}.tsv"
        df = download_and_cache(url, f"liar_{split}.tsv")
        if df is not None:
            df['label'] = df[1].apply(lambda x: 1 if x in ['pants-fire', 'false', 'barely-true'] else 0)
            df['content'] = df[2].fillna('')
            all_dfs.append(df[['content', 'label']])
            print(f"  [OK] LIAR-{split}: {len(df)} records added")

    # ─────────────────────────────────────────────────────────
    # 4. FakeNewsNet — PolitiFact + GossipCop (~23k) — GitHub
    # ─────────────────────────────────────────────────────────
    print("\n[4/10] FakeNewsNet (PolitiFact + GossipCop)")
    fnn_base = "https://raw.githubusercontent.com/KaiDMML/FakeNewsNet/master/dataset"
    for source in ['politifact', 'gossipcop']:
        for label_name, label_val in [('fake', 1), ('real', 0)]:
            url = f"{fnn_base}/{source}_{label_name}.csv"
            df = download_and_cache(url, f"fnn_{source}_{label_name}.csv")
            if df is not None:
                df['label'] = label_val
                add_dataset(all_dfs, df, f"FNN-{source}-{label_name}", 'title', 'label')

    # ─────────────────────────────────────────────────────────
    # 5. COVID-19 Fake News (~10k) — GitHub
    # ─────────────────────────────────────────────────────────
    print("\n[5/10] COVID-19 Fake News Dataset")
    covid_url = "https://raw.githubusercontent.com/mohdahmad242/COVID19-Fake-News-Detection/main/dataset/PrePro/train_pre.csv"
    covid_df = download_and_cache(covid_url, "covid_fake_news.csv")
    if covid_df is not None:
        # Columns: text, label (0=real, 1=fake typically)
        if 'label' in covid_df.columns and 'text' in covid_df.columns:
            add_dataset(all_dfs, covid_df, "COVID-19", 'text', 'label')
        elif 'tweet' in covid_df.columns:
            add_dataset(all_dfs, covid_df, "COVID-19", 'tweet', 'label')
        else:
            # Try first two columns
            cols = covid_df.columns.tolist()
            if len(cols) >= 2:
                covid_df.columns = ['text', 'label'] + cols[2:]
                add_dataset(all_dfs, covid_df, "COVID-19", 'text', 'label')

    # ─────────────────────────────────────────────────────────
    # 6. FA-KES Conflict News (~804) — Zenodo
    # ─────────────────────────────────────────────────────────
    print("\n[6/10] FA-KES (Syrian War Conflict News)")
    fakes_url = "https://zenodo.org/record/2607278/files/FA-KES-Dataset.csv"
    fakes_df = download_and_cache(fakes_url, "FA-KES-Dataset.csv")
    if fakes_df is not None:
        # Columns: article_title, article_content, labels (1=fake, 0=real)
        if 'article_content' in fakes_df.columns:
            add_dataset(all_dfs, fakes_df, "FA-KES", ['article_title', 'article_content'], 'labels')
        elif 'text' in fakes_df.columns:
            add_dataset(all_dfs, fakes_df, "FA-KES", 'text', 'label')

    # ─────────────────────────────────────────────────────────
    # 7. Extended Synthetic Global Samples
    # ─────────────────────────────────────────────────────────
    print("\n[7/10] Synthetic Global Edge-Cases")
    synthetic_data = [
        # Health misinformation
        ("New miracle drug cures all cancers in 24 hours without any side effects", 1),
        ("Drinking bleach can cure coronavirus according to anonymous doctors", 1),
        ("WHO recommends a balanced diet and regular exercise for better health", 0),
        ("FDA approves new treatment for type 2 diabetes after clinical trials", 0),
        # Political conspiracies
        ("Secret government program to control population through water supply", 1),
        ("Election was rigged by foreign hackers who manipulated voting machines", 1),
        ("Congress passes bipartisan infrastructure bill worth 1.2 trillion dollars", 0),
        ("Supreme Court rules unanimously on landmark civil rights case", 0),
        # Technology scams  
        ("5G towers are spreading a new virus across major cities worldwide", 1),
        ("Vaccine contains microchips designed by tech companies to track citizens", 1),
        ("Apple announces new iPhone model with improved battery and camera features", 0),
        ("Google releases quarterly earnings report showing strong cloud growth", 0),
        # Financial scams
        ("Make ten thousand dollars per day with this one simple trick at home", 1),
        ("Exclusive crypto investment guarantees 1000 percent returns in one week", 1),
        ("Federal Reserve raises interest rates by quarter point to fight inflation", 0),
        ("Stock market indices reach new highs as unemployment rates drop to record low", 0),
        # Celebrity/Social
        ("Famous actor secretly died 3 years ago and was replaced by a clone", 1),
        ("Aliens spotted landing near Area 51 captured on viral footage", 1),
        ("NASA launches new Mars rover mission to study soil composition samples", 0),
        ("International climate summit reaches historic agreement on carbon emissions", 0),
        # Indian/Regional
        ("Government to distribute free laptops to all citizens starting tomorrow", 1),
        ("WhatsApp forward claims drinking warm water kills all viruses instantly", 1),
        ("India GDP growth rate reaches 7.2 percent according to finance ministry report", 0),
        ("Indian Space Research Organisation successfully launches new satellite", 0),
    ]
    syn_df = pd.DataFrame(synthetic_data, columns=['content', 'label'])
    all_dfs.append(syn_df)
    print(f"  [OK] Synthetic Samples: {len(syn_df)} records added")

    # ─────────────────────────────────────────────────────────
    # 8-10. Datasets that require special access (logged)
    # ─────────────────────────────────────────────────────────
    print("\n[8/10] CREDBANK (60M tweets)")
    print("  [SKIP] Requires Twitter API credentials & research access")
    print("\n[9/10] NELA-GT (1.8M articles)")
    print("  [SKIP] Requires Harvard Dataverse research agreement")
    print("\n[10/10] Fakeddit (1M Reddit posts)")
    print("  [SKIP] Requires Google Drive download (too large for auto-fetch)")

    # ─────────────────────────────────────────────────────────
    # MERGE & TRAIN
    # ─────────────────────────────────────────────────────────
    if not all_dfs:
        print("\n[FATAL] No datasets loaded!")
        return

    print("\n" + "=" * 60)
    print("  MERGING ALL DATASETS...")
    print("=" * 60)
    df = pd.concat(all_dfs, ignore_index=True)
    df.drop_duplicates(subset=['content'], inplace=True)
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    print(f"  Total Unique Records: {len(df)}")
    print(f"  Fake: {(df['label']==1).sum()} | Real: {(df['label']==0).sum()}")

    print("\n  Cleaning text (this may take 5-10 minutes)...")
    df['content'] = df['content'].apply(clean_text)
    df = df[df['content'].str.len() > 20]

    X = df['content']
    y = df['label']

    print(f"  Final clean dataset: {len(X)} records")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, random_state=42)

    print("\n  Building Mega-Scale Ensemble...")
    features = FeatureUnion([
        ('word_tfidf', TfidfVectorizer(max_features=30000, ngram_range=(1, 2))),
        ('char_tfidf', TfidfVectorizer(max_features=10000, analyzer='char', ngram_range=(3, 4)))
    ])

    lr = LogisticRegression(max_iter=1000, C=5)
    mlp = MLPClassifier(hidden_layer_sizes=(64,), max_iter=200, early_stopping=True, random_state=42)

    ensemble = VotingClassifier(
        estimators=[('lr', lr), ('mlp', mlp)],
        voting='soft'
    )

    pipeline = Pipeline([
        ('features', features),
        ('clf', ensemble)
    ])

    print(f"  Training on {len(X_train)} samples...")
    pipeline.fit(X_train, y_train)

    print("\n" + "=" * 60)
    print("  PERFORMANCE AUDIT")
    print("=" * 60)
    preds = pipeline.predict(X_test)
    print(f"  Global Accuracy: {accuracy_score(y_test, preds) * 100:.2f}%")
    print(classification_report(y_test, preds))

    print("  Saving compressed model...")
    os.makedirs('models', exist_ok=True)
    joblib.dump(pipeline, 'models/model.joblib', compress=3)
    print("\n  TRAINING COMPLETE!")
    print("  TrustGuard AI is now a global-scale truth engine.")
    print("=" * 60)

if __name__ == '__main__':
    train()
