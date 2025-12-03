#!/bin/bash
cd ..
poetry build -o io_validation_tool/dist -f sdist
cd io_validation_tool/dist

for file in *-*.tar.gz; do
    base=${file%-*};
    ext=${file##*-};
    mv "$file" "$base.tar.gz";
done
cd ..

docker build . $@
