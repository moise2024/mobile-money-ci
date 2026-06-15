# 🗺️ Feuille de route — Projet Mobile Money CI

*Notre plan de bataille pour aller jusqu'à la soutenance*

---

## 📊 État d'avancement

```
████████████████████████████░░░░░░░  70%  (10 étapes sur 14)
```

| # | Tâche | Statut | Temps estimé |
|---|---|---|---|
| 1 | Création structure projet | ✅ Terminé | — |
| 2 | Pipeline ETL + tests qualité | ✅ Terminé | — |
| 3 | Schéma en étoile + SQL | ✅ Terminé | — |
| 4 | Dashboard 5 graphiques | ✅ Terminé | — |
| 5 | DAG Airflow + callbacks | ✅ Terminé | — |
| 6 | Dockerfile + docker-compose | ✅ Terminé | — |
| 7 | dbt (bonus) | ✅ Terminé | — |
| 8 | Rapport technique PDF | ✅ Terminé | — |
| 9 | Carte mentale | ✅ Terminé | — |
| 10 | Histoire de l'amitié | ✅ Terminé | — |
| **11** | **Notebook Jupyter .ipynb** | ⏳ **À faire** | **~1h** |
| **12** | **Création compte Supabase + captures** | ⏳ **À faire** | **~30min** |
| **13** | **Repo GitHub + push** | ⏳ **À faire** | **~30min** |
| **14** | **Slides de soutenance** | ⏳ **À faire** | **~2h** |

---

## 📅 Planning des tâches restantes

### Étape 11 : Notebook Jupyter .ipynb
**Objectif :** Convertir `etl_pipeline.py` en notebook exécutable cellule par cellule
**À faire :**
- Créer le fichier `.ipynb` avec toutes les cellules
- Ajouter les commentaires pédagogiques (chaque bloc expliqué)
- Tester `Runtime → Run all` sans erreur

### Étape 12 : Compte Supabase + Captures
**Objectif :** Prendre les 4 captures d'écran pour le rapport
**À faire :**
- Créer un compte sur supabase.com (gratuit, sans CB)
- Créer un projet `mobile-money-ci`
- Exécuter les scripts SQL (`create_tables.sql`, `star_schema.sql`)
- Charger les données depuis le pipeline ETL
- Prendre captures : Table Editor, SQL Editor (×2), dashboard

### Étape 13 : GitHub
**Objectif :** Rendre le projet accessible publiquement
**À faire :**
- Créer le repo sur GitHub (public)
- Initialiser git, commit, push
- Ajouter le lien dans le rapport PDF

### Étape 14 : Slides de soutenance
**Objectif :** 10-15 slides pour 15 minutes de présentation
**Structure suggérée :**
```
1. Titre + noms du trinôme
2. Contexte métier (Mobile Money CI)
3. Architecture du pipeline (schéma)
4. Dataset — audit de qualité
5. ETL — transformations clés
6. Schéma en étoile (diagramme)
7. Résultats SQL — top requêtes
8. Tableau de bord — 5 graphiques
9. Orchestration — DAG Airflow
10. Docker — containerisation
11. Difficultés rencontrées
12. Conclusion + démo live
```

---

## 🔗 Dépendances entre les tâches

```
Notebook.ipynb  ──→  GitHub push
      │
      ├──→  Rapport PDF  (déjà fait)
      │
      ├──→  Slides       (après le notebook)
      │
      └──→  Soutenance   (tout doit être prêt)
      
Supabase  ──→  Captures  ──→  Rapport final
```

---

## 🎯 Objectif final

**Soutenance devant le jury** : 15 minutes de présentation + 10 minutes de questions
- Coefficient : 40% de la note finale
- Chaque membre du trinôme doit parler ≥ 5 minutes
- Le code doit être compréhensible et commenté

---

## ⌛ Temps restant estimé

| Tâche | Durée |
|---|---|
| Notebook .ipynb | 1h |
| Supabase + captures | 30min |
| GitHub push | 30min |
| Slides | 2h |
| **Total** | **~4h** |

---

*Cette feuille de route a été créée par notre trinôme pour visualiser clairement ce qu'il reste à faire et ne rien oublier. Chaque tâche cochée est une victoire de plus vers la soutenance.*
