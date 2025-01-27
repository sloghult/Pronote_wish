from app import create_app  # Importer l'application depuis __init__.py

app = create_app()  # Créer l'application

if __name__ == '__main__':
    app.run(debug=True)  # Lancer le serveur Flask
