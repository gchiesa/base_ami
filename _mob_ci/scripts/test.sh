#!/usr/bin/env bash
set -e

# load the .aws profile exporting the variables to connect to aws
load_profile() {
    if [ -z "$1" ]; then
        echo "You must specify a profile or export AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY"
        exit 1
    fi
    local cred=($(grep -A2 -e "\[$1\]" ~/.aws/credentials))
    local key=${cred[1]}
    local secret=${cred[2]}
    export AWS_ACCESS_KEY_ID=${key#*=}
    export AWS_SECRET_ACCESS_KEY=${secret#*=}
}

# move to base folder
cd $(dirname $0)/../..

if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
    load_profile $1
fi

PACKER="packer"
[ ! -z "$ENV_PACKER" ] && PACKER="$ENV_PACKER"

PACKER_PROJECT="packer.json"
[ ! -z "$ENV_PACKER_PROJECT" ] && PACKER_PROJECT="$ENV_PACKER_PROJECT"

PACKER_BASE=''
[ ! -z "$ENV_BASE_IMAGE" ] && PACKER_BASE="-var base_image=$ENV_BASE_IMAGE"

set -x
${PACKER} validate -var-file variables.json \
    ${PACKER_BASE} \
    ${PACKER_PROJECT}
set +x
