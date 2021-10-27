#!/bin/bash

# Build the app using sam and output yaml file


# The layer requires to be packaged up with a 'python' folder.
# sam build handles that for us. So we are going to use that
# to prep the layer artifacts and the lambda artifacts.


# Setup build output
buildDir=.build
tempLayerDir=$buildDir/layer

# Copy cloudwedge layer src to a temp folder, so we can get the
# layer with the 'cloudwedge' layer still intact
mkdir -p $tempLayerDir && cp -r app/src/cloudwedge $tempLayerDir

# The req file needs to be up 1 level
mv $tempLayerDir/cloudwedge/requirements.txt $tempLayerDir/
# touch $tempLayerDir/requirements.txt

# If a particular function was given as $1, just build that
# this is used in the package.json configurations to speed
# up running functions locally
if [ -n "$1" ]; then
    sam build $1 --template-file app/cloudwedge.yaml
# Build all the functions and layer from the yaml
# this is done when you need to build the real deal
else
    sam build --template-file app/cloudwedge.yaml
fi

# Clear out the build, we dont need it anymore
rm -rf $buildDir
