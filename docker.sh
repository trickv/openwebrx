#!/usr/bin/env bash
set -euo pipefail

ARCH=$(uname -m)
IMAGES="openwebrxplus-rtlsdr openwebrxplus-sdrplay openwebrxplus-hackrf openwebrxplus-airspy openwebrxplus-rtlsdr-soapy openwebrxplus-plutosdr openwebrxplus-limesdr openwebrxplus-soapyremote openwebrxplus-perseus openwebrxplus-fcdpp openwebrxplus-radioberry openwebrxplus-uhd openwebrxplus-rtltcp openwebrxplus-runds openwebrxplus-hpsdr openwebrxplus-bladerf openwebrxplus-full openwebrxplus"
ALL_ARCHS="x86_64 armv7l aarch64"
TAG=${TAG:-"latest"}
ARCHTAG="${TAG}-${ARCH}"

usage () {
  echo "Usage: ${0} [command]"
  echo "Available commands:"
  echo "  help       Show this usage information"
  echo "  build      Build all docker images"
  echo "  push       Push built docker images to the docker hub"
  echo "  manifest   Compile the docker hub manifest (combines arm and x86 tags into one)"
  echo "  tag        Tag a release"
}

build () {
  # build the base images
  docker build --pull -t openwebrxplus-base:${ARCHTAG} -f docker/Dockerfiles/Dockerfile-base .
  docker build --build-arg ARCHTAG=${ARCHTAG} -t openwebrxplus-soapysdr-base:${ARCHTAG} -f docker/Dockerfiles/Dockerfile-soapysdr .

  for image in ${IMAGES}; do
      echo "Image: $image"
    i=${image:10}
    i=$(echo $image | cut -d- -f2-)
    echo "i: $i"
    # "openwebrxplus" is a special image that gets tag-aliased later on
    if [[ ! -z "${i}" ]] ; then
      docker build --build-arg ARCHTAG=$ARCHTAG -t trickv/${image}:${ARCHTAG} -f docker/Dockerfiles/Dockerfile-${i} .
    fi
  done

  # tag openwebrxplus alias image
  docker tag trickv/openwebrxplus-full:${ARCHTAG} trickv/openwebrxplus:${ARCHTAG}
}

push () {
  for image in ${IMAGES}; do
    docker push trickv/${image}:${ARCHTAG}
  done
}

manifest () {
  for image in ${IMAGES}; do
    # there's no docker manifest rm command, and the create --amend does not work, so we have to clean up manually
    rm -rf "${HOME}/.docker/manifests/docker.io_trickv_${image}-${TAG}"
    IMAGE_LIST=""
    for a in ${ALL_ARCHS}; do
      IMAGE_LIST="${IMAGE_LIST} trickv/${image}:${TAG}-${a}"
    done
    docker manifest create trickv/${image}:${TAG} ${IMAGE_LIST}
    docker manifest push --purge trickv/${image}:${TAG}
  done
}

tag () {
  if [[ -x ${1:-} || -z ${2:-} ]] ; then
    echo "Usage: ${0} tag [SRC_TAG] [TARGET_TAG]"
    return
  fi

  local SRC_TAG=${1}
  local TARGET_TAG=${2}

  for image in ${IMAGES}; do
    # there's no docker manifest rm command, and the create --amend does not work, so we have to clean up manually
    rm -rf "${HOME}/.docker/manifests/docker.io_trickv_${image}-${TARGET_TAG}"
    IMAGE_LIST=""
    for a in ${ALL_ARCHS}; do
      docker pull trickv/${image}:${SRC_TAG}-${a}
      docker tag trickv/${image}:${SRC_TAG}-${a} trickv/${image}:${TARGET_TAG}-${a}
      docker push trickv/${image}:${TARGET_TAG}-${a}
      IMAGE_LIST="${IMAGE_LIST} trickv/${image}:${TARGET_TAG}-${a}"
    done
    docker manifest create trickv/${image}:${TARGET_TAG} ${IMAGE_LIST}
    docker manifest push --purge trickv/${image}:${TARGET_TAG}
    docker pull trickv/${image}:${TARGET_TAG}
  done
}

case ${1:-} in
  build)
    build
    ;;
  push)
    push
    ;;
  manifest)
    manifest
    ;;
  tag)
    tag ${@:2}
    ;;
  *)
    usage
    ;;
esac
