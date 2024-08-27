# Fun With Building Yocto

My notes on how I built Yocto with k3s.

.:NOTE The Dockerfile is of limited use right now.

## Useful commands

To build the basic image:

```bash
git clone git://git.yoctoproject.org/poky &&\
cd poky &&\
git checkout -t origin/scarthgap -b my-scarthgap &&\
git pull &&\
source oe-init-build-env &&\
bitbake core-image-sato
```

- `docker build -t yacto_fun .`
- `docker run -it --privileged --net host -v $(pwd):/playpen -e GITLAB_CREDS -e CI_SERVER_HOST="gitlab.aero.ball.com" -e GITLAB_GROUP -e AERO=true -u yocto yacto_fun:latest bash`
- `bitbake -c menuconfig virtual/kernel` - Look at the kernel configuration for the image that it will build.
- `bitbake - c cleanall core-image-minimal` - Clean up the output images to try to start over
  - `rm -rf tmp` - Remove everything and actually start over. This includes the layers and all intermedate steps.
- `bitbake-layers create-layer <layer-name>` create a new Yocto layer, usuallt called `meta-<something>`.

## Terms

- Metadata - Files containting information about how to build an image. It can be used to augment the existing build by adding layers
- Layer - A directory containing grouped meta data and a collection of related recipies. Can be board specific recipies and meta data
- Recipe - File with instructions to build one or more packages. Includes build, complilation, and configuration information
- Package - a "baked recipe" that `bitbake` has alredy been run on, this can be though of as a pre-build binary
- BSP (Board Support Package) - A layer that defines how to build for a board that is normally maintained by a specific vendor
- Distribution - A specific implementation of Linux
- Machine - The hardware defines the architecture, pins, busses, BSP, etc
- Image - Output of the build process which includes kernel and OS
- Reference distribution - Metadata, layers, BSP, BitBake, and tools that make up the Yocto project that will generate the images in a known image
- Poky - The Yocto build tool
- [Class](https://docs.yoctoproject.org/ref-manual/classes.html) - Used to abstract common functionality and share it within recipies has extension `.bbclass`. Usually a recipe inherits a class. Metadata can usually be made into a class file.

New layers should be put on the same layer as poky.
If it is a git repo, it should have a branch that is compatable with the version of Yocto that we are using.

## General practices

Sources should contain the things that we build from like Poky and other BSPs.
The new layers that I develop should be in the what they call the [source directory}(https://docs.yoctoproject.org/dev/ref-manual/terms.html#term-Source-Directory) in Yocto which comes from Poky.

Using a `?=` is a soft assignment which basically creates defaults.
An assignment with just `=` is hard assignment will over always overwrite.

Layers start with `meta-`.
pre made layers can be found at https://www.yoctoproject.org/development/yocto-project-compatible-layers/ and https://www.yoctoproject.org/development/yocto-project-compatible-layers/.

Existing layers can be found on [the Open Embedded](https://layers.openembedded.org/layerindex/branch/master/layers/).
You must add the layers to the poky layers config in `poky/build/conf/bblayers.conf`.
Once layers are added to the config, you can add depends on your custom recipies.

To add a new recipe, bitbake has some things built in to help create it: `devtool add k0s /home/dave/playpen/yocto_test/poky/build/workspace/sources/k0s https://arti.bsf.ball.com:443/artifactory/dev-local/k0s/k0s_binary_and_images.tar.gz -b`

## Useful links

- [PetaLinux to Yocto Command cross reference](https://xilinx-wiki.atlassian.net/wiki/spaces/A/pages/2787311617/PetaLinux+to+Yocto+-+Command+Cross+Reference)
- [Yocto Development Manual](https://docs.yoctoproject.org/dev/dev-manual/)

## Below is mostly Peta Linux which we cannot use on stardust

### From Rick

Start by using a development container.
I started with the common ACE container.

```bash
export GITLAB_TOKEN_NAME=<your-token-name>
export GITLAB_TOKEN=<your-token>
export GITLAB_CREDS="${GITLAB_TOKEN_NAME}:${GITLAB_TOKEN}"

docker run \
  --rm \
  -it \
  --privileged \
  --net host \
  -v $(pwd):/workdir \
  -w /workdir -e GITLAB_CREDS -e CI_SERVER_HOST="gitlab.aero.ball.com" -e GITLAB_GROUP -e AERO=true \
  -v ${HOME}/.gitconfig:/root/.gitconfig \
  registry-gitlab.aero.ball.com/nci/common-ace/docker/peta-cpp-develop \
  bash
```

look at common-ace bsp repo - get peta linux link from that

BSP - board support package. Includes/create bootable images.
The big one is called boot.bin which is a first stage bootloader which will fire up uboot.
image.ub - FIT image which includes kernal for peta linux
boot.scr - first stage boot loader
will need to send to SD card.

recipies are in components and src
ckeck out `startup.bb` and try adding k3s to `RDEPENDS`.

Check out Qemu for testing builds

### #From Barak
