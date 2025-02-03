import mysql.connector
from werkzeug.security import generate_password_hash

# Connexion à la base de données
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="pronote1"
)

cursor = db.cursor(dictionary=True)

# Mot de passe à hasher (le même pour tous les utilisateurs pour le test)
password = "test123"
hashed_password = generate_password_hash(password)

# Mettre à jour le mot de passe de l'admin
cursor.execute("""
    UPDATE users 
    SET password = %s,
        role = 'admin'
    WHERE username = 'admin'
""", (hashed_password,))

# Mettre à jour le mot de passe du prof
cursor.execute("""
    UPDATE users 
    SET password = %s,
        role = 'prof'
    WHERE username = 'prof1'
""", (hashed_password,))

# Valider les changements
db.commit()

# Vérifier les mises à jour
cursor.execute("SELECT id, username, password, role FROM users")
users = cursor.fetchall()
print("\nUtilisateurs mis à jour :")
for user in users:
    print(f"ID: {user['id']}, Username: {user['username']}, Role: {user['role']}")

cursor.close()
db.close()

print("\nMot de passe mis à jour pour tous les utilisateurs :")
print(f"Username: admin ou prof1")
print(f"Password: {password}")
