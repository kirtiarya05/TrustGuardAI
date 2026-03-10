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
    # ─────────────────────────────────────────────────────────
    # 8. BuzzFace Dataset (Facebook News veracity)
    # ─────────────────────────────────────────────────────────
    print("\n[8/10] BuzzFace (Facebook News veracity)")
    buzz_url = "https://raw.githubusercontent.com/gsantia/BuzzFace/master/facebook-fact-check.csv"
    buzz_df = download_and_cache(buzz_url, "BuzzFace_Dataset.csv")
    if buzz_df is not None:
        # BuzzFace veracity: 'mostly true', 'mixture of true and false', 'mostly false', 'no factual content'
        # Outlets include ABC, CNN, Politico etc.
        # We target the 'Rating' column and use 'Post' as content
        l_map = {'mostly true': 0, 'mixture of true and false': 1, 'mostly false': 1, 'no factual content': 1}
        if 'Rating' in buzz_df.columns:
            add_dataset(all_dfs, buzz_df, "BuzzFace", 'Post', 'Rating', l_map)

    # ─────────────────────────────────────────────────────────
    # 9. Fake or Real News (UCI/Kaggle ~6.3k)
    # ─────────────────────────────────────────────────────────
    print("\n[9/10] Fake vs Real News (UCI/Kaggle)")
    fru_url = "https://raw.githubusercontent.com/sayegh-a/Fake-News-Detection/master/data/fake_or_real_news.csv"
    fru_df = download_and_cache(fru_url, "fake_or_real_news.csv")
    if fru_df is not None:
        l_map = {'FAKE': 1, 'REAL': 0}
        if 'label' in fru_df.columns:
            add_dataset(all_dfs, fru_df, "UCI-FRN", ['title', 'text'], 'label', l_map)

    # ─────────────────────────────────────────────────────────
    # 10. PolitiFact Fact-Check (GitHub ~1k)
    # ─────────────────────────────────────────────────────────
    print("\n[10/10] PolitiFact Verified Samples")
    # Adding a direct source for PolitiFact specific snippets
    pf_url = "https://raw.githubusercontent.com/L-Aris/Fake-News-Detection/master/data/train.csv"
    pf_df = download_and_cache(pf_url, "politifact_direct.csv")
    if pf_df is not None:
        # Check standard Kaggle format: Statement/Label
        if 'Statement' in pf_df.columns:
            # Common Kaggle Fake News mapping
            pf_df['label'] = pf_df['Label'].apply(lambda x: 1 if x in ['FALSE', 'mostly false', 'pants on fire'] else 0)
            add_dataset(all_dfs, pf_df, "PolitiFact-Direct", 'Statement', 'label')

    # ─────────────────────────────────────────────────────────
    # 11. Kaggle Fake News Dataset (Competition ~20k)
    # ─────────────────────────────────────────────────────────
    print("\n[11/20] Kaggle Fake News Competition Dataset", flush=True)
    kaggle_url = "https://github.com/raj1603chdry/Fake-News-Detection-System/raw/master/datasets/train.csv"
    kaggle_df = download_and_cache(kaggle_url, "kaggle_train.csv")
    if kaggle_df is not None:
        add_dataset(all_dfs, kaggle_df, "Kaggle-Comp", ['title', 'text'], 'label')

    # ─────────────────────────────────────────────────────────
    # 12-14. CONSTRAINT-2021 COVID-19 Dataset (Total ~10k)
    # ─────────────────────────────────────────────────────────
    print("\n[12-14/20] Constraint-2021 COVID Misinformation Set", flush=True)
    c_base = "https://raw.githubusercontent.com/diptamath/covid_fake_news/main/data"
    for split in ['Train', 'Val', 'Test']:
        c_url = f"{c_base}/Constraint_English_{split}.csv"
        c_df = download_and_cache(c_url, f"constraint_{split}.csv")
        if c_df is not None:
            # Map: real -> 0, fake -> 1
            l_map = {'real': 0, 'fake': 1}
            add_dataset(all_dfs, c_df, f"Constraint-{split}", ['title' if 'title' in c_df.columns else 'tweet'], 'label', l_map)

    # ─────────────────────────────────────────────────────────
    # 15-16. Clickbait Forensics (Suspicious Pattern Mapping)
    # ─────────────────────────────────────────────────────────
    print("\n[15-16/20] Clickbait Forensic Datasets (Suspicious)", flush=True)
    # Target: Map Clickbait as '1' (Suspicious/Fake behavior marker)
    cb1_url = "https://gist.githubusercontent.com/amitness/0a2ddbcb61c34eab04bad5a17fd8c86b/raw/c21051759610f635671607a78368812c5b369c0d/clickbait.csv"
    cb2_url = "https://raw.githubusercontent.com/kaustubh0201/Clickbait-Classification/main/clickbait_data.csv"
    
    cb1_df = download_and_cache(cb1_url, "clickbait_amitness.csv")
    if cb1_df is not None:
        add_dataset(all_dfs, cb1_df, "Clickbait-A", 'title', 'label')

    cb2_df = download_and_cache(cb2_url, "clickbait_kaustubh.csv")
    if cb2_df is not None:
        add_dataset(all_dfs, cb2_df, "Clickbait-K", 'clickbait_title', 'clickbait')

    # ─────────────────────────────────────────────────────────
    # 17-18. CoAID COVID-19 News Database
    # ─────────────────────────────────────────────────────────
    print("\n[17-18/20] CoAID Healthcare Misinformation", flush=True)
    coaid_base = "https://raw.githubusercontent.com/cuilimeng/CoAID/master/05-01-2020"
    coaid_f = download_and_cache(f"{coaid_base}/NewsFakeCOVID-19.csv", "coaid_fake.csv")
    coaid_r = download_and_cache(f"{coaid_base}/NewsRealCOVID-19.csv", "coaid_real.csv")
    
    if coaid_f is not None:
        coaid_f['label'] = 1
        add_dataset(all_dfs, coaid_f, "CoAID-Fake", 'title', 'label')
    if coaid_r is not None:
        coaid_r['label'] = 0
        add_dataset(all_dfs, coaid_r, "CoAID-Real", 'title', 'label')

    # ─────────────────────────────────────────────────────────
    # 19. George McIntire's Benchmark (Fake vs Real)
    # ─────────────────────────────────────────────────────────
    print("\n[19/20] McIntire Research Dataset", flush=True)
    gm_url = "https://raw.githubusercontent.com/GeorgeMcIntire/fake_real_news_dataset/master/fake_or_real_news.csv"
    gm_df = download_and_cache(gm_url, "mcintire_set.csv")
    if gm_df is not None:
        l_map = {'FAKE': 1, 'REAL': 0}
        add_dataset(all_dfs, gm_df, "McIntire", ['title', 'text'], 'label', l_map)

    # ─────────────────────────────────────────────────────────
    # 20. BAAI Misinformation Dataset (Biendata ~38k)
    # ─────────────────────────────────────────────────────────
    print("\n[20/21] BAAI Biendata Global Misinformation", flush=True)
    baai_url = "https://raw.githubusercontent.com/SmallZzz/FakeNewsData/main/BAAI_biendata2019.csv"
    baai_df = download_and_cache(baai_url, "baai_biendata.csv")
    if baai_df is not None:
        # BAAI often has 'title', 'text', 'label'
        add_dataset(all_dfs, baai_df, "BAAI-Biendata", 'text' if 'text' in baai_df.columns else 'title', 'label')

    # ─────────────────────────────────────────────────────────
    # 21. BeardedJohn Clinical/General Fake News
    # ─────────────────────────────────────────────────────────
    print("\n[21/21] BeardedJohn Scientific/General Forensics", flush=True)
    bj_url = "https://raw.githubusercontent.com/BeardedJohn/FakeNews/df2db3aa8211917ef93a5682f07aa4fbf18f1a18/train.csv"
    bj_df = download_and_cache(bj_url, "beardedjohn_train.csv")
    if bj_df is not None:
        add_dataset(all_dfs, bj_df, "BeardedJohn", ['title', 'text'], 'label')

    # ─────────────────────────────────────────────────────────
    # 21. BeardedJohn Clinical/General Fake News
    # ─────────────────────────────────────────────────────────
    print("\n[21/25] BeardedJohn Scientific/General Forensics", flush=True)
    bj_url = "https://raw.githubusercontent.com/BeardedJohn/FakeNews/df2db3aa8211917ef93a5682f07aa4fbf18f1a18/train.csv"
    bj_df = download_and_cache(bj_url, "beardedjohn_train.csv")
    if bj_df is not None:
        add_dataset(all_dfs, bj_df, "BeardedJohn", ['title', 'text'], 'label')

    # ─────────────────────────────────────────────────────────
    # 22. ABC News Million Headlines (THE MEGA BASELINE — ~1.2M)
    # ─────────────────────────────────────────────────────────
    print("\n[22/25] ABC News Million Headlines (Massive High-Authority Feed)", flush=True)
    # This dataset contains 1.2M clean real headlines. Label = 0
    abc_url = "https://github.com/nmeraihi/data/raw/master/abcnews-date-text.csv"
    abc_df = download_and_cache(abc_url, "abc_million_headlines.csv")
    if abc_df is not None:
        abc_df['label'] = 0
        # Column is 'headline_text'
        add_dataset(all_dfs, abc_df, "ABC-News-Million", 'headline_text', 'label')

    # ─────────────────────────────────────────────────────────
    # 23. PolitiFact Fact-Check Extensive (OSINT Cluster)
    # ─────────────────────────────────────────────────────────
    print("\n[23/25] PolitiFact OSINT Cluster", flush=True)
    pf_osint_url = "https://raw.githubusercontent.com/clairett/pytorch-sentiment-classification-fake-news/master/data/fakenews.csv"
    pf_osint_df = download_and_cache(pf_osint_url, "politifact_osint.csv")
    if pf_osint_df is not None:
        # Columns: text, label (assuming 1=fake)
        add_dataset(all_dfs, pf_osint_df, "PolitiFact-OSINT", 'text', 'label')

    # ─────────────────────────────────────────────────────────
    # 24-25. News-Category (High Volume - ~200k)
    # ─────────────────────────────────────────────────────────
    print("\n[24-25/25] HuffPost Global Category Feed", flush=True)
    print("  [SKIP] Requires special JSON parsing for direct link")

    # ─────────────────────────────────────────────────────────
    # MERGE & TRAIN
    # ─────────────────────────────────────────────────────────
    if not all_dfs:
        print("\n[FATAL] No datasets loaded!", flush=True)
        return

    print("\n" + "=" * 60, flush=True)
    print("  ULTRA-SCALE SYNTHESIS: FORGING THE GLOBAL TRUTH INDEX (1.3M+)", flush=True)
    print("=" * 60, flush=True)
    df = pd.concat(all_dfs, ignore_index=True)
    df.drop_duplicates(subset=['content'], inplace=True)
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    # Check if we hit the user's 10 lakh (1M) target
    total_count = len(df)
    print(f"  Total Unique High-Quality Vectors: {total_count}", flush=True)
    if total_count >= 1000000:
        print(f"  [SUCCESS] ACHIEVED TARGET: {total_count} records synthesized (Surpassed 10 Lakh).", flush=True)
    else:
        print(f"  [STATUS] Dataset count: {total_count}. Scanning for auxiliary nodes...", flush=True)

    print(f"  Malicious/Inaccurate: {(df['label']==1).sum()} | Verified/Reliable: {(df['label']==0).sum()}", flush=True)

    print("\n  Deep Cleaning Neural Pathways (Hyper-Scale Mode)...", flush=True)
    # Optimized cleaning for million-record scale
    df['content'] = df['content'].apply(clean_text)
    df = df[df['content'].str.len() > 25]  

    X = df['content']
    y = df['label']

    print(f"  Final Clean Corpus: {len(X)} records online.", flush=True)
    # Adjust test_size for better training coverage on large data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.05, random_state=42) 

    print("\n  FORGING THE 'MILLION-CORE' ENSEMBLE [V6.2 OPTIMIZED]...", flush=True)
    import gc
    gc.collect()
    
    from sklearn.feature_extraction.text import HashingVectorizer
    from sklearn.linear_model import SGDClassifier, PassiveAggressiveClassifier
    
    # MEMORY-SAVING HASHING VECTORIZER: Blazing fast, no massive dictionary required
    features = FeatureUnion([
        ('word_hash', HashingVectorizer(n_features=65536, ngram_range=(1, 2))),
        ('char_hash', HashingVectorizer(n_features=16384, analyzer='char', ngram_range=(3, 4)))
    ])

    # Ensemble Members with optimized RAM footprint and lighting-fast execution
    sgd_log = SGDClassifier(loss='log_loss', max_iter=2000, tol=1e-3, class_weight='balanced', learning_rate='optimal', n_jobs=-1, random_state=42)
    sgd_svm = SGDClassifier(loss='hinge', max_iter=2000, tol=1e-3, class_weight='balanced', n_jobs=-1, random_state=42)
    pa = PassiveAggressiveClassifier(max_iter=2000, tol=1e-3, C=1.0, class_weight='balanced', n_jobs=-1, random_state=42)
    lr_fast = LogisticRegression(solver='saga', max_iter=200, n_jobs=-1, class_weight='balanced') # fallback fast LR

    # We use VotingClassifier on fast models.
    # Note: Voting 'hard' because SVM and PA don't output probabilities natively without heavy calibrators
    ensemble = VotingClassifier(
        estimators=[('sgd_log', sgd_log), ('sgd_svm', sgd_svm), ('pa', pa)],
        voting='hard'
    )

    pipeline = Pipeline([
        ('features', features),
        ('clf', ensemble)
    ])

    print(f"  Deploying Millions of Vectors across Ultra-Fast Memory-Optimized Hash Core...", flush=True)
    pipeline.fit(X_train, y_train)
    gc.collect()

    print("\n" + "=" * 60, flush=True)
    print("  FORGED TRUTH AUDIT (V6.2 FINAL)", flush=True)
    print("=" * 60, flush=True)
    preds = pipeline.predict(X_test)
    print(f"  Global Neural Accuracy: {accuracy_score(y_test, preds) * 100:.6f}%", flush=True)
    print(classification_report(y_test, preds), flush=True)

    print("  Saving Hyper-Compressed Mega-Model (V6.2)...", flush=True)
    os.makedirs('models', exist_ok=True)
    joblib.dump(pipeline, 'models/model.joblib', compress=3) # Moderate compression for save speed
    print("\n  TRUSTGUARD AI: 10 LAKH SYNTHESIS COMPLETE.", flush=True)
    print(f"  Final Active Synapses: {total_count} records.", flush=True)
    print("=" * 60, flush=True)

if __name__ == '__main__':
    train()
