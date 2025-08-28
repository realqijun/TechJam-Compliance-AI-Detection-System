import pandas as pd

def load_data(file_path: str) -> pd.DataFrame:
  try:
    df = pd.read_csv(file_path)
    print(f"Loaded {len(df)} features from {file_path}")
    return df
  except Exception as e:
    print(f"Error loading data: {e}, returning empty DataFrame instead.")
    return pd.DataFrame()
  
if __name__ == "__main__":
  # run this as a script for quick testing
  df = load_data('data/sample_data.csv')
  if df.empty:
    print("No data loaded. Please check your file path.")