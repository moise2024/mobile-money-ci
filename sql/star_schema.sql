-- ============================================================
-- SCHEMA EN ETOILE - Mobile Money CI
-- Dimensions + Table de faits
-- ============================================================

-- DIMENSION 1 : Operateur
CREATE TABLE IF NOT EXISTS dim_operateur (
    id_operateur   SERIAL PRIMARY KEY,
    nom_operateur  TEXT NOT NULL UNIQUE,
    type_operateur TEXT,
    actif          BOOLEAN DEFAULT TRUE
);

-- DIMENSION 2 : Zone
CREATE TABLE IF NOT EXISTS dim_zone (
    id_zone    SERIAL PRIMARY KEY,
    nom_zone   TEXT NOT NULL UNIQUE,
    region     TEXT,
    type_zone  TEXT,
    population INTEGER
);

-- DIMENSION 3 : Type d'operation
CREATE TABLE IF NOT EXISTS dim_type_operation (
    id_type        SERIAL PRIMARY KEY,
    nom_type       TEXT NOT NULL UNIQUE,
    categorie      TEXT,
    taux_frais_max NUMERIC(4,2)
);

-- DIMENSION 4 : Calendrier
CREATE TABLE IF NOT EXISTS dim_date (
    id_date       SERIAL PRIMARY KEY,
    date_complete DATE NOT NULL UNIQUE,
    annee         INTEGER,
    mois          INTEGER,
    nom_mois      TEXT,
    trimestre     INTEGER,
    semaine       INTEGER,
    jour          INTEGER,
    nom_jour      TEXT,
    est_weekend   BOOLEAN
);

-- TABLE DE FAITS
CREATE TABLE IF NOT EXISTS faits_transactions (
    id_transaction    TEXT PRIMARY KEY,
    id_operateur      INTEGER REFERENCES dim_operateur(id_operateur),
    id_zone_exp       INTEGER REFERENCES dim_zone(id_zone),
    id_zone_ben       INTEGER REFERENCES dim_zone(id_zone),
    id_type           INTEGER REFERENCES dim_type_operation(id_type),
    id_date           INTEGER REFERENCES dim_date(id_date),
    montant_fcfa      BIGINT NOT NULL,
    frais_fcfa        INTEGER DEFAULT 0,
    montant_net_fcfa  BIGINT,
    taux_frais_pct    NUMERIC(5,2),
    heure             INTEGER,
    statut            TEXT,
    inter_ville       INTEGER DEFAULT 0,
    id_agent          TEXT
);
