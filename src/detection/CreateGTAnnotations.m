function CreateGTAnnotations(dataList,gtLabelDir,annotationDir,statsDir,doorLabel,windowLabel,numClasses)

doorParams = [];
windowParams = [];

for i=1:1:length(dataList)
    
    %[a,img_name,c] = fileparts(dataList{i});
		img_name = dataList{i};
    
    %Load segmentation labels for the image
    labels = load(strcat(gtLabelDir,img_name,'.txt'));
    
    numObjects = 0;
    objTypes = [];
    objParams = [];
    
    for j=0:1:numClasses
        bwImage = labels == j;
        params = GetParams(bwImage);
        for t=1:1:size(params,1)
            objParams = [objParams; params(t,:)];
            numObjects = numObjects + 1;
            
            switch j
                case doorLabel
                    %Door class
                    objTypes{numObjects} =  'door';
                    doorParams = [doorParams; params(t,1:4)];
                case windowLabel
                    %Window class
                    objTypes{numObjects} =  'window';
                    windowParams = [windowParams; params(t,1:4)];
                otherwise
                    objTypes{numObjects} = 'other';
            end
        end
        
    end
    
    objs = bbGt('create',[numObjects]);
    for k=1:1:numObjects
        objs(k).lbl = objTypes{k};
        objs(k).bb = objParams(k,1:4);
        %objs(k).occ = objParams(k,5:8);
        %objs(k). bbv = objParams(k,9);
        %objs(k).ign = objParams(k,10);
        %objs(k).ang = objParams(k,11);
    end
    
    fName = strcat(annotationDir,img_name,'.txt');
    objs = bbGt('bbSave', objs, fName);
    
end

doorStats = {};
doorStats.xRange = [max(0,min(doorParams(:,1))-100) max(doorParams(:,1))+100];
doorStats.yRange = [max(0,min(doorParams(:,2))-100) max(doorParams(:,2))+100];
doorStats.hRange = [max(0,min(doorParams(:,4))-20) max(doorParams(:,4))+20];
doorStats.wRange = [max(0,min(doorParams(:,3))-10) max(doorParams(:,3))+10];
doorStats.modelDs = [mean(doorParams(:,4))-10 mean(doorParams(:,3))-10];
doorStats.modelDsPad = [doorStats.hRange(2)-10 doorStats.wRange(2)];

windowStats = {};
windowStats.xRange = [max(0,min(windowParams(:,1))-100) max(windowParams(:,1))+100];
windowStats.yRange = [max(0,min(windowParams(:,2))-100) max(windowParams(:,2))+100];
windowStats.hRange = [max(0,min(windowParams(:,4))-20) max(windowParams(:,4))+20];
windowStats.wRange = [max(0,min(windowParams(:,3))-10) max(windowParams(:,3))+10];
windowStats.modelDs = [mean(windowParams(:,4))-10 mean(windowParams(:,3))-10];
windowStats.modelDsPad = [windowStats.hRange(2)-10 windowStats.wRange(2)];

save(strcat(statsDir,'/stats.mat'),'doorStats','windowStats');

end

function params = GetParams(bwImage)

params = [];

bwImage = bwareaopen(bwImage, 200);
CC = bwconncomp(bwImage);
nObjects = CC.NumObjects;
imgL = bwlabel(bwImage);
for i=1:1:nObjects
    [indX,indY]=find(imgL==i);
    obj_l=min(indY);obj_t=min(indX);
    obj_w=max(indY)-min(indY);
    obj_h=max(indX)-min(indX);
    params = [params; obj_l obj_t obj_w obj_h 0 0 0 0 0 0 0];
end


end
