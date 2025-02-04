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

        stage('Setup Environment') {
            steps {
                script {
                    sh 'python3 -m venv venv'
                    sh 'source venv/bin/activate && pip install -r requirements.txt'
                }
            }
        }

        stage('Verify Dependencies') {
            steps {
                script {
                    sh 'source venv/bin/activate && pip list'
                }
            }
        }

        stage('Pip-Audit Security Check') {
            steps {
                script {
                    sh 'source venv/bin/activate && pip install pip-audit && pip-audit > pip-audit-report.txt'
                }
            }
        }

        stage('Safety Security Check') {
            steps {
                script {
                    sh 'source venv/bin/activate && pip install safety && safety check -r requirements.txt --full-report > safety-report.txt'
                }
            }
        }

        stage('Publish Security Reports') {
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
