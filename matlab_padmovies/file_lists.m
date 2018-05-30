
%basedir = '/home/nmurphy/work/projects/stochastic/data/bio_film_data/hdisk/biofilm_fig1/';
basedir = '/home/nmurphy/SLCU/teamJL/Niall/biofilm_slice/biofilm_fig1/';

make_schitz = @(date, name, frames) create_new_schnitzobj(basedir, date, name, frames);


all_delRU_list = [ %make_schitz('2015-10-29', 'sigB_biofilmpad6-O001_2', 25 ) 
    make_schitz('2015-10-29', 'sigB_biofilmpad6-O001_3', 3:31 ) 
    make_schitz('2015-10-30', 'sigB_biofilmpadrepeat-delRU_1', 1:36); % SKIPED doenst reach steady
    make_schitz('2015-10-30', 'sigB_biofilmpadrepeat-delRU_2', 21:36); %(ignoring bright cell) 
    make_schitz('2015-10-30', 'sigB_biofilmpadrepeat-delRU_6', 1:31); %(ignoring bright) 
    make_schitz('2015-10-30', 'sigB_biofilmpadrepeat-delRU_8', 22:31); 
    make_schitz('2015-11-03', 'sigB_biofilmfinal-DelRU_1', 25:41) %(bright cell until frame 25)
    make_schitz('2015-11-03', 'sigB_biofilmfinal-DelRU_3', 21:38)
    make_schitz('2015-11-03', 'sigB_biofilmfinal-DelRU_4', 1:41) % SKIPED not steady (bright cells, left alone)
    make_schitz('2015-11-03', 'sigB_biofilmfinal-DelRU_5', 21:36) % SKIPED not steady
    make_schitz('2015-11-03', 'sigB_biofilmfinal-DelRU_10' , 1:40) % (ignoreing bright cell) % small, doesnt pulse much
];

delRU_low_mean = [
    all_delRU_list(6)  %sigB_biofilmfinal-DelRU_1_1 109.608250
    all_delRU_list(7)  %sigB_biofilmfinal-DelRU_3_1 113.332518
    all_delRU_list(3)  %sigB_biofilmpadrepeat-delRU_2_1 115.467066
    all_delRU_list(10) %sigB_biofilmfinal-DelRU_10_1 122.056002
    all_delRU_list(1)  %sigB_biofilmpad6-O001_3_1 135.156870
];

delRU_list = delRU_low_mean;

delRU_high_mean = [
    all_delRU_list(4) %sigB_biofilmpadrepeat-delRU_6_1 191.112753
    all_delRU_list(5) %sigB_biofilmpadrepeat-delRU_8_1 205.008289
];



delQP_list = [ 
       make_schitz('2015-10-30', 'sigB_biofilmpadrepeat-B_1', 1:20 )  % SIC
       make_schitz('2015-10-30', 'sigB_biofilmpadrepeat-B_3', 1:25 ) % SIC
       make_schitz('2015-10-31', 'sigB_biofilmpadrepeatrepeat1-delRU_3', 1:25) % SIC
       make_schitz('2015-11-03', 'sigB_biofilmfinal-DelQP_1' , 1:29)
       make_schitz('2015-11-03', 'sigB_biofilmfinal-DelQP_2' , 11:33) % ignored a cell
       make_schitz('2015-11-03', 'sigB_biofilmfinal-DelQP_5' , 1:35) %ignored a bright cell
       make_schitz('2015-11-03', 'sigB_biofilmfinal-DelQP_6' , 1:29) %ignored two bright cells
       %make_schitzd('sigB_biofilmfinal-DelQP_7' , 1:36)
       make_schitz('2015-11-03', 'sigB_biofilmfinal-DelQP_9' , 12:33)
];
% Means 
% sigB_biofilmfinal-DelQP_9_1 96.979010
% sigB_biofilmfinal-DelQP_5_1 105.636013
% sigB_biofilmfinal-DelQP_6_1 111.083487
% sigB_biofilmfinal-DelQP_2_1 128.622816
% sigB_biofilmfinal-DelQP_1_1 135.415739
% sigB_biofilmpadrepeat-B_1_1 166.113501
% sigB_biofilmpadrepeat-B_3_1 169.932553

sigB_list = [ 
    make_schitz('2015-10-30', 'sigB_biofilmpadrepeat-QP_1', 25:54) %SIC % ignoreing cell, has dim red cells % tracked
    %make_schitz('sigB_biofilmfinal-B_2',  1:45) Where is this?
    make_schitz('2015-11-03', 'sigB_biofilmfinal-B_3',  21:42) % SKIPED (not steady)
    make_schitz('2015-11-03','sigB_biofilmfinal-B_4',  1:39) % ignored cell
    make_schitz('2015-11-03','sigB_biofilmfinal-B_6',  21:37)
    make_schitz('2015-11-03','sigB_biofilmfinal-B_7',  1:37)
    make_schitz('2015-11-03','sigB_biofilmfinal-B_8',  1:35) % Bright non grower, but left it in.
    %make_schitz('2015-11-03','sigB_biofilmfinal-B_9',  14:37 ) % SKIPPING because its strangly dim in RFP Ignored a cell that is a bright non grower
];




% half have very high RFP levels, but consistant YFP levels, 
% but we dont want RFP histograms so I leave them in
RFPonly_list = [ 
    make_schitz('2015-10-30', 'sigB_biofilmpadrepeat-RFP_3', 1:50)        % very high RFP level 
    make_schitz('2015-10-31', 'sigB_biofilmpadrepeatrepeat1-RFP_3', 1:27) % very high RFP level 
    make_schitz('2015-10-31', 'sigB_biofilmpadrepeatrepeat1-RFP_8', 1:24) % very high RFP level 
    make_schitz('2015-11-03', 'sigB_biofilmfinal-RFP_3', 18:37) %j
    make_schitz('2015-11-03', 'sigB_biofilmfinal-RFP_5', 14:36) %j
    make_schitz('2015-11-03', 'sigB_biofilmfinal-RFP_7', 24:45) %j
    ];

delSigB_list = [
    make_schitz('2015-10-31', 'sigB_biofilmpadrepeatrepeat1-sigB_2', 1:19) % SIC
    make_schitz('2015-10-31', 'sigB_biofilmpadrepeatrepeat1-sigB_3', 1:26)% SIC
    make_schitz('2015-10-31', 'sigB_biofilmpadrepeatrepeat1-sigB_4', 1:23)% SIC
    make_schitz('2015-10-31', 'sigB_biofilmpadrepeatrepeat1-sigB_5', 1:24)% SIC
    make_schitz('2015-10-31', 'sigB_biofilmpadrepeatrepeat1-sigB_6', 1:25)% SIC
    make_schitz('2015-10-31', 'sigB_biofilmpadrepeatrepeat1-sigB_7', 1:27)% SIC
    make_schitz('2015-10-31', 'sigB_biofilmpadrepeatrepeat1-sigB_8', 1:14)% SIC
    make_schitz('2015-11-03', 'sigB_biofilmfinal-DelB_1', 1:30) %j
    make_schitz('2015-11-03', 'sigB_biofilmfinal-DelB_6', 21:37) %j
    %make_schitz('2015-11-03', 'sigB_biofilmfinal-DelB_9', 17:42) % (j hist) The RFP channel is bimodal 
    make_schitz('2015-11-03', 'sigB_biofilmfinal-DelB_10', 1:41) %j (ignoring 2 bright cells) 
]

all_list = [ delRU_list; delQP_list; sigB_list; RFPonly_list; delSigB_list ] 
