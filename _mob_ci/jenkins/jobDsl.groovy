#!/usr/bin/env groovy
import groovy.json.JsonSlurperClassic

// read the temporary map file
String jsonData = readFileFromWorkspace('_SCRATCH/cascade_jobs.json')
def jobMap = new JsonSlurperClassic().parseText(jsonData)

String defaultBaseImage = 'ami-70edb016'

// for each job tuple it will create a new pipeline on jenkins
jobMap.each { jobName, jobInfo ->
    pipelineJob(jobName) {
        concurrentBuild(false)
        definition {
            cpsScm {
                scm {
                    git {
                        remote {
                            url(jobInfo.repository)
                            credentials(jobInfo.gitCredentialsId)
                        }
                    }
                }
                scriptPath(jobInfo.projectPath + '/Jenkinsfile')
            }
        }
        parameters {
            persistentStringParameterDefinition {
                name('projectPath')
                defaultValue(jobInfo.projectPath)
                successfulOnly(true)
                description('Path in the repository where the project is')
            }
            persistentStringParameterDefinition {
                name('baseImage')
                defaultValue(defaultBaseImage)
                successfulOnly(true)
                description('Base AMI')
            }
            persistentBooleanParameterDefinition {
                name('multiPacker')
                defaultValue(false)
                successfulOnly(true)
                description('Select if the job needs to build cascade jobs')
            }
        }
    }
}
