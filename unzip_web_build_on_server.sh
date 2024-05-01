#!/bin/bash
cd /home/ubuntu/fully-featured-backend/flutter_web_app
# rm -rf *
unzip web_build.zip
mv home/ph/Projects/fully-featured/build/web/* .
# mv home/ph/Projects/fully-featured/build/web/.last_build_id .
rm -rf home web_build.zip
