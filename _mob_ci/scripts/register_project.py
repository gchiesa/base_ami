#!/usr/bin/env python

"""register a project on Jenkins"""
import sys
import os
import argparse
import logging
import getpass
import json

__author__ = "Giuseppe Chiesa"
__copyright__ = "Copyright 2017, Mobiquity Inc."
__credits__ = ["Giuseppe Chiesa"]
__license__ = "BSD"
__version__ = "0.0.1"
__maintainer__ = "Giuseppe Chiesa"
__email__ = "gchiesa@mobiquityinc.com"
__status__ = "Beta"

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__file__)

CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(CURRENT_PATH.rpartition('/')[0], 'lib', 'modules'))

import jenkins


def get_arguments():
    parser = argparse.ArgumentParser(description="Register a project into jenkins")
    parser.add_argument('-u', '--user',
                        dest='username',
                        help='Username to authenticate in jenkins',
                        required=True)
    parser.add_argument('-j', '--jenkins',
                        dest='jenkins_uri',
                        help='Jenkins server uri',
                        required=True),
    parser.add_argument('-r', '--reconfig',
                        dest='reconfig',
                        action='store_true',
                        help='reconfigure the job',
                        default=False)
    parser.add_argument('-l', '--log-level',
                        help='Set log level',
                        dest='log_level',
                        default='INFO')
    return parser.parse_args()


def set_logging(log_level):
    logging.basicConfig(level=logging.getLevelName(log_level))


def create_project(server, project_name, configxml_data, reconfig=False):
    logger = logging.getLogger(__name__)
    try:
        if server.job_exists(project_name) and not reconfig:
            logger.warn('job with name: {n} already exists on Jenkins. Not creating it'.format(n=project_name))
        elif server.job_exists(project_name) and reconfig:
            logger.warn('job with name: {n} already exists. Reconfiguring it'.format(n=project_name))
            server.reconfig_job(project_name, configxml_data)
        else:
            logger.info('creating job with name: {n}'.format(n=project_name))
            server.create_job(project_name, configxml_data)
    except jenkins.JenkinsException as e:
        logger.error('Error while creating/updating job on jenkins. Error is: {e}'.format(e=str(e)))
        return False
    except Exception as e:
        logger.error('Exception while creating job in jenkins. Type: {t}. Error is: {e}'
                     ''.format(t=str(e.__class__.__name__), e=str(e)))
        return False
    return True


def main():
    args = get_arguments()
    set_logging(args.log_level)
    logger = logging.getLogger(__name__)
    metadata_file = os.path.join(CURRENT_PATH.rpartition('/')[0], 'metadata', 'cookiecutter.json')
    configxml_file = os.path.join(CURRENT_PATH.rpartition('/')[0], 'jenkins', 'job_config.xml')
    logger.info('Loading metadata from {metadata}'.format(metadata=metadata_file))

    with open(metadata_file) as fp:
        metadata = json.loads(fp.read())

    password = getpass.getpass('Jenkins password: ')

    server = jenkins.Jenkins(args.jenkins_uri, username=args.username, password=password)
    user = server.get_whoami()
    logger.info('Connected as user: {u}'.format(u=user['fullName']))
    try:
        version = server.get_version()
        logger.info('Jenkins version: {v}'.format(u=user, v=version))
    except jenkins.BadHTTPException:
        pass

    project_name = 'packer_{image_name}'.format(image_name=metadata['image_name'])
    with open(configxml_file) as fp:
        configxml_data = fp.read()

    if not create_project(server, project_name, configxml_data, reconfig=args.reconfig):
        logger.error('Error creating the project. Exiting.')
        sys.exit(1)
    logger.info('Project created successfully')


if __name__ == '__main__':
    main()
