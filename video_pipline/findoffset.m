function [av_offset, confidence]=findoffset(frames_dir, wav_file)
run /home/zyq/matconvnet-1.0-beta25/matlab/vl_setupnn.m	% Path to MatConvNet Vers 23
addpath /home/zyq/PycharmProjects/Video_pipline/bin/tools
gpuDevice(1);
%% Fixed parameters


shift   = -24:24;             % Audio-video offsets to search
Yframes = 5;
Aframes	= 20;

opt.fs       = 16000;
opt.Tw       = 25;
opt.Ts       = 10;            % analysis frame shift (ms)
opt.alpha    = 0.97;          % preemphasis coefficient
opt.R        = [ 300 3700 ];  % frequency range to consider
opt.M        = 40;            % number of filterbank channels 
opt.C        = 13;            % number of cepstral coefficients
opt.L        = 22;            % cepstral sine lifter parameter

%% Load net

netStruct = load('/home/zyq/PycharmProjects/Video_pipline/bin/syncnet_v4.mat');
net = dagnn.DagNN.loadobj(netStruct.net);
net.move('gpu')
net.conserveMemory = 0;
net.mode = 'test' ;

aud_id = structfind(net.vars,'name','x23_audio');
lip_id = structfind(net.vars,'name','x24_lip');


%% Load and prepare data

frame_list = dir([frames_dir, '*.png']);
frame_nums = length(frame_list);
Y = zeros(120,120,frame_nums, 'uint8');
for i=1:frame_nums;
    image_name = strcat(frames_dir, frame_list(i).name);
    img = imread(image_name);
    Y(:, :, i) = img;
end;

Y 				= bsxfun(@minus, single(Y), net.meta.normalization_l.averageImage) ;
Y 				= Y(5:115,5:115,:);

[Z,fs] = audioread(wav_file);
[ C, ~, ~ ] 	= runmfcc( Z, opt );
C 				= C(2:13,:);
C 				= bsxfun(@minus, single(C), net.meta.normalization_a.averageImage) ;


%% Network forward pass to get features

for j = 1: size(Y,3) - Yframes + 1
    y       = Y(:,:,(j:j+Yframes-1));
    net.eval({'input_lip',gpuArray(y)});
    Yf{j}  = squeeze(gather(net.vars(lip_id).value));
end


for j = 1: size(C,2) - Aframes + 1
    c       = C(:,(j:j+Aframes-1));
    net.eval({'input_audio',gpuArray(c)});
    Cf{j}   = squeeze(gather(net.vars(aud_id).value));
end


yf  = cat(2,Yf{:});
cf  = cat(2,Cf{:});

%% Determine frame offset

for i = 1:size(yf,2)-numel(shift)+1

    vframe = i-min(shift);
    aframe = (vframe*4)-1;

    for j = 1:numel(shift)
        dist(j) = pdist([yf(:,vframe+shift(j)) cf(:,aframe)]');
    end

    output{i} = dist;

end

out = mean(cat(1,output{:}),1);

[~,idx] = min(out);

offset = shift(idx);
conf = median(out)-min(out);

av_offset = offset;
confidence = conf;
