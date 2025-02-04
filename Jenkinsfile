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

        stage('Generate Dependency List') {
            steps {
                script {
                    sh 'source venv/bin/activate && pip freeze > dependencies.txt'
                }
            }
        }

        stage('Verify Dependencies') {
            steps {
                script {
                    sh 'ls -l dependencies.txt || echo "dependencies.txt not found!"'
                }
            }
        }

        stage('OWASP Dependency Check') {
            steps {
                script {
                    sh """
                        dependency-check.sh --project FlaskApp \
                        --scan dependencies.txt \
                        --enableExperimental \
                        --format HTML \
                        --out ${DEPENDENCY_CHECK_REPORTS} \
                        -l debug
                    """
                }
            }
        }

        stage('Python Safety Check') {
            steps {
                script {
                    sh 'source venv/bin/activate && pip install safety && safety check -r requirements.txt --full-report > safety-report.txt'
                }
            }
        }

        stage('Publish Reports') {
            steps {
                publishHTML(target: [
                    allowMissing: false,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: "${DEPENDENCY_CHECK_REPORTS}",
                    reportFiles: "dependency-check-report.html",
                    reportName: "OWASP Dependency Check Report"
                ])
                archiveArtifacts artifacts: "safety-report.txt", onlyIfSuccessful: true
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: "${DEPENDENCY_CHECK_REPORTS}/dependency-check-report.html", onlyIfSuccessful: true
        }
    }
}
