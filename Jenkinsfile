
pipeline {
    agent any

    stages {
        stage('Verify Tools') {
            steps {
                sh 'python3 --version'
                sh 'git --version'
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                    python3 -m venv .venv
                    .venv/bin/python -m pip install --upgrade pip
                    .venv/bin/python -m pip install -r requirements-dev.txt
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '.venv/bin/python -m pytest -v'
            }
        }
    }

    post {
        success {
            echo 'IIoT PLC Inspector CI pipeline completed successfully.'
        }

        failure {
            echo 'Pipeline failed. Check the stage logs for details.'
        }
    }
}
