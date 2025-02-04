pipeline {
    agent any

    stages {
        stage('Clone Repository') {
            steps {
                git 'https://github.com/sloghult/Pronote_wish.git'
            }
        }

        stage('Set up Python Environment') {
            steps {
                sh 'python -m venv venv' // Créer un environnement virtuel
                sh 'source venv/bin/activate' // Activer l’environnement (Linux/Mac)
                sh 'pip install --upgrade pip' // Mettre à jour pip
                sh 'pip install -r requirements.txt' // Installer les dépendances
            }
        }

        stage('Security Scan') {
            steps {
                sh 'pip install pip-audit' // Installer pip-audit
                sh 'pip-audit --requirement requirements.txt --format=json > audit_report.json' // Scanner les vulnérabilités
            }
        }

        stage('Publish Report') {
            steps {
                publishHTML(target: [
                    allowMissing: false,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: '.',
                    reportFiles: 'audit_report.json',
                    reportName: 'Security Audit Report'
                ])
            }
        }
    }
}
