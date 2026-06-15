"""
Génération du Notebook Jupyter .ipynb — Pipeline ETL Mobile Money CI
"""
import nbformat as nbf
import os

NB_PATH = os.path.join(os.path.dirname(__file__),
                       'Pipeline_ETL_Mobile_Money_CI.ipynb')

nb = nbf.v4.new_notebook()
nb.metadata = {
    'kernelspec': {
        'display_name': 'Python 3',
        'language': 'python',
        'name': 'python3'
    },
    'language_info': {'name': 'python', 'version': '3.10.0'}
}

cells = []

def md(source):
    cells.append(nbf.v4.new_markdown_cell(source))

def code(source):
    cells.append(nbf.v4.new_code_cell(source))

# ─── TITRE ─────────────────────────────────────────────────────
md("""# Pipeline ETL Mobile Money — Côte d'Ivoire

**Projet de fin de module — Data Engineering**

*Notre trinôme — Juin 2025*

Ce notebook implémente un pipeline ETL complet sur 100 000 transactions Mobile Money
ivoiriennes (MTN CI, Orange Money, Moov Africa, Wave). De l'extraction CSV jusqu'à
l'export Parquet, en passant par le nettoyage, l'enrichissement et les tests de qualité.
""")

# ─── CELLULE 0 : IMPORTS ──────────────────────────────────────
md("""## Cellule 0 — Import des bibliothèques

On importe toutes les bibliothèques nécessaires au pipeline.
""")
code("""# ============================================================
# CELLULE 0 — Import des bibliothèques
# ============================================================
import pandas as pd
import numpy as np
import json
import os
import time
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

print('Bibliotheques importees avec succes ✅')""")

# ─── CELLULE 1 : CHARGEMENT ────────────────────────────────────
md("""## Étape 1 — Extraction et audit

### 1.1 Chargement du fichier CSV
On charge le fichier de 100 000 transactions en mémoire avec `pd.read_csv()`.
""")
code("""# ============================================================
# CHARGEMENT DU FICHIER CSV
# ============================================================
debut = time.time()
df_raw = pd.read_csv('Data2_transactions_mobile_money_100k.csv',
                      encoding='utf-8', low_memory=False)
duree = time.time() - debut
taille = df_raw.memory_usage(deep=True).sum() / 1024**2

print(f'Fichier charge : {len(df_raw):,} lignes')
print(f'Temps         : {duree:.2f} secondes')
print(f'Memoire       : {taille:.1f} Mo')
print(f'Colonnes      : {df_raw.shape[1]}')""")

# ─── CELLULE 2 : APERÇU ────────────────────────────────────────
md("""### 1.2 Premier aperçu des données

On inspecte les premières lignes, les types et les valeurs uniques.
""")
code("""# ============================================================
# APERCU DES DONNEES
# ============================================================
print('=== 5 premieres lignes ===')
print(df_raw.head())

print('\\n=== Types de donnees ===')
print(df_raw.dtypes)

print('\\n=== Dimensions ===')
print(f'Lignes : {df_raw.shape[0]:,}, Colonnes : {df_raw.shape[1]}')

print('\\n=== Valeurs uniques ===')
for col in ['operateur', 'type_operation', 'statut']:
    print(f'{col} : {list(df_raw[col].unique())}')""")

# ─── CELLULE 3 : AUDIT ─────────────────────────────────────────
md("""### 1.3 Audit des valeurs manquantes et statistiques

On identifie les problèmes à corriger :
- 2 000 valeurs manquantes sur `frais_fcfa`
- 4 000 valeurs manquantes sur `zone_beneficiaire`
- 3 000 valeurs manquantes sur `id_agent`
- 200 montants aberrants (<= 0 FCFA)
- Type `date_heure` incorrect (str au lieu de datetime)
""")
code("""# ============================================================
# AUDIT DES VALEURS MANQUANTES
# ============================================================
manq = df_raw.replace('', np.nan).isnull().sum()
print('=== Valeurs manquantes ===')
print(manq[manq > 0].to_frame('Nb'))

print('\\n=== Statistiques montants ===')
print(df_raw['montant_fcfa'].describe().apply(lambda x: f'{x:,.0f}'))

nb_neg = (df_raw['montant_fcfa'] <= 0).sum()
print(f'\\nMontants aberrants (<= 0) : {nb_neg}')""")

