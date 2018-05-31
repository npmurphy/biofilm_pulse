
run file_lists.m

base = '/home/nmurphy/SLCU/teamJL/Niall/bfpulse_paper_data/datasets/padmovies_brightfield/traces/';

yfp_blank = 9.6431; 
[sigB_list.yfpOffset]=deal(yfp_blank);
[delRU_list.yfpOffset]=deal(yfp_blank);
%[delSigB_list.yfpOffset]=deal(yfp_blank);
[delQP_list.yfpOffset]=deal(yfp_blank);

p_delRU = delRU_list(5); 
p_delQP = delQP_list(8);
p_sigB =  sigB_list(3);


export_schnitz_to_tracks(p_delRU, [base 'delru.tsv']);
export_schnitz_to_tracks(p_delQP, [base 'delqp.tsv']);
export_schnitz_to_tracks(p_sigB, [base 'sigb.tsv']);


