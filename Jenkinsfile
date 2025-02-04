pipeline {
    agent any

    environment {
        REPORTS_DIR = "security-reports"
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
                    // Vérification de l'existence du fichier requirements.txt
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

        stage('Install Security Tools') {
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
                        mkdir -p ${REPORTS_DIR}
                        pip-audit -r requirements.txt --format=json > ${REPORTS_DIR}/pip-audit-report.json || echo "pip-audit a échoué !"
                    """
                }
            }
        }

        stage('Safety Security Check') {
            steps {
                script {
                    sh """
                        . venv/bin/activate
                        mkdir -p ${REPORTS_DIR}
                        safety check -r requirements.txt --json > ${REPORTS_DIR}/safety-report.json || echo "safety a échoué !"
                    """
                }
            }
        }

        stage('Afficher Résultats') {
            steps {
                script {
                    // Vérifie si les rapports ont bien été générés
                    sh 'ls -lah ${REPORTS_DIR} || echo "Le répertoire des rapports est vide ou introuvable."'
                    sh 'cat ${REPORTS_DIR}/pip-audit-report.json || echo "Rapport pip-audit introuvable !"'
                    sh 'cat ${REPORTS_DIR}/safety-report.json || echo "Rapport Safety introuvable !"'
                }
            }
        }

        stage('Publier les Rapports') {
            steps {
                script {
                    // Archive les rapports JSON générés
                    sh 'ls -lah ${REPORTS_DIR} || echo "Le répertoire des rapports est vide."'
                    archiveArtifacts artifacts: "${REPORTS_DIR}/**/*.json", allowEmptyArchive: true
                }
            }
        }
    }

    post {
        always {
            // Vérifier les fichiers générés dans le répertoire de rapports
            echo "Vérification des fichiers générés dans ${REPORTS_DIR}"
            sh "ls -lah ${REPORTS_DIR}"
        }
    }
}
