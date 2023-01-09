function facadeSeg(configFileName, tmppath, stage, testFileName)
    % modified from Gadde et al. (2017) https://bitbucket.org/rgadde/wacv15_code/src/master/

    %shFile = [tmppath "tmp.sh"];
    shFile = "tmp.sh";
    fsh = fopen(shFile,"w");
    fprintf(fsh,"#!/bin/bash\n");

    %% drwn commands
    cmd = cell(3,1);
    cmd{1} = "../lib/drwn/bin/inferPixelLabels -pairwise 0.0 ";
    %pairwise
    cmd{2} = "../lib/drwn/bin/inferPixelLabels ";

    %% parse the config file
    try
        xDoc = xmlread(configFileName);
        drwn = xDoc.getDocumentElement;
        options = drwn.getElementsByTagName("option");

        for i = 0:options.getLength-1
            name = options.item(i).getAttribute("name");
            if (strcmpi(name, "baseDir")) baseDir = char(options.item(i).getAttribute("value")); end
        end

        for i = 0:options.getLength-1
            name = options.item(i).getAttribute("name");
            if (strcmpi(name, "modelsDir")) modelDir = strcat(baseDir, char(options.item(i).getAttribute("value"))); end
            if (strcmpi(name, "imgDir")) imgDir = strcat(baseDir, char(options.item(i).getAttribute("value"))); end
            if (strcmpi(name, "outputDir")) outputDir = strcat(baseDir, char(options.item(i).getAttribute("value"))); end
            if (strcmpi(name, "auxFeatureDir")) auxFeatureDir = char(options.item(i).getAttribute("value")); end
            if (strcmpi(name, "cacheDir")) cacheDir = strcat(baseDir, char(options.item(i).getAttribute("value"))); end
        end
        %regions = drwn.getElementsByTagName("region");
    catch
        fprintf(2, "config file errror!\n");
        return;
    end


    if~isfolder(strcat(baseDir, outputDir)) mkdir(strcat(baseDir, outputDir)); end
    if~isfolder(strcat(baseDir, cacheDir)) mkdir(strcat(baseDir, cacheDir)); end
    if~isfolder(auxFeatureDir) mkdir(auxFeatureDir); end

    %% Facade Segmentation
    addpath(genpath("../lib/toolbox/"));
    addpath( "detection");
    addpath("autocontext");



    tmpXmlName = strcat(tmppath, "_stage", num2str(stage), ".xml");
    saveimages = strcat(" -outImages .stage",num2str(stage), ".unary.png ");
    savelabels = strcat(" -outLabels .stage", num2str(stage), ".unary.txt ");
    saveunary  = strcat(" -outUnary .pot.txt ");
    savepair = strcat(" -outLabels .stage", num2str(stage), ".pairwise.txt -outImages .stage", num2str(stage), ".pairwise.png ");
    projMultiSeg6 = strcat(" -outLabels .stage", num2str(stage), ".projMultiSeg6.txt -outImages .stage", num2str(stage), ".projMultiSeg6.png ");
    config = strcat(" -config ", tmpXmlName, " ");

    xDoc = xmlread(configFileName); drwn = xDoc.getDocumentElement; options = drwn.getElementsByTagName("option");

    regionDefinitions = drwn.getElementsByTagName("regionDefinitions");
    regions = regionDefinitions.item(0).getChildNodes;
    node = regions.getFirstChild; numRegions =0 ;
    while ~isempty(node)
        if strcmpi(node.getNodeName, "region")
            numRegions = numRegions + 1;
            name = node.getAttribute("name");
            if (strcmpi(name, "window"))
                windowLabel = str2num(char(node.getAttribute("id")));
            end
            if (strcmpi(name, "door"))
                doorLabel = str2num(char(node.getAttribute("id")));
            end
        end
        node = node.getNextSibling;
    end

    for i = 0:options.getLength-1
        name = options.item(i).getAttribute("name");
        if (strcmpi(name, "auxFeatureExt") && stage~=1)
            fileExt = ".pot.txt";
            featstr = extractFeatures_binary(testFileName, outputDir, auxFeatureDir, imgDir, numRegions, fileExt);
            auxFeatureExt = char(options.item(i).getAttribute("value"));
            auxFeatureExt = strcat(auxFeatureExt, " ", featstr);
            options.item(i).setAttribute("value",auxFeatureExt);
        end
    end
    xmlwrite(tmpXmlName, drwn); % xDoc

    if stage == 1
        DoDoorWindowDetections(testFileName,outputDir,doorLabel,windowLabel,imgDir,numRegions, modelDir);
    end

    shLine = strcat(cmd{1}, config, saveimages, savelabels, saveunary, testFileName);fprintf(fsh,"%s\n",shLine);
    %shLine = strcat(cmd{2}, config, savepair, testFileName);fprintf(fsh,"%s\n",shLine);
    shLine = strcat(cmd{2}, config, projMultiSeg6, " -longrange 2.0 ", testFileName);fprintf(fsh,"%s\n",shLine);

    fclose(fsh);