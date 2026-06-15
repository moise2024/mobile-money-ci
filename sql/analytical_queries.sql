-- ============================================================
-- REQUETES SQL ANALYTIQUES - Schema en etoile
-- ============================================================

-- REQUETE 1 : Volume par operateur
SELECT
    o.nom_operateur,
    COUNT(f.id_transaction)         AS nb_transactions,
    SUM(f.montant_fcfa)              AS volume_total_fcfa,
    ROUND(AVG(f.montant_fcfa))       AS montant_moyen_fcfa,
    SUM(f.frais_fcfa)                AS frais_totaux_fcfa
FROM  faits_transactions f
JOIN  dim_operateur o ON f.id_operateur = o.id_operateur
WHERE f.statut = 'Succes'
GROUP BY o.nom_operateur
ORDER BY volume_total_fcfa DESC;

-- REQUETE 2 : Tendances mensuelles
SELECT
    d.mois,
    d.nom_mois,
    COUNT(f.id_transaction)      AS nb_transactions,
    SUM(f.montant_fcfa)           AS volume_fcfa,
    ROUND(AVG(f.montant_fcfa))    AS montant_moyen,
    ROUND(100.0 * SUM(CASE WHEN f.statut='Succes' THEN 1 ELSE 0 END)
               / COUNT(*), 1)    AS taux_succes_pct
FROM  faits_transactions f
JOIN  dim_date d ON f.id_date = d.id_date
GROUP BY d.mois, d.nom_mois
ORDER BY d.mois;

-- REQUETE 3 : Volume par zone et type (jointure triple)
SELECT
    z.nom_zone,
    z.region,
    t.nom_type,
    COUNT(*)              AS nb_transactions,
    SUM(f.montant_fcfa)   AS volume_fcfa
FROM  faits_transactions f
JOIN  dim_zone            z ON f.id_zone_exp = z.id_zone
JOIN  dim_type_operation  t ON f.id_type     = t.id_type
WHERE f.statut = 'Succes'
  AND z.region = 'Abidjan'
GROUP BY z.nom_zone, z.region, t.nom_type, t.categorie
ORDER BY z.nom_zone, volume_fcfa DESC;

-- REQUETE 4 : Fonctions de fenetre (CTE + RANK + LAG)
WITH vol_mensuel AS (
    SELECT
        d.mois, d.nom_mois,
        o.nom_operateur,
        SUM(f.montant_fcfa) AS volume
    FROM  faits_transactions f
    JOIN  dim_date d        ON f.id_date      = d.id_date
    JOIN  dim_operateur o   ON f.id_operateur = o.id_operateur
    WHERE f.statut = 'Succes'
    GROUP BY d.mois, d.nom_mois, o.nom_operateur
)
SELECT
    mois, nom_mois, nom_operateur, volume,
    RANK() OVER (PARTITION BY mois ORDER BY volume DESC) AS rang,
    LAG(volume) OVER (PARTITION BY nom_operateur ORDER BY mois) AS vol_precedent,
    ROUND(100.0 * (volume - LAG(volume)
        OVER (PARTITION BY nom_operateur ORDER BY mois))
        / NULLIF(LAG(volume) OVER (PARTITION BY nom_operateur ORDER BY mois), 0), 1
    ) AS variation_pct
FROM  vol_mensuel
ORDER BY mois, rang;
