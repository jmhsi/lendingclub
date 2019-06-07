pipeline {
  agent {
    docker { image 'joyzoursky/python-chromedriver:3.7-selenium'}
  }
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
      agent {
        docker {
          image 'joyzoursky/python-chromedriver'
        }

      }
      when {
        branch 'csv_dl_preparation'
      }
      steps {
        echo 'hi from only csv_dl_preparation'
        sh 'python scripts/csv_dl_preparation/download_and_check_csvs.py'
      }
    }
  }
  environment {
    CI = 'true'
  }
}