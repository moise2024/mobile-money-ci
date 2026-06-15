-- ============================================================
-- CREATION DES TABLES (OLTP) - Supabase SQL Editor
-- ============================================================

CREATE TABLE IF NOT EXISTS transactions (
    id_transaction     TEXT PRIMARY KEY,
    date_heure         TIMESTAMP,
    operateur          TEXT NOT NULL,
    type_operation     TEXT NOT NULL,
    expediteur         TEXT,
    beneficiaire       TEXT,
    montant_fcfa       BIGINT,
    frais_fcfa         INTEGER DEFAULT 0,
    montant_net_fcfa   BIGINT,
    taux_frais_pct     NUMERIC(5,2),
    zone_expediteur    TEXT,
    zone_beneficiaire  TEXT,
    id_agent           TEXT,
    statut             TEXT,
    heure              INTEGER,
    jour_semaine       TEXT,
    mois               TEXT,
    categorie_montant  TEXT,
    tranche_horaire    TEXT,
    inter_ville        INTEGER
);

CREATE TABLE IF NOT EXISTS agg_operateur (
    operateur         TEXT PRIMARY KEY,
    nb_transactions   INTEGER,
    volume_fcfa       BIGINT,
    montant_moyen     BIGINT,
    montant_median    BIGINT,
    frais_total       BIGINT,
    part_volume_pct   NUMERIC(5,1)
);

CREATE TABLE IF NOT EXISTS agg_type_operation (
    type_operation  TEXT PRIMARY KEY,
    nb              INTEGER,
    volume          BIGINT,
    moy             BIGINT,
    taux_frais      NUMERIC(5,2)
);

CREATE TABLE IF NOT EXISTS agg_zone (
    zone           TEXT PRIMARY KEY,
    volume_fcfa    BIGINT,
    part_pct       NUMERIC(5,1)
);
