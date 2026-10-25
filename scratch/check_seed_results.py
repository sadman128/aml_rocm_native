import pandas as pd
for s in [42, 123, 2024]:
    df = pd.read_csv(f'outputs/v10_final/seeds/{s}/seed_results.csv')
    print(f'=== SEED {s} ===')
    for idx, r in df.iterrows():
        m = r['method']
        a = r['attack']
        acc = r['accuracy']
        f1 = r['f1']
        print(f'{m:<15} | {a:<25} | acc={acc:.4f} | f1={f1:.4f}')
