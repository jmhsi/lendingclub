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
            sh 'echo "Hi from master."'
          }
        }
        stage('concurrent_to_download_data') {
          steps {
            echo 'hi again from master'
          }
        }
      }
    }
    stage('after CDD') {
      steps {
        sh 'hi a third time from master'
      }
    }
  }
}
