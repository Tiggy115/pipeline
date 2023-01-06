# pipeline
## A pipeline for translating a building from a panoramic image to its representation in the CGV grammar.


Used non Python lib projects:
- cgv: https://github.com/cc-bbohlender/cgv
- lsaa-dataset: https://github.com/ZPdesu/lsaa-dataset
- sky-detector: https://github.com/cftang0827/sky-detector
- wacv15_code: https://bitbucket.org/rgadde/wacv15_code/src/master/
- Darwin: https://github.com/sgould/drwn
- toolbox: https://github.com/pdollar/toolbox



If error message "*libopencv_core.so.2.4: cannot open shared object file: No such file or directory*" occurs, try:

```commandline
sudo ldconfig -v
```

To install the libraries, run **lib/setup.sh**

Tested on Ubuntu 22.04.1 LTS  