function mask = GetDetectionMask(imgSize,bbs,score);
% from Gadde et al. (2017) https://bitbucket.org/rgadde/wacv15_code/src/master/

mask = zeros(imgSize(1),imgSize(2));
bbs = floor(bbs);
mask(max(bbs(2),1):min(bbs(2)+bbs(4),imgSize(1)),...
    max(bbs(1),1):min(bbs(1)+bbs(3),imgSize(2))) = score;

end