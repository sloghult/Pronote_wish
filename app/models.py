class Student:
    def __init__(self, id, nom, prenom, notes_matiere1, notes_matiere2, notes_matiere3, notes_matiere4, notes_matiere5):
        self.id = id
        self.nom = nom
        self.prenom = prenom
        self.notes_matiere1 = notes_matiere1
        self.notes_matiere2 = notes_matiere2
        self.notes_matiere3 = notes_matiere3
        self.notes_matiere4 = notes_matiere4
        self.notes_matiere5 = notes_matiere5

students = [
    Student(1, "Dupont", "Jean", 12, 15, 14, 13, 16),
    Student(2, "Martin", "Marie", 14, 13, 15, 12, 10),
    Student(3, "Durand", "Paul", 17, 16, 14, 18, 19)
]
