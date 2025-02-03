USE pronote1;

-- Ajouter la colonne pour le statut d'autorisation
ALTER TABLE absences 
ADD COLUMN statut_autorisation ENUM('autorisee', 'non_autorisee') DEFAULT 'non_autorisee';
