import os
import matlab.engine


def do_classification(config, test_list, tmp, stages):
    eng = matlab.engine.start_matlab()
    # eng.cd(r"src", nargout=0)

    eng.createTmpXML(config, stages, tmp, nargout=0)
    for i in range(1, stages + 1):
        print("Stage " + str(i) + ":")
        xml = tmp + "_stage" + str(i) + ".xml"
        eng.facadeSeg(xml, tmp, i, test_list, nargout=0)
        os.system("./tmp.sh")

    eng.quit()

    os.system('rm -rf ' + tmp + '*')
    os.system('rm -rf ../cache')
    os.system('rm tmp.sh')


if __name__ == "__main__":
    do_classification("config/etrimsConfigFile.xml", "testList.txt", "../tmp/", 3)