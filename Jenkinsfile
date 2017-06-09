#!/usr/bin/env groovy
import groovy.json.JsonOutput

/**
 * Main configuration for jenkins file pipeline
 */
config = [
        awsCredentialsId: "awspacker",
        gitCredentialsId: "awsjenkins_git",
        gitRepoUrl      : "ssh://git@github.com:gchiesa/base_ami.git",
        packerUrl       : "https://releases.hashicorp.com/packer/0.12.3/packer_0.12.3_linux_amd64.zip",
]

/**
 * Cascade jobs must be configured here
 */
cascadeJobs = [
        jobName: [
                repository      : "",
                gitCredentialsId: config.gitCredentialsId,
                projectPath: '.'
        ]
]

// global packer tool
String packer = ''
// packer project file
String packerProject = 'packer.json'
// new produced image
String newImage = ''

echo "Cascade: ${params.multiPacker}"
/**
 * PIPELINE
 */
currentBuild.result = 'SUCCESS'
node {
    // checkout code
    stage('Checkout Code') {
        checkout(changelog: false, poll: false,
                scm: [$class                           : 'GitSCM',
                      branches                         : [[name: '*/master']],
                      doGenerateSubmoduleConfigurations: false,
                      extensions                       : [],
                      submoduleCfg                     : [],
                      userRemoteConfigs                : [
                              [credentialsId: config.gitCredentialsId,
                               url          : config.gitRepoUrl]
                      ]
                ])
    }

    // verify or install packer
    stage('Packer Installation') {
        if (sh(returnStatus: true, script: "which packer") != 0) {
            String packer_path = '_SCRATCH/packer'
            if (!fileExists(packer_path)) {
                sh 'mkdir -p _SCRATCH/'
                sh "curl -o _SCRATCH/packer.zip ${config.packerUrl}"
                sh 'unzip _SCRATCH/packer.zip -d _SCRATCH'
                sh 'chmod +x _SCRATCH/packer'
                echo "Downloaded packer"
            } else {
                echo "Packer already downloaded in: ${packer_path}"
            }
            packer = env.WORKSPACE + '/' + packer_path
            echo "Packer available at: ${packer}"
        } else {
            packer = sh(returnStdout: true, script: "which packer")
            echo "Packer available at system level here: ${packer}"
        }
    }

    // test the project file
    stage("Testing: ${params.projectPath}") {
        dir(params.projectPath) {
            echo "packer binary: ${packer}"
            echo "packer file is: ${packerProject}"
            echo "base ami is: ${params.baseImage}"
            withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', accessKeyVariable: 'AWS_ACCESS_KEY_ID', credentialsId: config.awsCredentialsId, secretKeyVariable: 'AWS_SECRET_ACCESS_KEY']]) {
                withEnv(["ENV_PACKER=${packer}", "ENV_PACKER_PROJECT=${packerProject}", "ENV_BASE_IMAGE=${params.baseImage}"]) {
                    retcode = sh(returnStatus: true, script: "./_mob_ci/scripts/test.sh")
                    echo "script return code: ${retcode}"
                }
            }
        }
        sh("exit ${retcode}")
    }

    // build the image
    stage("Building : ${params.projectPath}") {
        dir(params.projectPath) {
            echo "packer binary: ${packer}"
            echo "packer file is ${packerProject}"
            echo "base ami is: ${params.baseImage}"
            withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', accessKeyVariable: 'AWS_ACCESS_KEY_ID', credentialsId: config.awsCredentialsId, secretKeyVariable: 'AWS_SECRET_ACCESS_KEY']]) {
                withEnv(["ENV_PACKER=${packer}", "ENV_PACKER_PROJECT=${packerProject}", "ENV_BASE_IMAGE=${params.baseImage}"]) {
                    sh(returnStatus: true, script: "./_mob_ci/scripts/build.sh 2>&1| tee packer_output.txt")
                    newImage = sh(returnStdout: true, script: "tail -2 packer_output.txt | head -2 | awk 'match(\$0, /ami-.*/) { print substr(\$0, RSTART, RLENGTH) }'")
                    echo "PRODUCED AMI ID: ${newImage}"
                    if(newImage == '') {
                        sh("exit 1")
                    }
                }
            }
        }
    }

    /*
     * if it's a cascade image stage here we check the image map and we generate the other pipelines
     */
    if (params.multiPacker == true) {
        stage("Generating depending pipelines") {
            // save the cascade jobs in a json map
            String json_data = new JsonOutput().toJson(cascadeJobs)
            writeFile(file: '_SCRATCH/cascade_jobs.json', text: json_data)
            // trigger the dsl job plugin
            jobDsl(failOnMissingPlugin: true, removedJobAction: 'DELETE', removedViewAction: 'DELETE', targets: "${params.projectPath}/_mob_ci/jenkins/jobDsl.groovy")
        }
    }

    if (params.multiPacker == true) {
        stage("Triggering depending pipelines") {
            // prepare the cascade job map
            LinkedHashMap cascadeJobsPipeline = prepareCascadeJobs(newImage)
            parallel(cascadeJobsPipeline)
            return
        }
    }
}

/**
 * calculate the cascade jobs
 */
@NonCPS
LinkedHashMap prepareCascadeJobs(String newImage) {
    LinkedHashMap cascadeJobsPipeline = [:]
    cascadeJobs.each { jobName, jobInfo ->
        cascadeJobsPipeline.put(jobName, {
            node {
                build(job: jobName, parameters: [string(name: 'baseImage', value: newImage)], quietPeriod: 5, wait: false)
            }
        })
    }
    return cascadeJobsPipeline
}
