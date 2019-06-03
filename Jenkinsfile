pipeline {
  agent {
    docker {
      image 'joyzoursky/python-chromedriver'
    }
  }
  environment {
    CI = 'true'
  }  
  stages {
    stage('Run every time?') {
      steps {
        echo 'hi from every branch'
      }
    }
    stage('Check Download Data') {
      when {
        branch 'csv_dl_preparation'
      }
      steps {
        echo 'hi from only csv_dl_prep'
        pwd
        ls
      }
    }
  }
}