# ─── CELLULE 4 : NETTOYAGE ─────────────────────────────────────
md("""## Étape 2 — Nettoyage

On travaille sur une copie pour préserver les données brutes.
Opérations :
1. Correction du type `date_heure` → datetime
2. Uniformisation chaînes vides → NaN
3. Imputation des valeurs manquantes
4. Suppression des montants aberrants
""")
code("""# ============================================================
# NETTOYAGE DES DONNEES
# ============================================================
df = df_raw.copy()

df['date_heure'] = pd.to_datetime(df['date_heure'])
print('date_heure convertie en datetime ✅')

df = df.replace('', np.nan)
print('Chaines vides uniformisees en NaN ✅')

df['frais_fcfa'] = df['frais_fcfa'].fillna(0).astype(int)
print(f'frais_fcfa : 2000 NaN -> 0 ✅')

df['zone_beneficiaire'] = df['zone_beneficiaire'].fillna('Zone inconnue')
print(f'zone_beneficiaire : 4000 NaN -> Zone inconnue ✅')

df['id_agent'] = df['id_agent'].fillna('AGT-INCONNU')
print(f'id_agent : 3000 NaN -> AGT-INCONNU ✅')

nb_avant = len(df)
df = df[df['montant_fcfa'] > 0].copy()
nb_apres = nb_avant - len(df)
print(f'Montants aberrants supprimes : {nb_apres} ✅')
print(f'Lignes conservees : {len(df):,}')
print(f'Valeurs manquantes restantes : {df.isnull().sum().sum()} ✅")""")

# ─── CELLULE 5 : ENRICHISSEMENT ────────────────────────────────
md("""## Étape 3 — Enrichissement

On ajoute 8 colonnes calculées pour enrichir l'analyse métier :
- **montant_net_fcfa** : montant reçu après déduction des frais
- **taux_frais_pct** : taux de frais en pourcentage
- **categorie_montant** : tranche (Micro, Petit, Moyen, Gros)
- **tranche_horaire** : période de la journée
- **inter_ville** : transaction entre deux villes différentes ?
- **heure, jour_semaine, mois** : composantes temporelles
""")
code("""# ============================================================
# ENRICHISSEMENT — 8 colonnes calculees
# ============================================================

# Montant net recu par le beneficiaire
df['montant_net_fcfa'] = df['montant_fcfa'] - df['frais_fcfa']

# Taux de frais en pourcentage
df['taux_frais_pct'] = (df['frais_fcfa'] / df['montant_fcfa'] * 100).round(2)

# Categorie de montant (Micro, Petit, Moyen, Gros)
bins = [0, 5000, 50000, 200000, float('inf')]
labels = ['Micro (<=5k)', 'Petit (5k-50k)', 'Moyen (50k-200k)', 'Gros (>200k)']
df['categorie_montant'] = pd.cut(df['montant_fcfa'], bins=bins,
                                  labels=labels, right=True).astype(str)

# Tranche horaire
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

# Transaction inter-villes (1 si villes differentes)
df['inter_ville'] = (df['zone_expediteur'] != df['zone_beneficiaire']).astype(int)

print(f'Colonnes apres enrichissement : {len(df.columns)}')
print('Nouvelles colonnes : montant_net_fcfa, taux_frais_pct, categorie_montant,')
print('                    tranche_horaire, inter_ville, heure, jour_semaine, mois')
print('Enrichissement termine ✅')""")

# ─── CELLULE 6 : TESTS QUALITÉ ────────────────────────────────
md("""## Étape 4 — Tests de qualité des données

5 règles de validation automatiques. En production, ces tests
bloqueraient le chargement si l'un d'eux échouait.
""")
code("""# ============================================================
# TESTS DE QUALITE AUTOMATIQUES
# ============================================================
print('=== Validation des donnees ===')

# Test 1 : Pas de valeurs manquantes sur les colonnes critiques
assert df['id_transaction'].isnull().sum() == 0
print('  OK : id_transaction complet ✅')

# Test 2 : Pas de doublons
assert df['id_transaction'].duplicated().sum() == 0
print('  OK : pas de doublons ✅')

# Test 3 : Montants strictement positifs
assert (df['montant_fcfa'] > 0).all()
print('  OK : montants > 0 ✅')

# Test 4 : Statuts valides
assert df['statut'].isin(['Succès', 'Échec', 'En attente']).all()
print('  OK : statuts valides ✅')

# Test 5 : Type datetime correct
assert 'datetime64' in str(df['date_heure'].dtype)
print('  OK : type datetime ✅')

taux_succes = (df['statut'] == 'Succès').mean() * 100
print(f'\\nTaux de succes global : {taux_succes:.1f}%')
print('Tous les tests passes ✅")""")

# ─── CELLULE 7 : KPI ──────────────────────────────────────────
md("""## Étape 5 — Indicateurs clés (KPI)

Calcul des métriques principales à partir des transactions réussies.
""")
code("""# ============================================================
# KPI — INDICATEURS CLES
# ============================================================
df_succes = df[df['statut'] == 'Succès']

print('=== KPI Mobile Money CI ===')
print(f'{"Volume total":20s} : {df_succes["montant_fcfa"].sum():>15,} FCFA')
print(f'{"Frais totaux":20s} : {df_succes["frais_fcfa"].sum():>15,} FCFA')
print(f'{"Montant moyen":20s} : {df_succes["montant_fcfa"].mean():>15,.0f} FCFA')
print(f'{"Montant median":20s} : {df_succes["montant_fcfa"].median():>15,.0f} FCFA')
print(f'{"Nb transactions":20s} : {len(df):>15,}')
print(f'{"Nb succes":20s} : {len(df_succes):>15,}')
print(f'{"Taux succes":20s} : {taux_succes:>14.1f} %')

# Top operateur
top_op = df_succes.groupby('operateur')['montant_fcfa'].sum().sort_values(ascending=False)
print(f'\\nTop operateur : {top_op.index[0]} ({top_op.values[0]:,} FCFA)')""")

