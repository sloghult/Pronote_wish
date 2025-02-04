pipeline {
    agent any
    
    environment {
        PYTHON_VERSION = '3.9'  // Ajustez selon votre version de Python
    }
    
    tools {
        // Assurez-vous que ces outils sont configurés dans Jenkins
        python 'Python-3.9'
    }
    
    stages {
        stage('Checkout') {
            steps {
                // Récupère le code source
                checkout scm
            }
        }
        
        stage('Setup Python Environment') {
            steps {
                script {
                    // Crée et active un environnement virtuel
                    sh '''
                        python -m venv venv
                        . venv/bin/activate
                        pip install -r Pronote_wish/requirements.txt
                    '''
                }
            }
        }
        
        stage('OWASP Dependency Check') {
            steps {
                script {
                    // Configure et exécute OWASP Dependency Check
                    dependencyCheck(
                        additionalArguments: """
                            --scan . 
                            --format 'HTML' 
                            --format 'XML' 
                            --enableExperimental 
                            --enableRetired
                            --enablePython
                            --failOnCVSS 7
                            --project 'Pronote_wish'
                            --log './dependency-check.log'
                        """,
                        odcInstallation: 'OWASP-Dependency-Check'
                    )
                    
                    // Publie les résultats
                    dependencyCheckPublisher(
                        pattern: 'dependency-check-report.xml',
                        failedTotalCritical: 1,
                        failedTotalHigh: 2,
                        failedTotalMedium: 5,
                        unstableTotalLow: 10
                    )
                }
            }
        }
    }
    
    post {
        always {
            // Nettoie l'environnement de travail
            cleanWs()
            
            // Archive les rapports
            archiveArtifacts artifacts: 'dependency-check-report.*', fingerprint: true
            
            // Envoie une notification par email
            emailext (
                subject: "Pipeline ${currentBuild.fullDisplayName} - ${currentBuild.currentResult}",
                body: """
                    Pipeline terminée avec le statut : ${currentBuild.currentResult}
                    
                    Consultez le rapport de sécurité pour plus de détails.
                    
                    ${env.BUILD_URL}
                """,
                recipientProviders: [[$class: 'DevelopersRecipientProvider']]
            )
        }
    }
}
