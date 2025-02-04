pipeline {
    agent any

    environment {
        DEPENDENCY_CHECK_VERSION = "latest" // Vous pouvez spécifier une version précise
        DEPENDENCY_CHECK_REPORTS = "owasp-report"
    }

    stages {
        stage('Checkout') {
            steps {
                git url: 'https://github.com/votre-utilisateur/votre-repo.git', branch: 'main'
            }
        }

        stage('Setup Environment') {
            steps {
                script {
                    // Création d'un environnement virtuel et installation des dépendances
                    sh 'python3 -m venv venv'
                    sh 'source venv/bin/activate && pip install -r requirements.txt'
                }
            }
        }

        stage('OWASP Dependency Check') {
            steps {
                script {
                    sh """
                        dependency-check.sh --project FlaskApp \
                        --scan . \
                        --format HTML \
                        --out ${DEPENDENCY_CHECK_REPORTS}
                    """
                }
            }
        }

        stage('Publish OWASP Report') {
            steps {
                publishHTML(target: [
                    allowMissing: false,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: "${DEPENDENCY_CHECK_REPORTS}",
                    reportFiles: "dependency-check-report.html",
                    reportName: "OWASP Dependency Check Report"
                ])
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: "${DEPENDENCY_CHECK_REPORTS}/dependency-check-report.html", onlyIfSuccessful: true
        }
    }
}
