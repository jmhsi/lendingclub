pipeline {
  agent any 
  environment {
    CI = 'true'
  }  
  stages {
    stage('Run every time?') {
      steps {
        echo 'hi from every branch, not in a container.'
      }
    }
    stage('Check Download Data') {
      /*
      agent {
        docker {
          image 'joyzoursky/python-chromedriver'
        }
      */
      when {
        branch 'csv_dl_preparation'
      }
      steps {
        // echo 'hi from only csv_dl_preparation'
        // echo 'problem with import pause'
        // sh 'export PYTHONPATH=$WORKSPACE:$PYTHONPATH'
        // sh '$PATH'
        // sh 'pip install -r requirements.txt'
        // sh 'python scripts/csv_dl_preparation/download_and_check_csvs.py'
        sh 'python --version'
        sh 'which python'
        sh 'python hello_world.py'
      }
    }
  }
}