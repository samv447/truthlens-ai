"""Model loading, classification, and linear-model explanations."""
from pathlib import Path
import joblib
import numpy as np
from .preprocessing import validate_text

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / 'models' / 'truthlens_pipeline.joblib'

def load_model(path=MODEL_PATH):
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError('Trained model missing. Download the dataset and run: python train_model.py')
    model = joblib.load(path)  # Load only trusted, locally generated model files.
    if not hasattr(model, 'predict') or not hasattr(model, 'predict_proba'):
        raise ValueError('Model is not a supported trained classifier pipeline.')
    return model

def predict_news(model, text):
    cleaned = validate_text(text)
    label = str(model.predict([cleaned])[0])
    probabilities = model.predict_proba([cleaned])[0]
    scores = {str(name): float(score) for name, score in zip(model.classes_, probabilities)}
    if label not in ('FAKE', 'REAL') or not np.isfinite(list(scores.values())).all():
        raise ValueError('Unexpected model output.')
    return {'label': label, 'score': scores[label], 'probabilities': scores, 'cleaned_text': cleaned}

def top_terms(model, text, limit=8):
    """Largest signed local TF-IDF contributions for a binary linear classifier."""
    try:
        vectorizer = model.named_steps['tfidf']
        classifier = model.named_steps['classifier']
        if not hasattr(classifier, 'coef_'):
            return []
        row = vectorizer.transform([validate_text(text)])
        weights = classifier.coef_[0]
        contributions = row.multiply(weights).tocoo()
        terms = vectorizer.get_feature_names_out()
        order = np.argsort(np.abs(contributions.data))[::-1][:limit]
        return [{'term': str(terms[contributions.col[i]]), 'contribution': float(contributions.data[i]), 'toward': str(classifier.classes_[1] if contributions.data[i] > 0 else classifier.classes_[0])} for i in order]
    except (AttributeError, KeyError, ValueError):
        return []
