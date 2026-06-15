# Pipeline ETL Mobile Money — Côte d'Ivoire

Pipeline de données industrialisé pour l'analyse des transactions Mobile Money en Côte d'Ivoire (100 000 transactions, 4 opérateurs).

## Architecture
```
CSV brut → Airflow DAG → Pandas (ETL) → Supabase PostgreSQL → dbt → Parquet → Dashboard
```

## Technologies
- **Orchestration** : Apache Airflow 2.9
- **Transformation** : Python 3.10, Pandas 2.0
- **Base de données** : Supabase (PostgreSQL 15)
- **Modèles analytiques** : dbt 1.8
- **Conteneurisation** : Docker + docker-compose
- **CI/CD** : GitHub Actions
- **Visualisation** : Matplotlib / Seaborn

## Résultats clés
- Volume traité : 14,8 milliards FCFA / 6 mois
- Taux de succès : 80,3%
- Compression CSV → Parquet : 77%
- Pipeline quotidien : 23h00 → rapport disponible à 00h15

## Structure
```
pipeline_mobile_money/
├── dags/              # DAGs Apache Airflow
├── data/              # Données (raw, clean, output)
├── tests/             # Tests unitaires pytest
├── Dockerfile         # Containerisation
├── docker-compose.yml # Orchestration locale
└── requirements.txt   # Dépendances Python
```

## Auteurs
Notre trinôme — Projet de fin de module Data Engineering
