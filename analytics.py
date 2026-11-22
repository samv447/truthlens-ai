"""History aggregation for the dashboard."""
import pandas as pd

def history_frame(records):
    df = pd.DataFrame(records, columns=['id', 'created_at', 'preview', 'label', 'score'])
    if not df.empty:
        df['created_at'] = pd.to_datetime(df['created_at'], utc=True, errors='coerce')
        df['date'] = df['created_at'].dt.date.astype(str)
    return df

def summary(records):
    df = history_frame(records)
    counts = df['label'].value_counts().to_dict() if not df.empty else {}
    return {'total': len(df), 'fake': counts.get('FAKE', 0), 'real': counts.get('REAL', 0)}
