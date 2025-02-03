USE pronote;

-- Ajouter les colonnes pour la justification
ALTER TABLE absences 
ADD COLUMN justification TEXT,
ADD COLUMN justification_status ENUM('en_attente', 'acceptee', 'refusee') DEFAULT NULL;
