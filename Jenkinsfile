pipeline {
  agent none 
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
      when {
        branch 'csv_dl_preparation'
      }
      agent {
        docker {  image 'joyzoursky/python-chromedriver'  }
      }
      steps {
        echo 'hi from only csv_dl_preparation'
        sh 'pwd'
        sh 'python scripts/csv_dl_preparation/download_and_check_csvs.py'
      }
    }
  }
}