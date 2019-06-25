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

        stage('Run code for csv_dl_archiving') {
            when {
                branch 'csv_dl_archiving'
            }
            steps {
                echo 'Build venv for csv_dl_archiving'
                sh  ''' python --version
                        conda create --yes -n ${BUILD_TAG} python
                        source activate ${BUILD_TAG}
                        cp -r /home/justin/projects/lendingclub/user_creds .
                        pip install -r requirements/csv_dl_archiving.txt
                        cd scripts/csv_dl_archiving
                        python -u download_and_check_csvs.py
                    '''
            }
        }
        stage('Run code for csv_preparation') {
            when {
                branch 'csv_preparation'
            }
            steps {
                echo 'Build venv for csv_preparation'
                sh  ''' python --version
                        conda create --yes -n ${BUILD_TAG} python
                        source activate ${BUILD_TAG}
                        pip install -r requirements/csv_preparation.txt
                        cd scripts/csv_preparation
                        # python -u unzip_csvs.py
                        # python -u merge_loan_info.py
                        # python -u clean_pmt_history_1.py 
                        # python -u clean_pmt_history_2.py 
                        # python -u clean_pmt_history_3.py 
                        python -u setup.py build_ext --inplace
                        # move the .so file to current dir (scripts)
                        find . -name "*.so" -exec mv {} . \\;
                        python -u clean_loan_info.py
                    '''
                        // cp -r /home/justin/projects/lendingclub/user_creds .
            }
        }
    }
    post {
        always {
            sh 'conda remove --yes -n ${BUILD_TAG} --all'
        }
    }
}
