pipeline {
  agent {
    docker {
      image 'joyzoursky/python-chromedriver'
    }

  }
  stages {
    stage('Check Download Data') {
      parallel {
        stage('Check Download Data') {
          steps {
            sh 'echo "I checked for new data"'
          }
        }
        stage('concurrent_to_download_data') {
          steps {
            echo 'doing stage concurrent to "Check Download Data" from print message in BO'
          }
        }
      }
    }
    stage('after CDD') {
      steps {
        sh 'echo doing something'
      }
    }
  }
}