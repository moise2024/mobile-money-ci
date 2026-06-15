-- Modèle dbt : performances des opérateurs par mois
SELECT
    o.nom_operateur,
    d.annee,
    d.mois,
    d.nom_mois,
    COUNT(f.id_transaction)                          AS nb_transactions,
    SUM(f.montant_fcfa)                              AS volume_fcfa,
    ROUND(AVG(f.montant_fcfa))                       AS montant_moyen,
    ROUND(100.0 * SUM(CASE WHEN f.statut = 'Succes'
        THEN 1 ELSE 0 END) / COUNT(*), 1)            AS taux_succes_pct
FROM  faits_transactions f
JOIN  dim_operateur  o ON f.id_operateur = o.id_operateur
JOIN  dim_date       d ON f.id_date      = d.id_date
GROUP BY o.nom_operateur, d.annee, d.mois, d.nom_mois
ORDER BY d.annee, d.mois, volume_fcfa DESC
