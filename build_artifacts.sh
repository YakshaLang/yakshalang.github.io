#!/usr/bin/env bash

realpath() {
    [[ $1 = /* ]] && echo "$1" || echo "$PWD/${1#./}"
}

cd pdf-builder
docker build -t pdf-builder .

export DOCS=$(realpath "../docs")

echo "docs path is $DOCS"

docker run -v "$DOCS:/workspace" --rm -it pdf-builder --url http://localhost/documentation.html --pdf "yaksha-documentation-$(date +%Y-%m-%d).pdf"
docker run -v "$DOCS:/workspace" --rm -it pdf-builder --url http://localhost/library-docs.html --pdf "yaksha-library-docs-$(date +%Y-%m-%d).pdf"
docker run -v "$DOCS:/workspace" --rm -it pdf-builder --url http://localhost/tutorials.html --pdf "yaksha-tutorials-$(date +%Y-%m-%d).pdf"
docker run -v "$DOCS:/workspace" --rm -it pdf-builder --url http://localhost/yama.html --pdf "yaksha-yama-$(date +%Y-%m-%d).pdf"
docker run -v "$DOCS:/workspace" --rm -it pdf-builder --url http://localhost/blog.html --pdf "yaksha-blog-$(date +%Y-%m-%d).pdf"

cd ..
rm -f downloadable_artifacts/*.pdf
rm -f downloadable_artifacts/*.zip
mv -f docs/*.pdf downloadable_artifacts/
cp LICENSE docs/LICENSE
zip -r "downloadable_artifacts/yaksha-docs-html-$(date +%Y-%m-%d).zip" docs
rm -f docs/LICENSE