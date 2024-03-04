#!/bin/bash

if [ -z "$1" ]; then
    echo "Usage: $0 <onion_link>"
    exit 1
fi

torsocks wget -qO- "$1" > page.html

grep -oP '(?<=<img src=").*?(?=")' page.html | sed 's|^/|'"$1"'|' > image_urls.txt

mkdir images

cd images
xargs -n 1 torsocks wget -nv < ../image_urls.txt
