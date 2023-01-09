function DoDoorWindowDetections(testListFile,outDir,doorLabel,windowLabel,imageDir,numClasses, modelDir)
% modified from Gadde et al. (2017) https://bitbucket.org/rgadde/wacv15_code/src/master/

f = fopen(testListFile,'r');
testDataFiles = textscan(f,'%s');
testDataFiles = testDataFiles{1};

%Create GT annotations and also compute size statistics of doors and
%windows
statsDir = strcat(modelDir, '../');
annotationDir = strcat(modelDir,'../annotations/');
statsFile = strcat(statsDir,'stats.mat');
if ~isfolder(annotationDir) %after training not needed
    fprintf("annotations are missing! \n")
elseif ~exist(statsFile,'file');
    fprintf(strcat(statsDir, " is missing! \n"));
end

decModelDir = strcat(modelDir, "../detection_models/");
auxFeatureDir = strcat(outDir, "auxFeatures/");
if ~isfolder(auxFeatureDir) mkdir(auxFeatureDir); end

%Train the detectors and extract features
DoDetections(testDataFiles,imageDir,annotationDir,statsDir,decModelDir,auxFeatureDir,doorLabel,windowLabel,numClasses);

end
