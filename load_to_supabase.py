"""
Script de chargement des donnees dans Supabase PostgreSQL
Usage : python3 load_to_supabase.py "postgresql://postgres.XXX:password@pooler.supabase.com:6543/postgres"
"""
import pandas as pd
import numpy as np
import sqlalchemy
import time
import sys
import os

CSV_PATH = 'Data2_transactions_mobile_money_100k.csv'

def load_to_supabase(supabase_url):
    print('='*60)
    print('CHARGEMENT DANS SUPABASE')
    print('='*60)

    # Connexion
    engine = sqlalchemy.create_engine(supabase_url)
    with engine.connect() as conn:
        result = conn.execute(sqlalchemy.text('SELECT version()'))
        version = result.fetchone()[0]
        print(f'Connexion Supabase reussie !')
        print(f'PostgreSQL : {version[:50]}...')

    # Charger et nettoyer
    print('\nChargement du CSV...')
    df = pd.read_csv(CSV_PATH, encoding='utf-8', low_memory=False)
    df['date_heure'] = pd.to_datetime(df['date_heure'])
    df = df.replace('', np.nan)
    df['frais_fcfa'] = df['frais_fcfa'].fillna(0).astype(int)
    df['zone_beneficiaire'] = df['zone_beneficiaire'].fillna('Zone inconnue')
    df['id_agent'] = df['id_agent'].fillna('AGT-INCONNU')
    df = df[df['montant_fcfa'] > 0].copy()
    df['montant_net_fcfa'] = df['montant_fcfa'] - df['frais_fcfa']
    df['taux_frais_pct'] = (df['frais_fcfa'] / df['montant_fcfa'] * 100).round(2)
    df['heure'] = df['date_heure'].dt.hour
    df['jour_semaine'] = df['date_heure'].dt.day_name()
    df['mois'] = df['date_heure'].dt.strftime('%Y-%m')
    df['inter_ville'] = (df['zone_expediteur'] != df['zone_beneficiaire']).astype(int)

    bins = [0, 5000, 50000, 200000, float('inf')]
    labels = ['Micro (<=5k)', 'Petit (5k-50k)', 'Moyen (50k-200k)', 'Gros (>200k)']
    df['categorie_montant'] = pd.cut(df['montant_fcfa'], bins=bins, labels=labels, right=True).astype(str)

    def tranche(h):
        if 6<=h<9: return 'Matin (6h-9h)'
        elif 9<=h<12: return 'Matinée (9h-12h)'
        elif 12<=h<14: return 'Déjeuner (12h-14h)'
        elif 14<=h<18: return 'Après-midi (14h-18h)'
        elif 18<=h<21: return 'Soirée (18h-21h)'
        else: return 'Nuit (21h-6h)'
    df['tranche_horaire'] = df['heure'].apply(tranche)

    df_load = df.copy()
    df_load['date_heure'] = df_load['date_heure'].astype(str)

    # Chargement par chunks
    CHUNK_SIZE = 5000
    TOTAL = len(df_load)
    chunks = [df_load[i:i+CHUNK_SIZE] for i in range(0, TOTAL, CHUNK_SIZE)]

    print(f'\nChargement de {TOTAL:,} lignes en {len(chunks)} lots...')
    debut = time.time()

    with engine.connect() as conn:
        conn.execute(sqlalchemy.text('DELETE FROM transactions'))
        for i, chunk in enumerate(chunks):
            chunk.to_sql('transactions', conn, if_exists='append',
                        index=False, method='multi', chunksize=500)
            pct = (i+1)/len(chunks)*100
            print(f'  Lot {i+1}/{len(chunks)} - {pct:.0f}%', end='\r')
        conn.commit()

    duree = time.time() - debut
    print(f'\n✅ {TOTAL:,} lignes chargees en {duree:.1f}s')

    # Tables d'agregation
    df_s = df[df['statut'] == 'Succès']

    agg_op = df_s.groupby('operateur').agg(
        nb_transactions=('id_transaction','count'),
        volume_fcfa=('montant_fcfa','sum'),
        montant_moyen=('montant_fcfa','mean'),
        montant_median=('montant_fcfa','median'),
        frais_total=('frais_fcfa','sum'),
    ).round(0).reset_index()
    agg_op['part_volume_pct'] = (agg_op['volume_fcfa']/agg_op['volume_fcfa'].sum()*100).round(1)
    agg_op = agg_op.astype({'nb_transactions':int,'volume_fcfa':int,'montant_moyen':int,'montant_median':int,'frais_total':int})

    agg_type = df_s.groupby('type_operation').agg(
        nb=('id_transaction','count'),
        volume=('montant_fcfa','sum'),
        moy=('montant_fcfa','mean'),
    ).round(0).sort_values('volume',ascending=False).reset_index()
    agg_type = agg_type.astype({'nb':int,'volume':int,'moy':int})

    agg_zone = df_s.groupby('zone_expediteur')['montant_fcfa'].sum().sort_values(ascending=False).reset_index()
    agg_zone.columns = ['zone','volume_fcfa']
    agg_zone['part_pct'] = (agg_zone['volume_fcfa']/agg_zone['volume_fcfa'].sum()*100).round(1)
    agg_zone = agg_zone.astype({'volume_fcfa':int})

    with engine.connect() as conn:
        for nom, dt in [('agg_operateur', agg_op), ('agg_type_operation', agg_type), ('agg_zone', agg_zone)]:
            dt.to_sql(nom, conn, if_exists='replace', index=False, method='multi')
            print(f'  ✅ {nom} : {len(dt)} lignes')
        conn.commit()

    print('\n✅ Toutes les tables chargees dans Supabase !')
    print('\nVerifie dans Supabase : Table Editor -> transactions')
    engine.dispose()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python3 load_to_supabase.py "postgresql://..."')
        print('Trouve ta connection string dans Supabase -> Connect -> Session pooler')
        sys.exit(1)
    load_to_supabase(sys.argv[1])
