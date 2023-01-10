#!/bin/bash

rm -rf _site
if [ $1 == "local" ]; then
    echo "Building for local deployment"
    cp _config_local.yml _config.yml
elif [ $1 == "cse" ]; then
    echo "Building for CSE deployment"
    cp _config_cse.yml _config.yml
else
    echo "Building for github deployment"
    cp _config_github.yml _config.yml
fi

bundle exec jekyll build

cd _site/
dist=./d.txt

if [ ! -e "$dist" ]; then
    touch $dist
    chmod 666 $dist
    echo "0" >> $dist
    echo "Initialized $dist in /_site"
fi

mv index.html index.php
rm build.sh CONTRIBUTING.md README.md LICENSE #from _site/
