

//base_dir="/Users/npm33/bf_pulse/proc_data/iphox_movies/";
//base_dir="/media/nmurphy/BF_Data_Orange/proc_data/iphox_movies/";
//base_dir="/media/nmurphy/BF_Data_Orange/proc_data/iphox_movies/";
base_dir="/media/nmurphy/BF_Data_Orange/raw_data/iphox_movies";
//data_dir="/Biofilm_movie_04_02_2019/";
data_dir="/Biofilm_delF_movie_07_03_2019/";
//data_dir="/Biofilm_movie_2xQP_test/Movie";
call("java.lang.System.gc")
moviedir="Column_4"
//moviedir="Position014"
version=""
//pattern =  "(_t(.*)_ch" + chan[c] + ")";
pattern =  "(_(.*)_ch" ;

//chan = newArray( "r", "g", "y" );
chan = newArray(  "00", "01", "02" );
numchans = 2;

merge_line = ""
for (c = 0; c < numchans; c++){
	moviepath = base_dir + "/" + data_dir + "/" + moviedir ;
	
    regex = pattern + chan[c] + ")";
	//print(regex);
	//print("open=[" + moviepath+ "] file=[" +regex + "] sort");
	run("Image Sequence...", "open=[" + moviepath+ "] number=380 file=[" +regex + "] sort");
	rename(chan[c]);
  merge_line = merge_line + "c" + toString(c+1) + "=" + chan[c] + " ";
}

run("Merge Channels...", merge_line + "create");
selectWindow("Composite"); 
rename(moviedir);
run("Re-order Hyperstack ...", "channels=[Channels (c)] slices=[Frames (t)] frames=[Slices (z)]");
