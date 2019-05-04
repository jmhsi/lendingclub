pipeline {
  agent {
    docker {
      image 'joyzoursky/python-chromedriver'
    }

  }
  stages {
    stage('Check Download Data') {
      steps {
        sh 'echo "I checked for new data"'
      }
    }
  }
}