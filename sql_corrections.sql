-- Corrections et améliorations du schéma de base de données
-- À exécuter pour corriger les erreurs dans les tables existantes

-- 1. Corriger la table materiel_physique (enlever la virgule finale)
DROP TABLE IF EXISTS materiel_physique;
CREATE TABLE materiel_physique (
    id_physique INT AUTO_INCREMENT PRIMARY KEY,
    code_localisation_ref INT NOT NULL,
    nom_materiel VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL,
    FOREIGN KEY (code_localisation_ref) REFERENCES localisation(code_localisation)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Corriger la table incident (id_incident manquait un espace)
DROP TABLE IF EXISTS incident;
CREATE TABLE incident (
    id_incident INT AUTO_INCREMENT PRIMARY KEY,
    motif VARCHAR(200),
    compatibilite_consommable VARCHAR(100),
    achat_consommable VARCHAR(100),
    id_materiel INT,
    FOREIGN KEY (id_materiel) REFERENCES materiel_informatique(id_snapshot) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Ajouter des index pour optimiser les performances
ALTER TABLE materiel_informatique ADD INDEX idx_id_physique (id_physique);
ALTER TABLE materiel_informatique ADD INDEX idx_id_date_import (id_date_import);
ALTER TABLE materiel_informatique ADD INDEX idx_etat (etat);

ALTER TABLE materiel_physique ADD INDEX idx_code_localisation (code_localisation_ref);
ALTER TABLE materiel_physique ADD INDEX idx_type (type);

ALTER TABLE localisation ADD INDEX idx_code (code);
ALTER TABLE localisation ADD INDEX idx_region (region);
ALTER TABLE localisation ADD INDEX idx_district (district);
ALTER TABLE localisation ADD INDEX idx_commune (commune);

-- 4. Ajouter des contraintes d'intégrité supplémentaires
ALTER TABLE users ADD CONSTRAINT unique_mail UNIQUE (mail);

-- 5. Script complet de création (si besoin de tout recréer)
-- Décommenter si vous partez de zéro

/*
DROP DATABASE IF EXISTS trait8;
CREATE DATABASE trait8 CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE trait8;

CREATE TABLE localisation (
    code_localisation INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(50), 
    region VARCHAR(100),
    district VARCHAR(100),
    commune VARCHAR(100),
    INDEX idx_code (code),
    INDEX idx_region (region),
    INDEX idx_district (district),
    INDEX idx_commune (commune)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE date_import (
    id_date INT AUTO_INCREMENT PRIMARY KEY,
    date_complet DATE DEFAULT (CURRENT_DATE)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE materiel_physique (
    id_physique INT AUTO_INCREMENT PRIMARY KEY,
    code_localisation_ref INT NOT NULL,
    nom_materiel VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL,
    FOREIGN KEY (code_localisation_ref) REFERENCES localisation(code_localisation),
    INDEX idx_code_localisation (code_localisation_ref),
    INDEX idx_type (type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE materiel_informatique (
    id_snapshot INT AUTO_INCREMENT PRIMARY KEY,
    id_physique INT NOT NULL,
    etat VARCHAR(50),
    id_date_import INT NOT NULL,
    FOREIGN KEY (id_physique) REFERENCES materiel_physique(id_physique),
    FOREIGN KEY (id_date_import) REFERENCES date_import(id_date),
    INDEX idx_id_physique (id_physique),
    INDEX idx_id_date_import (id_date_import),
    INDEX idx_etat (etat)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE incident (
    id_incident INT AUTO_INCREMENT PRIMARY KEY,
    motif VARCHAR(200),
    compatibilite_consommable VARCHAR(100),
    achat_consommable VARCHAR(100),
    id_materiel INT,
    FOREIGN KEY (id_materiel) REFERENCES materiel_informatique(id_snapshot) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    mail VARCHAR(255) NOT NULL UNIQUE,
    mot_de_passe VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE upload_history (
    id_upload INT AUTO_INCREMENT PRIMARY KEY,
    filename VARCHAR(255),
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
*/