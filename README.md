# Stochastic pulsing of gene expression enables the generation of spatial patterns in Bacillus subtilis biofilms

Stochastic pulsing of gene expression can generate phenotypic diversity in a genetically identical population of cells, but it is unclear whether it has a role in the development of multicellular systems. Here, we show how stochastic pulsing of gene expression enables spatial patterns to form in a model multicellular system, Bacillus subtilis bacterial biofilms. We use quantitative microscopy and time-lapse imaging to observe pulses in the activity of the general stress response sigma factor σB in individual cells during biofilm development. Both σB and sporulation activity increase in a gradient, peaking at the top of the biofilm, even though σB represses sporulation. As predicted by a simple mathematical model, increasing σB expression shifts the peak of sporulation to the middle of the biofilm. Our results demonstrate how stochastic pulsing of gene expression can play a key role in pattern formation during biofilm development.

## Repository explanation
The code in this repository assumes you have in your local, checkout out version, a directory called `datasets`. 
The contents of this directory can be found at https://dx.doi.org/10.5281/zenodo.3544513/. 

There is also an assumed directory called `proc_data`. 
To get this data you need to contact us. 

### Segmentation Code


### Model 
Information about the computational model are found in [model/README.md](model/READ.md).

## Figures

### Figure 1
Single cells from "pad movies" were segmented and tracked using the [Schnitzcells Matlab package](http://easerver.caltech.edu/wordpress/schnitzcells/). 
The main files to generate the data for Figure 1 are `matlab_padmovies/fig1_generate_hist_data.m` and `matlab_padmovies/fig1_generate_track_data.m`. 
The resulting data can be found at `https://dx.doi.org/10.5281/zenodo.3544513/padmovies_brightfield.zip`.

From here you can generate Figure 1 by running 
```
python figures/figure_padmovies/padmovie_trace_main.py
```


### Figure 2
```
python analysis/summarise_10x_gradients.py
python figures/figure_sigb_repress_spores/sigb_vs_spore.py
```

### Figure 3
```
python figures/figure_63x_sigb_histo/make_histograms_quad.py
```
### Figure 4

### Figure 5
```
python figures/figure_sigb_repress_spores/sigb_vs_spore.py
```

### Figure 6

### Figure 7
```
 python figures/figure_allspore_2xqp_combo/figure_all_spore_sigb_combo.py
```

