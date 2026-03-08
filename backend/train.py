import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score
import os

def train():
    print("Loading datasets...")
    # Paths adjusted based on your folder structure
    fake_path = '../data/Fake.csv'
    true_path = '../data/True.csv'
    
    if not os.path.exists(fake_path) or not os.path.exists(true_path):
        print(f"Dataset not found at {fake_path} or {true_path}. Please make sure they exist.")
        return

    fake_df = pd.read_csv(fake_path)
    true_df = pd.read_csv(true_path)

    print(f"Loaded {len(fake_df)} fake news records and {len(true_df)} true news records.")

    # Assign labels: 1 = Fake, 0 = Real
    fake_df['label'] = 1
    true_df['label'] = 0

    # Combine dataframes
    df = pd.concat([fake_df, true_df], ignore_index=True)
    
    # Text preprocessing: combine title and text
    print("Preprocessing text data...")
    df['content'] = df['title'].fillna('') + ' ' + df['text'].fillna('')
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)

    # We use a manageable sample if data is huge for quick prototyping, here we use full data (44k) as TF-IDF is fast
    X = df['content']
    y = df['label']

    print("Splitting data into training and test sets...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    print("Building NLP pipeline (TF-IDF + Logistic Regression)...")
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(max_features=50000, stop_words='english', ngram_range=(1, 2))),
        ('clf', LogisticRegression(max_iter=1000, C=10))
    ])

    print("Training model... This usually takes ~10-20 seconds.")
    pipeline.fit(X_train, y_train)

    print("Evaluating model...")
    preds = pipeline.predict(X_test)
    acc = accuracy_score(y_test, preds)
    print(f"Accuracy on test set: {acc * 100:.2f}%")

    print("Saving pipeline to model.joblib...")
    # Ensure export directory exists
    os.makedirs('models', exist_ok=True)
    joblib.dump(pipeline, 'models/model.joblib')
    print("Training complete! Model ready for the FastAPI server.")

if __name__ == '__main__':
    train()
