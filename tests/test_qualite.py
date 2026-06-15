import pandas as pd
import numpy as np

def valider_qualite(df, seuil_lignes=80000, seuil_nan=0.01, seuil_taux_succes=70.0):
    erreurs = []
    avertissements = []

    nb = len(df)
    if nb < seuil_lignes:
        erreurs.append(f'ERREUR : {nb:,} lignes < seuil {seuil_lignes:,}')
    else:
        print(f'  OK : {nb:,} lignes (seuil={seuil_lignes:,})')

    for col in ['id_transaction', 'montant_fcfa', 'operateur', 'statut']:
        taux_nan = df[col].isnull().mean()
        if taux_nan > seuil_nan:
            erreurs.append(f'ERREUR : {col} a {taux_nan:.1%} de NaN > seuil {seuil_nan:.0%}')
        else:
            print(f'  OK : {col} completude {(1-taux_nan):.1%}')

    nb_doublons = df['id_transaction'].duplicated().sum()
    if nb_doublons > 0:
        erreurs.append(f'ERREUR : {nb_doublons} doublons sur id_transaction')
    else:
        print(f'  OK : pas de doublons sur id_transaction')

    nb_invalides = (df['montant_fcfa'] <= 0).sum()
    if nb_invalides > 0:
        erreurs.append(f'ERREUR : {nb_invalides} montants <= 0')
    else:
        print(f'  OK : tous les montants > 0')

    statuts_attendus = {'Succès', 'Échec', 'En attente'}
    statuts_invalides = set(df['statut'].dropna().unique()) - statuts_attendus
    if statuts_invalides:
        erreurs.append(f'ERREUR : statuts inconnus : {statuts_invalides}')
    else:
        print(f'  OK : statuts valides {set(df["statut"].unique())}')

    taux_s = (df['statut'] == 'Succès').mean() * 100
    if taux_s < seuil_taux_succes:
        avertissements.append(f'AVERT : taux succes {taux_s:.1f}% < seuil {seuil_taux_succes}%')
    else:
        print(f'  OK : taux succes {taux_s:.1f}%')

    for avert in avertissements:
        print(f'  {avert}')

    if erreurs:
        print(f'\n  ECHEC : {len(erreurs)} erreur(s) bloquante(s)')
        for e in erreurs:
            print(f'    -> {e}')
        raise ValueError(f'Qualite insuffisante : {len(erreurs)} erreur(s)')
    else:
        print(f'\n  QUALITE OK -- {len(df):,} lignes validees')
    return True

def test_valider_qualite():
    df = pd.DataFrame({
        'id_transaction': [f'TXN{i:07d}' for i in range(100)],
        'montant_fcfa': [1000] * 100,
        'operateur': ['MTN CI'] * 100,
        'statut': ['Succès'] * 80 + ['Echec'] * 20,
    })
    assert valider_qualite(df) == True

if __name__ == '__main__':
    test_valider_qualite()
    print('Tests passes ✅')
