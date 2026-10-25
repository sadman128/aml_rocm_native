import pandas as pd
import json

df_all = pd.read_csv('outputs/v10_final/ALL_SEED_RESULTS.csv')
df_unseen = pd.read_csv('outputs/v10_final/UNSEEN_ATTACKS_RESULTS.csv')

for s in [42, 123, 2024]:
    zd = json.load(open(f'outputs/v10_final/seeds/{s}/zero_day_spec.json'))
    print(f'=== SEED {s} ===')
    print('Held-out Zero-Day Attack:', zd['held_out_attack'])
    sub_v10 = df_all[(df_all['seed']==s) & (df_all['method']=='V10 Defense')]
    for _, r in sub_v10.iterrows():
        atk = r['attack']
        b_acc = r['accuracy'] * 100
        asr = r.get('attack_success_rate', float('nan')) * 100
        m_acc = r.get('multi_accuracy', float('nan')) * 100
        m_f1 = r.get('multi_weighted_f1', float('nan'))
        zd_c = r.get('zero_day_caught_as_attack', float('nan')) * 100
        print(f"  {atk:22s} -> Binary: {b_acc:.2f}%, ASR: {asr:.2f}%, Multi Acc: {m_acc:.2f}%, Multi F1: {m_f1:.4f}, ZD Caught: {zd_c:.2f}%")
        
    sub_unseen = df_unseen[(df_unseen['seed']==s) & (df_unseen['method']=='V10 Defense')]
    for _, r in sub_unseen.iterrows():
        atk = r['attack']
        b_acc = r['accuracy'] * 100
        asr = r.get('attack_success_rate', float('nan')) * 100
        print(f"  {atk:22s} -> Binary: {b_acc:.2f}%, ASR: {asr:.2f}%")
