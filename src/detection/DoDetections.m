function DoDetections(testDataFiles,imgDir,annotationDir,statsDir,modelDir,outputDir,doorLabel,windowLabel,numClasses)
% from Gadde et al. (2017) https://bitbucket.org/rgadde/wacv15_code/src/master/

%Default training parameters
opts = acfTrain();
opts.pPyramid.smooth=.5; opts.pPyramid.pChns.pColor.smooth=0;
opts.stride = 1;
opts.pNms.overlap = 0.99999;
opts.nWeak=[32 128 512 2048];
opts.pJitter=struct('flip',1);
opts.pBoost.pTree.fracFtrs=1/16;


stats = load(strcat(statsDir,'/stats.mat'));
doorStats = stats.doorStats;
windowStats = stats.windowStats;


%%%%%%%%%
%%% Do the training and detections for each fold and for each class
%%%%%%%%
%{
%Create Temp train image Dir and copy positive images into this dir
tempImgDir = strcat(outputDir,'tempImgDir/');
if isdir(tempImgDir) rmdir(tempImgDir,'s'); end
mkdir(tempImgDir);


for i=1:1:length(trainDataFiles)
    %[a,img_name,c] = fileparts(trainDataFiles{i});
		img_name = trainDataFiles{i};
    copyfile(strcat(imgDir,trainDataFiles{i},'.png'),tempImgDir);
end
%}

opts.posGtDir= annotationDir;
%opts.posImgDir=tempImgDir;

%For each class
for j=0:1:numClasses
    
    %disp(j);
    
    switch j
        
        case doorLabel
            %Door
            %Modify and train detector
            opts.name=strcat(modelDir, 'doorDetectorModel');
            opts.modelDs=doorStats.modelDs; opts.modelDsPad=doorStats.modelDsPad;
            pLoad={'lbls',{'door'},'ilbls',{'doors'}};
            opts.pLoad = [pLoad 'yRng',doorStats.yRange, 'xRng',doorStats.xRange, 'hRng',doorStats.hRange, 'wRng',doorStats.wRange ];
            detector = acfTrain(opts);
            
            %Do and save test detections
            leftRange = doorStats.xRange;
            topRange = doorStats.yRange;
            widthRange = doorStats.wRange;
            heightRange = doorStats.hRange;
            detector = acfModify(detector,'cascThr',-1,'cascCal',0.1,'stride',1);
            for t=1:1:length(testDataFiles)
                %[a,img_name,c] = fileparts(testDataFiles{t});
								img_name = testDataFiles{t};
                I = imread(strcat(imgDir,img_name,'.png'));
                bbs = acfDetect(I,detector);
                bbs_final = [];
                for s=1:1:size(bbs,1)
                    if (bbs(s,1) > leftRange(1)) && (bbs(s,1) < leftRange(2))
                        if (bbs(s,2) > topRange(1) && bbs(s,2) < topRange(2))
                            if (bbs(s,3) > widthRange(1) && bbs(s,3) < widthRange(2))
                                if (bbs(s,4) > heightRange(1) && bbs(s,4) < heightRange(2))
                                    bbs_final = [bbs_final ; bbs(s,:)];
                                end
                            end
                        end
                    end
                end
                
                imgSize = [size(I,1),size(I,2)];
                featureImage = zeros(imgSize);
                for k =1:1:size(bbs_final,1)
                    if bbs_final(k,5) > 0
                        featureImage = featureImage + GetDetectionMask(imgSize,bbs_final(k,:),bbs_final(k,5));
                    end
                end
                
                featureImage = featureImage';
                
                doorFeatures = featureImage(:);
                %dlmwrite(strcat(outputDir,'/',img_name,'.doorfeatures.txt'),doorFeatures,'delimiter',' ');
                
                fid=fopen(strcat(outputDir,'/',img_name,'.doorfeatures.bin'),'wb');
                fwrite(fid,doorFeatures,'float32');
                fclose(fid);
            end
            
        case windowLabel
            %Window
            %Modify and train detector
            opts.name=strcat(modelDir,'windowDetectorModel');
            opts.modelDs=windowStats.modelDs; opts.modelDsPad=windowStats.modelDsPad;
            pLoad={'lbls',{'window'},'ilbls',{'windows'}};
            opts.pLoad = [pLoad 'yRng',windowStats.yRange, 'xRng',windowStats.xRange, 'hRng',windowStats.hRange, 'wRng',windowStats.wRange ];
            detector = acfTrain(opts);
            
            %Do and save test detections
            leftRange = windowStats.xRange;
            topRange = windowStats.yRange;
            widthRange = windowStats.wRange;
            heightRange = windowStats.hRange;
            detector = acfModify(detector,'cascThr',-1,'cascCal',0.01,'stride',1);
            for t=1:1:length(testDataFiles)
                %[a,img_name,c] = fileparts(testDataFiles{t});
								img_name = testDataFiles{t};
                I = imread(strcat(imgDir,img_name,'.png'));
                bbs = acfDetect(I,detector);
                bbs_final = [];
                for s=1:1:size(bbs,1)
                    if (bbs(s,1) > leftRange(1)) && (bbs(s,1) < leftRange(2))
                        if (bbs(s,2) > topRange(1) && bbs(s,2) < topRange(2))
                            if (bbs(s,3) > widthRange(1) && bbs(s,3) < widthRange(2))
                                if (bbs(s,4) > heightRange(1) && bbs(s,4) < heightRange(2))
                                    bbs_final = [bbs_final ; bbs(s,:)];
                                end
                            end
                        end
                    end
                end
                
                imgSize = [size(I,1),size(I,2)];
                featureImage = zeros(imgSize);
                for k =1:1:size(bbs_final,1)
                    if bbs_final(k,5) > 0
                        featureImage = featureImage + GetDetectionMask(imgSize,bbs_final(k,:),bbs_final(k,5));
                    end
                end
                
                featureImage = featureImage';
                
                windowFeatures = featureImage(:);
                %dlmwrite(strcat(outputDir,'/',img_name,'.windowfeatures.txt'),windowFeatures,'delimiter',' ');
                
                fid=fopen(strcat(outputDir,'/',img_name,'.windowfeatures.bin'),'wb');
                fwrite(fid,windowFeatures,'float32');
                fclose(fid);
            end
    end
end
%if isdir(tempImgDir) rmdir(tempImgDir,'s'); end
end
