function featstr = extractFeatures_binary(imgListFile, inputFolder, outputFolder, imageFolder, numClasses, fileExt)
% from Gadde et al. (2017) https://bitbucket.org/rgadde/wacv15_code/src/master/

file = fopen(imgListFile);
unaryFiles = textscan(file,'%s');
unaryFiles = unaryFiles{1};

try
    parpool close;
end
try
	if (feature('numCores') >= 4)
    parpool open 8;
	else
		parpool open 4;
	end
end
t_time=0;
for i = 1:length(unaryFiles)
%for i = 1:1:length(unaryFiles)
    
    %disp(i);
    
    img_name = unaryFiles{i};
    
    img = imread(strcat(imageFolder,img_name,'.png'));
    [rs,cls,ch] = size(img);
    numPix = rs*cls;
    
    unaries = load(strcat(inputFolder,img_name,fileExt));
    unaries = exp(-1*unaries);
    
    %Compute MAP estimate
    [mapValues, mapClasses] = max(unaries,[],2);
    
    %Compute Entropy
    entropyValues = -1*sum(unaries.*log(unaries),2);
    
    mapFeatures = unaries;
    
    horFeatures = zeros(numPix,numClasses);
    verFeatures = zeros(numPix,numClasses);
    
    horScoreFeatures = zeros(numPix,numClasses);
    verScoreFeatures = zeros(numPix,numClasses);
    
    distFeatures = zeros(numPix,numClasses);
    distBlockFeatures = zeros(numPix,numClasses);
    colorFeatures = zeros(numPix,numClasses);
    bboxFeatures = zeros(numPix,numClasses);
    rectFeatures = zeros(numPix,numClasses);
    
    leftFeatures = zeros(numPix,numClasses);
    rightFeatures = zeros(numPix,numClasses);
    topFeatures = zeros(numPix,numClasses);
    bottomFeatures = zeros(numPix,numClasses);
    
    
    %Compute Hor-Count, Ver-Count, Distance Transform and color distance features
    unaryLabels = reshape(mapClasses,cls,rs);
	t_start = cputime;
    for t = 1:1:numClasses
        classScores = unaries(:,t);
        classScores = reshape(classScores,cls,rs);
        
        countValues = conv2(classScores,ones(11,5))/55;
        tFeatures = countValues(11:end,3:end-2);
        topFeatures(:,t) = tFeatures(:);
        bFeatures = countValues(1:end-10,3:end-2);
        bottomFeatures(:,t) = bFeatures(:);
        
        countValues = conv2(classScores,ones(5,11))/55;
        lFeatures = countValues(3:end-2,11:end);
        leftFeatures(:,t) = lFeatures(:);
        rFeatures = countValues(3:end-2,1:end-10);
        rightFeatures(:,t) = rFeatures(:);
        
        
        binaryImage = (unaryLabels == t);
        
        horCount = sum(binaryImage,1) / cls;
        verCount = sum(binaryImage,2) / rs;
        
        horFeat = repmat(horCount,[cls,1]);
        verFeat = repmat(verCount,[1,rs]);
        
        horFeatures(:,t) = horFeat(:);
        verFeatures(:,t) = verFeat(:);
        
        distFeat = bwdist(binaryImage);
        distFeatures(:,t) = distFeat(:);
        
        distFeat = bwdist(binaryImage,'cityblock');
        distBlockFeatures(:,t) = distFeat(:);
        
        scoreImage = reshape(unaries(:,t),cls,rs);
        
        horScore = sum(scoreImage,1) / cls;
        verScore = sum(scoreImage,2) / rs;
        horScore = repmat(horScore,[cls,1]);
        verScore = repmat(verScore,[1,rs]);
        horScoreFeatures(:,t) = horScore(:);
        verScoreFeatures(:,t) = verScore(:);
       
        
        %Compute Rectangle and Bbox Features
        BW = bwareaopen(binaryImage,200);
        bboxImage = zeros(size(BW));
        bboxes = regionprops(BW,'BoundingBox');
        for k=1:1:length(bboxes)
            bb = bboxes(k).BoundingBox;
            bboxImage(round(max(1,bb(2))):round(bb(2)+bb(4)),round(max(1,bb(1)):round(bb(1)+bb(3)))) = 1;
        end
				bboxImage=bboxImage(1:size(BW,1),1:size(BW,2));
        bboxFeatures(:,t) = bboxImage(:);
        bFeatures = bboxImage(:);
        y = double(mapClasses == t) .* unaries(:,t);
        rFeatures = y;
        rFeatures(bFeatures==0) = 0;
        rectFeatures(:,t) = rFeatures;
        
        
        %Get class pixel probabilities
        %y = double(mapClasses==t) .* unaries(:,t);
        y(y==0) = [];
        y = sort(y);
        
        % compute 25th percentile (first quartile)
        %q_1 = median(y(find(y<median(y))));
        
        % compute 50th percentile (second quartile)
        %q_2 = median(y);
        
        % compute 75th percentile (third quartile)
        q_3 = median(y(find(y>median(y))));
        
        
        classPixels = (mapClasses == t);
        classPixels(mapValues < q_3) = 0;
        
        tImage=permute(img,[2,1,3]);
        
        R = reshape(tImage(:,:,1),[],1);
        G = reshape(tImage(:,:,2),[],1);
        B = reshape(tImage(:,:,3),[],1);
        A = [R G B];
        colorValues = A;
        
        A(classPixels == 0,:) = [];
        
        color_mu = mean(A);
        color_sigma = cov(double(A));
        
        %Check for SPD
        check1 = isequal(tril(color_sigma), triu(color_sigma)');
        [~,p] = chol(color_sigma);
        check2 = (p==0);
        if check1 && check2
        else
            color_sigma = eye(3) * 0.5;
        end
        if length(color_mu) == 3
            colorFeatures(:,t) = -1*log(mvnpdf(double(colorValues),color_mu,color_sigma));
        end
        
    end
   	%t_time = t_time + 
    %cputime - t_start;
    colorFeatures(colorFeatures < 0.001) = 0;
    colorFeatures(isnan(colorFeatures)) = 0;
    colorFeatures(colorFeatures==Inf) = 1;
    
    horFeatures(horFeatures < 0.001) = 0;
    horFeatures(isnan(horFeatures)) = 0;
    horFeatures(horFeatures==Inf) = 1;
    
    verFeatures(verFeatures < 0.001) = 0;
    verFeatures(isnan(verFeatures)) = 0;
    verFeatures(verFeatures==Inf) = 1;
    
    horScoreFeatures(horScoreFeatures < 0.001) = 0;
    horScoreFeatures(isnan(horScoreFeatures)) = 0;
    horScoreFeatures(horScoreFeatures==Inf) = 1;
    
    verScoreFeatures(verScoreFeatures < 0.001) = 0;
    verScoreFeatures(isnan(verScoreFeatures)) = 0;
    verScoreFeatures(verScoreFeatures==Inf) = 1;
    
    distFeatures(distFeatures < 0.001) = 0;
    distFeatures(isnan(distFeatures)) = 10000;
    distFeatures(distFeatures==Inf) = 10000;
    
    distBlockFeatures(distBlockFeatures < 0.001) = 0;
    distBlockFeatures(isnan(distBlockFeatures)) = 10000;
    distBlockFeatures(distBlockFeatures==Inf) = 10000;
    
    leftFeatures(isnan(leftFeatures)) = 0;
    rightFeatures(isnan(rightFeatures)) = 0;
    bottomFeatures(isnan(bottomFeatures)) = 0;
    topFeatures(isnan(topFeatures)) = 0;
    

		featstr = []; disp(img_name);
    fid = fopen([outputFolder img_name '.entropy.bin'],'wb'); 
		fwrite(fid,entropyValues,'float32'); fclose(fid);
		featstr = [featstr ' .entropy.bin '];
    
    for s=1:1:size(mapFeatures,2)
        fid = fopen([outputFolder img_name '.score' int2str(s) '.bin'], 'wb'); 
        fwrite(fid,mapFeatures(:,s),'float32'); fclose(fid);
				featstr = [featstr ' .score' int2str(s) '.bin '];
    end
    
    for s=1:1:size(horFeatures,2)
        fid=fopen(strcat(outputFolder,img_name,'.horcount',int2str(s) ,'.bin'),'wb');
        fwrite(fid,horFeatures(:,s),'float32');  fclose(fid);
		featstr = [featstr ' .horcount' int2str(s) '.bin '];
    end
    
    for s=1:1:size(verFeatures,2)
        fid=fopen(strcat(outputFolder,img_name,'.vercount',int2str(s) ,'.bin'),'wb');
        fwrite(fid,verFeatures(:,s),'float32'); fclose(fid);
		featstr = [featstr ' .vercount' int2str(s) '.bin ' ];
    end
    
    for s=1:1:size(horScoreFeatures,2)
        fid=fopen(strcat(outputFolder,img_name,'.horscore',int2str(s) ,'.bin'),'wb');
        fwrite(fid,horScoreFeatures(:,s),'float32'); fclose(fid);
			featstr = [featstr ' .horscore' int2str(s) '.bin '];
    end
    
    for s=1:1:size(verScoreFeatures,2)
        fid=fopen(strcat(outputFolder,img_name,'.verscore',int2str(s) ,'.bin'),'wb');
        fwrite(fid,verScoreFeatures(:,s),'float32'); fclose(fid);
			featstr = [featstr ' .verscore' int2str(s) '.bin '];
    end
    
    for s=1:1:size(distFeatures,2)
        fid=fopen(strcat(outputFolder,img_name,'.blockdistance',int2str(s) ,'.bin'),'wb');
        fwrite(fid,distFeatures(:,s),'float32');    fclose(fid);
		featstr = [featstr ' .blockdistance',int2str(s) ,'.bin '];
    end
    
    for s=1:1:size(distBlockFeatures,2)
        fid=fopen(strcat(outputFolder,img_name,'.distance',int2str(s) ,'.bin'),'wb');
        fwrite(fid,distBlockFeatures(:,s),'float32'); fclose(fid);
		featstr = [featstr ' .distance' int2str(s) '.bin '];
    end
    
    
    for s=1:1:size(colorFeatures,2)
        fid=fopen(strcat(outputFolder,img_name,'.color',int2str(s) ,'.bin'),'wb');
        fwrite(fid,colorFeatures(:,s),'float32');        fclose(fid);
		featstr = [featstr ' .color' int2str(s) '.bin '];
    end
    
    for s=1:1:size(rectFeatures,2)
        fid=fopen(strcat(outputFolder,img_name,'.rectangle',int2str(s) ,'.bin'),'wb');
        fwrite(fid,rectFeatures(:,s),'float32'); fclose(fid);
		featstr = [featstr ' .rectangle' int2str(s) '.bin '];
    end
    
    for s=1:1:size(bboxFeatures,2)
        fid=fopen(strcat(outputFolder,img_name,'.bbox',int2str(s) ,'.bin'),'wb');
        fwrite(fid,bboxFeatures(:,s),'float32'); fclose(fid);
		featstr = [featstr ' .bbox' int2str(s) '.bin '];
    end
    
    for s=1:1:size(topFeatures,2)
        fid=fopen(strcat(outputFolder,img_name,'.top',int2str(s) ,'.bin'),'wb');
        fwrite(fid,topFeatures(:,s),'float32'); fclose(fid);
		featstr = [featstr ' .top' int2str(s) '.bin ' ];
    end
    
    for s=1:1:size(bottomFeatures,2)
        fid=fopen(strcat(outputFolder,img_name,'.bottom',int2str(s) ,'.bin'),'wb');
        fwrite(fid,bottomFeatures(:,s),'float32'); fclose(fid);
		featstr = [featstr ' .bottom' int2str(s) '.bin '];
    end
    
    for s=1:1:size(leftFeatures,2)
        fid=fopen(strcat(outputFolder,img_name,'.left',int2str(s) ,'.bin'),'wb');
        fwrite(fid,leftFeatures(:,s),'float32'); fclose(fid);
		featstr = [featstr ' .left' int2str(s) '.bin '];
    end
    
    for s=1:1:size(rightFeatures,2)
        fid=fopen(strcat(outputFolder,img_name,'.right',int2str(s) ,'.bin'),'wb');
        fwrite(fid,rightFeatures(:,s),'float32'); fclose(fid);
		featstr = [featstr ' .right' int2str(s) '.bin '];
    end  
		featstr1{i} = featstr;
end
featstr = featstr1{1};
try
    parpool close;
end
%t_time / length(unaryFiles)
end

