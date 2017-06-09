# base_ami
Base AMI Packer Image

## Requirements
Please check the files under ```resources/requirements.*``` to gather all the 3rd party component
used by the image

## Jenkins automatic job creation
If you want to automatically provision the project on Jenkins, you can run 
```bash
_mob_ci/scripts/register_project.py --help
```

## Usage
- Use the ```variables.json``` to override the defaults in ```packer.json```
- Use the ```_mob_ci/scripts/*``` helpers to test/build the code

## Notes
* In order to build in a unattended way you may need to export the __AWS_ACCESS_KEY_ID__ 
and __AWS_SECRET_ACCESS_KEY__
* If you want to base your build on a prexisting ami you can export the environment var __ENV_BASE_IMAGE__

## Supported variable overrides
these environment variables can be set to change the default behaviour:

* __ENV_PACKER__ : overrides the packer tool to use
* __ENV_PACKER_PROJECT__ : overrides the default name for the packer project file

When no environment variables are set, the ```_mob_ci/scripts/*``` will try to lookup the credentials
using profile name. You can pass the profile name to each script as 1st argument.

eg. 

    ./_mob_ci_scripts/build.sh devops

# Author
Giuseppe Chiesa <mailto:gchiesa@mobiquityinc.com>
