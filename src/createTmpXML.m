function createTmpXML(xmlFile, numStages, tmppath)
    % from Gadde et al. (2017) https://bitbucket.org/rgadde/wacv15_code/src/master/

    xDoc = xmlread(xmlFile);
    drwn = xDoc.getDocumentElement;
    options = drwn.getElementsByTagName('option');

    for i = 0:options.getLength-1
        name = options.item(i).getAttribute('name');
        if (strcmpi(name, 'baseDir')) baseDir = char(options.item(i).getAttribute('value')); end
        if (strcmpi(name, 'modelsDir')) modelsDir = char(options.item(i).getAttribute('value')); end
    end

    for stage = 1:numStages
        tmpXmlName = strcat(tmppath, '_stage', num2str(stage), '.xml');

        for i = 0:options.getLength-1
            name = options.item(i).getAttribute('name');
            if (strcmpi(name, 'modelsDir'))
                modModelsDir = strcat(modelsDir, '/stage', num2str(stage), '/');
                %modelsDir = strcat(modelsDir, 'fold', num2str(fold), '/');
                options.item(i).setAttribute('value',modModelsDir);
                if~isfolder(strcat(baseDir, modModelsDir)) mkdir(strcat(baseDir, modelsDir)); end
            end
        end
        xmlwrite(tmpXmlName, drwn); % xDoc
    end