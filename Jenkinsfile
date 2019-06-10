pipeline {
    agent any
    options {
        skipDefaultCheckout(true)
        // Keep the 10 most recent builds
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timestamps()
    }
    environment {
      PATH="/var/lib/jenkins/miniconda3/bin:$PATH"
    }
    stages {

        stage('Code pull') {
            steps {
                checkout scm 
            }
        }

        stage('Build for csv_dl_archiving') {
            when {
                branch 'csv_dl_archiving'
            }
            steps {
                echo 'Build venv for csv_dl_archiving'
                sh  ''' python --version
                        conda create --yes -n ${BUILD_TAG} python
                        source activate ${BUILD_TAG}
                        cp -r /home/justin/projects/lendingclub/user_creds .
                        pip install -r requirements.txt
                        cd scripts/csv_dl_archiving
                        python download_and_check_csvs.py
                    '''

                       // python test_mkdirs.py
            }
        }
    }
    post {
        always {
            sh 'conda remove --yes -n ${BUILD_TAG} --all'
        }
    }
}
