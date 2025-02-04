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
                sh 'python -m venv venv' // Create a virtual environment
                sh 'source venv/bin/activate' // Activate the environment (Linux/Mac)
                sh 'pip install --upgrade pip' // Upgrade pip
                sh 'pip install -r requirements.txt' // Install dependencies
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                source venv/bin/activate
                pytest --junitxml=test-results.xml || true
                '''
            }
            post {
                always {
                    junit 'test-results.xml' // Publish the test results
                }
            }
        }

        stage('Security Scan') {
            steps {
                sh 'pip install pip-audit' // Install pip-audit
                sh 'pip-audit --requirement requirements.txt --format=json > audit_report.json' // Scan for vulnerabilities
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
