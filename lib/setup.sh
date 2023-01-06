
set -e
sudo apt-get install csh cmake g++ libgtk2.0-dev pkg-config


# darwin
git clone https://github.com/sgould/drwn.git
mv eigen-3.2.10.tar.bz2 drwn/external/eigen-3.2.10.tar.bz2
mv lua-5.2.4.tar.gz drwn/external/lua-5.2.4.tar.gz
rm drwn/external/install.sh
mv install.sh drwn/external/install.sh
cd drwn/external
./install.sh Eigen
./install.sh zlib
./install.sh OpenCV
./install.sh wxWidgets
./install.sh lua

wget -O rapidxml-1.13.zip "http://downloads.sourceforge.net/project/rapidxml/rapidxml/rapidxml%201.13/rapidxml-1.13.zip?r=http%3A%2F%2Frapidxml.sourceforge.net%2F&ts=1364493742&use_mirror=garr"
unzip rapidxml-1.13.zip
mv rapidxml-1.13 rapidxml
cd ..

export DARWIN="$PWD"
export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${DARWIN}/external/opencv/lib

make -j8
make drwnprojs -j8
cd ..

# piotr dollar's toolbox
git clone https://github.com/pdollar/toolbox.git


git clone https://github.com/cftang0827/sky-detector.git
mv sky-detector/sky_detector sky_detector
rm -rf sky-detector



