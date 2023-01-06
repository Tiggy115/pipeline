function detect()

opts = acfTrain();
opts.pPyramid.smooth=.5; opts.pPyramid.pChns.pColor.smooth=0;
opts.stride = 1;
opts.pNms.overlap = 0.99999;
opts.nWeak=[32 128 512 2048];
opts.pJitter=struct('flip',1);
opts.pBoost.pTree.fracFtrs=1/16;