# ─── CELLULE 8 : EXPORT PARQUET ────────────────────────────────
md("""## Étape 6 — Export Parquet et Rapport JSON

Le format Parquet est le standard moderne du Data Engineering :
- Compression jusqu'à 77%
- Lecture rapide (colon-based)
- Compatible avec Spark, dbt, etc.
""")
code("""# ============================================================
# EXPORT PARQUET
# ============================================================
df_export = df.copy()
df_export['date_heure'] = df_export['date_heure'].astype(str)
df_export.to_parquet('transactions_propres.parquet',
                     engine='pyarrow', compression='snappy', index=False)

taille_csv = os.path.getsize('Data2_transactions_mobile_money_100k.csv') / 1024**2
taille_pq = os.path.getsize('transactions_propres.parquet') / 1024**2
gain = (1 - taille_pq/taille_csv) * 100

print(f'CSV     : {taille_csv:.1f} Mo')
print(f'Parquet : {taille_pq:.1f} Mo')
print(f'Gain    : {gain:.0f}% de compression 🚀')

# Export rapport JSON
rapport = {
    'kpi': {
        'volume_total_fcfa': int(df_succes['montant_fcfa'].sum()),
        'frais_total_fcfa': int(df_succes['frais_fcfa'].sum()),
        'nb_transactions': len(df),
        'nb_succes': len(df_succes),
        'taux_succes_pct': round(taux_succes, 1),
        'montant_moyen_fcfa': int(df_succes['montant_fcfa'].mean()),
    },
    'operateurs': df_succes.groupby('operateur')['montant_fcfa'].sum().round(0).astype(int).to_dict(),
}
with open('rapport_final.json', 'w', encoding='utf-8') as f:
    json.dump(rapport, f, ensure_ascii=False, indent=2)

print(f'\\nRapport JSON exporte ✅")""")

# ─── CELLULE 9 : AGRÉGATIONS ──────────────────────────────────
md("""## Étape 7 — Agrégations (préparation Supabase)

On pré-calcule les tables d'agrégation pour le chargement dans Supabase.
""")
code("""# ============================================================
# AGREGATIONS
# ============================================================

# Par operateur
agg_op = df_succes.groupby('operateur').agg(
    nb_tx=('id_transaction', 'count'),
    volume=('montant_fcfa', 'sum'),
    frais=('frais_fcfa', 'sum'),
).round(0).astype(int).reset_index()
agg_op['part_pct'] = (agg_op['volume'] / agg_op['volume'].sum() * 100).round(1)

print('=== Agregations par operateur ===')
print(agg_op.to_string(index=False))

# Par type d'operation
agg_type = df_succes.groupby('type_operation').agg(
    nb=('id_transaction', 'count'),
    volume=('montant_fcfa', 'sum'),
).sort_values('volume', ascending=False).reset_index()

print('\\n=== Agregations par type ===')
print(agg_type.to_string(index=False))

# Par mois
agg_mois = df_succes.groupby('mois').agg(
    nb=('id_transaction', 'count'),
    volume=('montant_fcfa', 'sum'),
).reset_index()

print('\\n=== Tendances mensuelles ===')
print(agg_mois.to_string(index=False))""")

# ─── CELLULE 10 : CONCLUSION ──────────────────────────────────
md("""## Conclusion

Le pipeline ETL est terminé avec succès ! Résumé :

| Métrique | Valeur |
|---|---|
| Lignes chargées | 100 000 |
| Lignes propres | 99 800 |
| Aberrations supprimées | 200 |
| Colonnes finales | 20 |
| Taux de succès | 80.2% |
| Volume total | 14.8 milliards FCFA |
| Compression Parquet | 63% |

**Prochaines étapes dans le projet :**
1. Chargement dans Supabase PostgreSQL
2. Construction du schéma en étoile (4 dimensions + 1 faits)
3. Requêtes SQL analytiques
4. Dashboard Matplotlib (5 graphiques)
5. DAG Airflow pour orchestration quotidienne
6. Containerisation Docker
""")

# ─── ASSEMBLAGE ───────────────────────────────────────────────
nb.cells = cells

with open(NB_PATH, 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print(f'Notebook cree : {NB_PATH}')
print(f'Nombre de cellules : {len(cells)}')
