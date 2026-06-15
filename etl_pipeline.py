"""
Pipeline ETL Mobile Money Côte d'Ivoire
========================================
Étape 1 : Extraction et audit
Étape 2 : Nettoyage et transformation
Étape 3 : Enrichissement
Étape 4 : Chargement Supabase
Étape 5 : Export Parquet + JSON
"""

import pandas as pd
import numpy as np
import json
import os
import time
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
CSV_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                        'TD', 'Data2_transactions_mobile_money_100k.csv')
SUPABASE_URL = os.environ.get('SUPABASE_URL', '')

# ─── ÉTAPE 1 : EXTRACTION ET AUDIT ────────────────────────────────

print('='*60)
print('PHASE 1 : EXTRACTION ET AUDIT')
print('='*60)

debut = time.time()
df_raw = pd.read_csv(CSV_PATH, encoding='utf-8', low_memory=False)
duree = time.time() - debut
taille = df_raw.memory_usage(deep=True).sum() / 1024**2

print(f'Fichier charge : {len(df_raw):,} lignes en {duree:.2f}s ({taille:.1f} Mo)')
print(f'\nColonnes : {list(df_raw.columns)}')
print(f'\nTypes :')
print(df_raw.dtypes)
print(f'\nValeurs manquantes :')
manq = df_raw.replace('', np.nan).isnull().sum()
print(manq[manq > 0].to_frame('Nb'))

# ─── ÉTAPE 2 : NETTOYAGE ──────────────────────────────────────────

print('\n' + '='*60)
print('PHASE 2 : NETTOYAGE')
print('='*60)

df = df_raw.copy()

df['date_heure'] = pd.to_datetime(df['date_heure'])
df = df.replace('', np.nan)
df['frais_fcfa'] = df['frais_fcfa'].fillna(0).astype(int)
df['zone_beneficiaire'] = df['zone_beneficiaire'].fillna('Zone inconnue')
df['id_agent'] = df['id_agent'].fillna('AGT-INCONNU')

nb_avant = len(df)
df = df[df['montant_fcfa'] > 0].copy()
nb_aberrations = nb_avant - len(df)

print(f'Aberrations (montants <= 0) supprimees : {nb_aberrations}')
print(f'Valeurs manquantes restantes : {df.isnull().sum().sum()}')
print(f'Lignes conservees : {len(df):,}')

# ─── ÉTAPE 3 : ENRICHISSEMENT ─────────────────────────────────────

print('\n' + '='*60)
print('PHASE 3 : ENRICHISSEMENT')
print('='*60)

df['montant_net_fcfa'] = df['montant_fcfa'] - df['frais_fcfa']
df['taux_frais_pct'] = (df['frais_fcfa'] / df['montant_fcfa'] * 100).round(2)

bins = [0, 5000, 50000, 200000, float('inf')]
labels = ['Micro (<=5k)', 'Petit (5k-50k)', 'Moyen (50k-200k)', 'Gros (>200k)']
df['categorie_montant'] = pd.cut(df['montant_fcfa'], bins=bins, labels=labels, right=True).astype(str)

def tranche(h):
    if 6 <= h < 9: return 'Matin (6h-9h)'
    elif 9 <= h < 12: return 'Matinée (9h-12h)'
    elif 12 <= h < 14: return 'Déjeuner (12h-14h)'
    elif 14 <= h < 18: return 'Après-midi (14h-18h)'
    elif 18 <= h < 21: return 'Soirée (18h-21h)'
    else: return 'Nuit (21h-6h)'

df['heure'] = df['date_heure'].dt.hour
df['jour_semaine'] = df['date_heure'].dt.day_name()
df['mois'] = df['date_heure'].dt.strftime('%Y-%m')
df['tranche_horaire'] = df['heure'].apply(tranche)
df['inter_ville'] = (df['zone_expediteur'] != df['zone_beneficiaire']).astype(int)

print(f'Colonnes apres enrichissement : {len(df.columns)}')
print(f'Nouvelles colonnes : montant_net_fcfa, taux_frais_pct, categorie_montant,')
print(f'                    tranche_horaire, inter_ville, heure, jour_semaine, mois')

