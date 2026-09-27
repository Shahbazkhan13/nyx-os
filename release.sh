#!/bin/bash
# NyxOS Release Script
set -e

VERSION=$(cat VERSION)
TAG="v$VERSION"

echo "Releasing NyxOS $TAG"

git add .
git commit -m "release: NyxOS $TAG" || true
git tag "$TAG"
git push
git push --tags

echo "Released: $TAG"
