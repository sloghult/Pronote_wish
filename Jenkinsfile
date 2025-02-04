pipeline {
    agent any

    environment {
        DEPENDENCY_CHECK_VERSION = "latest"
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
                    sh 'ls -l requirements.txt || echo "requirements.txt not found!"'
                }
            }
        }

        stage('OWASP Dependency Check') {
            steps {
                script {
                    sh """
                        dependency-check.sh --project FlaskApp \
                        --scan requirements.txt \
                        --enableExperimental \
                        --format HTML \
                        --out ${DEPENDENCY_CHECK_REPORTS} \
                        -l debug
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