# ─── TESTS DE QUALITÉ ─────────────────────────────────────────────

print('\n' + '='*60)
print('TESTS DE QUALITE')
print('='*60)

assert df['id_transaction'].isnull().sum() == 0, 'ID transaction NULL'
assert (df['montant_fcfa'] > 0).all(), 'Montant <= 0 detecte'
assert df['id_transaction'].duplicated().sum() == 0, 'Doublons sur ID'
assert df['statut'].isin(['Succès', 'Échec', 'En attente']).all(), 'Statut invalide'
assert 'datetime64' in str(df['date_heure'].dtype), 'Type date incorrect'

taux_succes = (df['statut'] == 'Succès').mean() * 100
print(f'Taux de succes : {taux_succes:.1f}%')
print(f'Tous les tests passes ✅')

# ─── KPI ─────────────────────────────────────────────────────────

print('\n' + '='*60)
print('KPI PRINCIPAUX')
print('='*60)

df_succes = df[df['statut'] == 'Succès']
print(f'Volume total : {df_succes["montant_fcfa"].sum():,} FCFA')
print(f'Frais totaux : {df_succes["frais_fcfa"].sum():,} FCFA')
print(f'Montant moyen : {df_succes["montant_fcfa"].mean():,.0f} FCFA')
print(f'Nombre de transactions : {len(df):,}')
print(f'Nombre de succes : {len(df_succes):,}')

# ─── EXPORT PARQUET ──────────────────────────────────────────────

print('\n' + '='*60)
print('EXPORT PARQUET')
print('='*60)

os.makedirs(os.path.join(DATA_DIR, 'clean'), exist_ok=True)
os.makedirs(os.path.join(DATA_DIR, 'output'), exist_ok=True)

df_export = df.copy()
df_export['date_heure'] = df_export['date_heure'].astype(str)
parquet_path = os.path.join(DATA_DIR, 'output', 'transactions_propres.parquet')
df_export.to_parquet(parquet_path, engine='pyarrow', compression='snappy', index=False)

taille_csv = os.path.getsize(CSV_PATH) / 1024**2
taille_pq = os.path.getsize(parquet_path) / 1024**2
print(f'CSV     : {taille_csv:.1f} Mo')
print(f'Parquet : {taille_pq:.1f} Mo (gain {100 - taille_pq/taille_csv*100:.0f}%)')

# ─── EXPORT RAPPORT JSON ─────────────────────────────────────────

rapport = {
    'meta': {
        'titre': 'Rapport Pipeline Mobile Money CI',
        'date_generation': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'version': '1.0.0',
        'source': 'Data2_transactions_mobile_money_100k.csv',
        'periode': '2024-01 a 2024-06',
    },
    'kpi': {
        'volume_total_fcfa': int(df_succes['montant_fcfa'].sum()),
        'frais_total_fcfa': int(df_succes['frais_fcfa'].sum()),
        'nb_transactions_total': int(len(df)),
        'nb_succes': int(len(df_succes)),
        'taux_succes_pct': round(taux_succes, 1),
        'montant_moyen_fcfa': int(df_succes['montant_fcfa'].mean()),
        'montant_median_fcfa': int(df_succes['montant_fcfa'].median()),
    },
    'operateurs': df_succes.groupby('operateur').agg(
        nb_tx=('id_transaction', 'count'),
        volume=('montant_fcfa', 'sum'),
        moy=('montant_fcfa', 'mean'),
        frais=('frais_fcfa', 'sum'),
    ).round(0).astype(int).reset_index().to_dict(orient='records'),
    'tendances': df_succes.groupby('mois').agg(
        nb_tx=('id_transaction', 'count'),
        volume=('montant_fcfa', 'sum'),
    ).astype(int).reset_index().to_dict(orient='records'),
}

rapport_path = os.path.join(DATA_DIR, 'output', 'rapport_final.json')
with open(rapport_path, 'w', encoding='utf-8') as f:
    json.dump(rapport, f, ensure_ascii=False, indent=2)
print(f'\nRapport JSON : {rapport_path}')
print('Pipeline ETL termine avec succes ✅')
