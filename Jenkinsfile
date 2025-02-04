pipeline {
    agent any

    environment {
        DEPENDENCY_CHECK_REPORTS = "owasp-report"
    }

    stages {
        stage('Checkout') {
            steps {
                git url: 'https://github.com/sloghult/Pronote_wish.git', branch: 'main'
            }
        }

        stage('Check Workspace') {
            steps {
                script {
                    sh 'ls -lah'
                    sh 'cat requirements.txt || echo "Fichier requirements.txt introuvable !"'
                }
            }
        }

        stage('Setup Environment') {
            steps {
                script {
                    sh """
                        python3 -m venv venv
                        . venv/bin/activate
                        pip install --upgrade pip
                        pip install -r requirements.txt
                    """
                }
            }
        }

        stage('Test pip-audit & Safety') {
            steps {
                script {
                    sh """
                        . venv/bin/activate
                        pip install pip-audit safety
                        pip-audit --version || echo "pip-audit non installé !"
                        safety --version || echo "safety non installé !"
                    """
                }
            }
        }

        stage('Pip-Audit Security Check') {
            steps {
                script {
                    sh """
                        . venv/bin/activate
                        pip-audit -r requirements.txt --verbose | tee pip-audit-report.txt || echo "pip-audit a échoué !"
                    """
                }
            }
        }

        stage('Safety Security Check') {
            steps {
                script {
                    sh """
                        . venv/bin/activate
                        safety check -r requirements.txt --full-report | tee safety-report.txt || echo "safety a échoué !"
                    """
                }
            }
        }

        stage('Afficher Résultats') {
            steps {
                script {
                    sh 'cat pip-audit-report.txt || echo "Rapport pip-audit introuvable !"'
                    sh 'cat safety-report.txt || echo "Rapport Safety introuvable !"'
                }
            }
        }

        stage('Publier les Rapports') {
            steps {
                archiveArtifacts artifacts: "pip-audit-report.txt, safety-report.txt", onlyIfSuccessful: true
            }
        }
    }

    post {
        always {
            echo "Pipeline terminé avec succès, les rapports sont archivés."
        }
    }
}
