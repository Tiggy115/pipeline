
DARWIN = "lib/drwn"

INC_DIRS = -I${DARWIN}/include -I${DARWIN}/external -I${DARWIN}/external/opencv/include/
LIBS = -L${DARWIN}/bin -ldrwnML -ldrwnPGM -ldrwnIO -ldrwnBase -ldrwnVision -lm -lpthread

all: main test test2

main:
	g++ -fPIC -shared -o libTest.so classify.cpp ${INC_DIRS} ${LIBS} -D__LINUX__

test:
	g++ -g -o testOut test.cpp ${INC_DIRS} ${LIBS} -D__LINUX__

test2:
	g++ -g -o testOut test2.cpp ${INC_DIRS} ${LIBS} -D__LINUX__

clean:
	rm -f libTest.so testOut
