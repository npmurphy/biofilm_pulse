machine=`hostname`
if [ "$machine" = "nmurphy-laptop" ]
  then
  #rsync -arvh ~/SLCU/teamJL/Niall/biofilm_datasets/biofilm_cryoslice/LSM780_10x_sigb ./datasets/biofilm_cryoslice/
  rsync -ravh "/home/nmurphy/SLCU/teamJL/Niall/bfpulse_paper_data/datasets" "/media/nmurphy/BF_Data_Orange/"

  #--delete
elif [ "$machine" = "slpc187" ]
  then
  #rsync -ravh datasets/LSM700_63x_sigb /Volumes/data-1/TeamJL/Niall/bfpulse_paper_data/datasets/ #--delete
  rsync -ravh raw_data/ "/Volumes/Seagate Backup Plus Drive/raw_data"
  rsync -ravh proc_data/ "/Volumes/Seagate Backup Plus Drive/proc_data"
  rsync -ravh datasets/ "/Volumes/Seagate Backup Plus Drive/datasets"
else
  echo $machine
fi
#LSM700_63x_sspb_giant

#LSM780_63x_spoiid_v_sigb
