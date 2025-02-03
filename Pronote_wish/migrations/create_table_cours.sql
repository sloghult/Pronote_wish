CREATE TABLE IF NOT EXISTS cours (
    id INT AUTO_INCREMENT PRIMARY KEY,
    professeur_id INT NOT NULL,
    classe_id INT NOT NULL,
    matiere_id INT NOT NULL,
    jour_semaine ENUM('Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi') NOT NULL,
    creneau VARCHAR(10) NOT NULL,
    FOREIGN KEY (professeur_id) REFERENCES prof(id) ON DELETE CASCADE,
    FOREIGN KEY (classe_id) REFERENCES classes(id) ON DELETE CASCADE,
    FOREIGN KEY (matiere_id) REFERENCES matieres(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
