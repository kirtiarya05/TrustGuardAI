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

# Download stopwords
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
    text = " ".join([word for word in text.split() if word not in STOPWORDS])
    return text

def download_and_cache(url, filename):
    cache_path = os.path.join('../data', filename)
    if os.path.exists(cache_path):
        print(f"Using cached dataset: {filename}")
        if filename.endswith('.tsv'):
            return pd.read_csv(cache_path, sep='\t', header=None, on_bad_lines='skip')
        return pd.read_csv(cache_path)
    
    print(f"Downloading {filename} from {url}...")
    try:
        response = requests.get(url, timeout=60, stream=True)
        response.raise_for_status()
        content = response.content
        with open(cache_path, 'wb') as f:
            f.write(content)
        if filename.endswith('.tsv'):
            return pd.read_csv(io.BytesIO(content), sep='\t', header=None, on_bad_lines='skip')
        return pd.read_csv(io.BytesIO(content))
    except Exception as e:
        print(f"Failed to download/load {filename}: {e}")
        return None

def train():
    all_dfs = []
    data_dir = '../data'
    os.makedirs(data_dir, exist_ok=True)

    # 1. Local ISOT Dataset (~45k)
    fake_path = os.path.join(data_dir, 'Fake.csv')
    true_path = os.path.join(data_dir, 'True.csv')
    if os.path.exists(fake_path) and os.path.exists(true_path):
        print("Loading local ISOT dataset...")
        f_df = pd.read_csv(fake_path)
        t_df = pd.read_csv(true_path)
        f_df['label'] = 1
        t_df['label'] = 0
        isot = pd.concat([f_df, t_df])
        isot['content'] = isot['title'].fillna('') + ' ' + isot['text'].fillna('')
        all_dfs.append(isot[['content', 'label']])

    # 2. WELFake Dataset (~72k)
    welfake_url = "https://zenodo.org/record/4561253/files/WELFake_Dataset.csv"
    welfake_df = download_and_cache(welfake_url, "WELFake_Dataset.csv")
    if welfake_df is not None:
        print(f"Adding WELFake dataset ({len(welfake_df)} rows)...")
        # WELFake Label: 1=Real, 0=Fake -> Normalize to 0=Real, 1=Fake
        welfake_df['label'] = welfake_df['label'].apply(lambda x: 1 if x == 0 else 0)
        welfake_df['content'] = welfake_df['title'].fillna('') + ' ' + welfake_df['text'].fillna('')
        all_dfs.append(welfake_df[['content', 'label']])

    # 3. LIAR Dataset (~12k)
    liar_url = "https://raw.githubusercontent.com/thiagorainmaker77/liar_dataset/master/train.tsv"
    liar_df = download_and_cache(liar_url, "liar_train.tsv")
    if liar_df is not None:
        print(f"Adding LIAR dataset ({len(liar_df)} rows)...")
        # Column indices: 1 is label, 2 is statement
        liar_df['label'] = liar_df[1].apply(lambda x: 1 if x in ['pants-fire', 'false', 'barely-true'] else 0)
        liar_df['content'] = liar_df[2].fillna('')
        all_dfs.append(liar_df[['content', 'label']])

    if not all_dfs:
        print("No datasets available for training!")
        return

    print("Merging and deduplicating massive dataset...")
    df = pd.concat(all_dfs, ignore_index=True)
    df.drop_duplicates(subset=['content'], inplace=True)
    print(f"Total Unique Records: {len(df)}")

    print("Cleaning text (processing ~120k records - this may take 3-5 minutes)...")
    df['content'] = df['content'].apply(clean_text)
    df = df[df['content'].str.len() > 20] # Filter out noise
    
    X = df['content']
    y = df['label']

    print("Splitting datasets (15% for evaluation)...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, random_state=42)

    print("Building Mega-Scale Ensemble (Word TF-IDF + Char N-Grams)...")
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

    print(f"Training TrustGuard Mega-Model on {len(X_train)} samples...")
    pipeline.fit(X_train, y_train)

    print("\n--- PERFORMANCE AUDIT ---")
    preds = pipeline.predict(X_test)
    print(f"Global Accuracy: {accuracy_score(y_test, preds) * 100:.2f}%")
    print(classification_report(y_test, preds))

    print("Saving compressed model to models/model.joblib...")
    os.makedirs('models', exist_ok=True)
    joblib.dump(pipeline, 'models/model.joblib', compress=3)
    print("Deployment complete! The AI is now a highly sophisticated global truth-engine.")

if __name__ == '__main__':
    train()
