module custom_sweeper

open Microsoft.Research.CRNEngine
open System.IO
open Argu
open FSharp.Collections.ParallelSeq


type CliArguments =
    | Multicore
    | Simulations of int
    | Seed of int 
    | Output_name of string
    | Sweep_file of string option 
    | Parameters_file of string option
    | Parameter_overrides of string
    | Analysis_method of string
with
    interface IArgParserTemplate with
        member s.Usage = 
            match s with
            | Multicore     -> "Process different files using multiple cores (if possible)."
            | Simulations _ -> "Set the number of simulation runs to perform."
            | Seed _ -> "Initialisation seed"
            | Output_name _ -> "name of output file"
            | Sweep_file _ -> "path to file containing the sweep"
            | Parameters_file _ -> "a path to a directive parameters file"
            | Parameter_overrides _ -> "a semicolon separated list of paramters to override in this run "
            | Analysis_method _ -> "name of the fuction analyse the simulations"

let get_chosen_env_entry env_headings env = 
    let env_p = env |> Map.filter (fun k v -> Array.contains k env_headings) |> Map.toArray
    env_p |> Array.map (fun (k,p) -> k , sprintf "%f" p)


//////////////////////////////
// Deterministic
let do_determinist_spore env_heading (incrn:Crn) env thresholds sweep_env = 
    let new_params = Common.update_map env sweep_env
    let crn = incrn |> Common.set_sim_time 5000.0 3
    let ode = (crn.substitute new_params).to_ode ()
    //let results = Ode.simulate_sundials ode
    let results = ode.to_oslo().simulate()
    let A = List.last (Table.find_column "A" results).values
    let B = List.last (Table.find_column "B" results).values
    [| Array.concat [ get_chosen_env_entry env_heading new_params
                 ; [| ("A", sprintf "%f" A); ("B", sprintf "%f" B) |] ] 
                 |> Map.ofArray |]
// End deterministic 
//////////////////////////////

///////////////////////////
// Biofilm sim take II. time over percentile 
let get_common_bf_sporeprob_sim_func_threshtime (incrn:Crn) env sweep_env = 
    let new_params = Common.update_map env sweep_env
    let crn  = incrn.substitute new_params 
    printfn "thresh %f" new_params.["threshold"]
    let threshold = int new_params.["threshold"]
    let do_simulation seed i =
        let seeded = crn |> Common.update_seed seed 
        let _, sigB, maxA, a_time = seeded.to_ssa () |> Common.biofilm_simulation_thresh_time threshold 
        maxA, a_time, sigB 
    new_params, do_simulation

let do_biofilm_sim_threshtime env_heading (rng:System.Random) (incrn:Crn) (env:Map<string,float>) simulations sweep_env = 
    let transrate = ((Map.find "stress" sweep_env) * (Map.find "pscale_a" env) * (Map.find "b0" env)) + (Map.find "ascale_a" env)
    //printfn "about to do gamma %g %g" (transrate/5e-3)  (0.005/0.05)
    //printfn "about to do gamma %g %g" (max 0.0 (transrate/5e-3)) (min 0.0  (0.005/0.05))
    //let threshold = MathNet.Numerics.Distributions.Gamma.InvCDF((transrate/5e-3), (0.005/0.05), 0.2)

    let realthresh =  Common.get_threshold_value (Common.update_map env sweep_env) 0.2
    
    //printfn "thrfdsesh %f" threshold
    let wthres = Map.add "threshold" realthresh env
    //printfn "thresh %f" wthres.["threshold"]
    let new_params, do_simulation = get_common_bf_sporeprob_sim_func_threshtime incrn wthres sweep_env
    let collect_results list_of_results = 
        list_of_results 
            |> Array.map (fun (sim_id, seed, (maxA, atime, sigB)) -> 
                Array.concat [
                    get_chosen_env_entry env_heading new_params
                    ; [| ("Amax", sprintf "%i" maxA); 
                         ("Atime", sprintf "%f" atime); 
                         ("Bsamp", sprintf "%i" sigB); 
                         ("seed", sprintf "%i" seed); 
                         ("sim_id", sprintf "%i" sim_id) |] ]
                        |> Map.ofArray)
        
    let timer = System.Diagnostics.Stopwatch()
    timer.Start()
    let str = Seq.init simulations (fun i -> i, rng.Next())
                |> Seq.map (fun (i,r) -> i, r, (do_simulation (Some r) i))
                |> Seq.toArray
                |> collect_results
    timer.Stop()
    printfn "Doing %i sims took %f minutes Map %A" simulations (timer.Elapsed.TotalMinutes) (sweep_env |> Map.toArray)
    str

let summarise_simulations_threshspore (thresh_vals:float[]) (num_sims:int) (results_of_lots_of_sims:(int*float*int)[]) = 
    let maxAs, (atimes:float[]), sigBs = Array.unzip3 results_of_lots_of_sims
    let bmean = sigBs |> Array.averageBy (float)
    let AmaxMean = maxAs |> Array.averageBy (float)
    let atimemax = atimes |> Array.max
    let atimemin = atimes |> Array.min
    let atimemean = atimes |> Array.average
    let find_percent n (t:float) alist = 
        (alist |> Array.sumBy (fun a -> if a >= t then 1.0 else 0.0)) / (float n)
    let Apercents = thresh_vals |> Array.map (fun t -> find_percent num_sims t atimes)
    AmaxMean, atimemax, atimemin, atimemean, bmean, Apercents

let do_percentage_chance_spore_thresh env_heading (rng:System.Random) (incrn:Crn) env simulations (threshold_times:float[]) sweep_env = 
    let new_params, do_simulation = get_common_bf_sporeprob_sim_func_threshtime incrn env sweep_env

    let turn_into_stringmap amean atimemax atimemin atimemean bmean percents =
        Array.concat [
             get_chosen_env_entry env_heading new_params
            ; [| ("mean_Amax", sprintf "%f" amean);
                 ("mean_Atime", sprintf "%f" atimemean);
                 ("max_Atime", sprintf "%f" atimemax);
                 ("min_Atime", sprintf "%f" atimemin);
                 ("mean_Bfinal", sprintf "%f" bmean); |]
            ; Array.map2 (fun t p -> (sprintf "time>=%.2f" (t/3600.0)), (sprintf "%f" p))  threshold_times percents 
        ] |> Map.ofArray
        
    let timer = System.Diagnostics.Stopwatch()
    timer.Start()
    let str = Seq.init simulations (fun i -> do_simulation (Some(rng.Next())) i)
                |> Seq.toArray
                |> (summarise_simulations_threshspore threshold_times simulations)
                |> (fun (a,b,c,d,e,f) -> turn_into_stringmap a b c d e f)
    timer.Stop()
    printfn "Doing %i sims took %f minutes Map %A" simulations (timer.Elapsed.TotalMinutes) (sweep_env |> Map.toArray)
    [| str |]

// End of biofilm sim take II. 
////////////////////////


//////////////////////////////
// Biofilm Sim 
let get_common_bf_sporeprob_sim_func (incrn:Crn) env sweep_env = 
    let new_params = Common.update_map env sweep_env
    let crn  = incrn.substitute new_params 

    let do_simulation seed i =
        let seeded = crn |> Common.update_seed seed         
        let _, sigB, maxA, _, _ = seeded.to_ssa () |> Common.biofilm_simulation false
        maxA, sigB 
    new_params, do_simulation

let do_biofilm_sim env_heading (rng:System.Random) (incrn:Crn) env simulations sweep_env = 
    let new_params, do_simulation = get_common_bf_sporeprob_sim_func incrn env sweep_env
    let collect_results list_of_results = 
        list_of_results 
            |> Array.map (fun (sim_id, seed, (maxA, sigB)) -> 
                Array.concat [
                    get_chosen_env_entry env_heading new_params
                    ; [| ("Amax", sprintf "%i" maxA); 
                         ("Bsamp", sprintf "%i" sigB); 
                         ("seed", sprintf "%i" seed); 
                         ("sim_id", sprintf "%i" sim_id) |] ]
                        |> Map.ofArray)
        
    let timer = System.Diagnostics.Stopwatch()
    timer.Start()
    let str = Seq.init simulations (fun i -> i, rng.Next())
                |> Seq.map (fun (i,r) -> i, r, (do_simulation (Some r) i))
                |> Seq.toArray
                |> collect_results
    timer.Stop()
    printfn "Doing %i sims took %f minutes Map %A" simulations (timer.Elapsed.TotalMinutes) (sweep_env |> Map.toArray)
    str

// End biofilm_sim
//////////////////////////////

//////////////////////////////
// Spore probability 
let summarise_simulations thresh_vals num_sims results_of_lots_of_sims = 
    let results = results_of_lots_of_sims |> Seq.toArray
    let bmean = results |> Array.averageBy (snd >> float) 
    let Amaxes = results |> Array.map (fst >> float) 
    let AmaxMean = Amaxes |> Array.average
    let find_percent n t alist = 
        (alist |> Array.sumBy (fun a -> if a >= t then 1.0 else 0.0)) / (float n)
    let Apercents = thresh_vals |> Array.map (fun t -> find_percent num_sims t Amaxes)
    AmaxMean, bmean, Apercents

let do_percentage_chance_spore env_heading (rng:System.Random) (incrn:Crn) env simulations thresholds sweep_env = 
    let new_params, do_simulation = get_common_bf_sporeprob_sim_func incrn env sweep_env

    let turn_into_stringmap amean bmean percents =
        Array.concat [
             get_chosen_env_entry env_heading new_params
            ; [| ("mean_Amax", sprintf "%f" amean);
                 ("mean_Bfinal", sprintf "%f" bmean); |]
            ; Array.map2 (fun t p -> (sprintf "A>=%i" (int t)), (sprintf "%f" p))  thresholds percents 
        ] |> Map.ofArray
        
    let timer = System.Diagnostics.Stopwatch()
    timer.Start()
    let str = Seq.init simulations (fun i -> do_simulation (Some(rng.Next())) i)
                |> summarise_simulations thresholds simulations 
                |||> turn_into_stringmap
    timer.Stop()
    printfn "Doing %i sims took %f minutes Map %A" simulations (timer.Elapsed.TotalMinutes) (sweep_env |> Map.toArray)
    [| str |]

// End spore probability 
//////////////////////////////

let do_quasi_potential (rng:System.Random) (incrn:Crn) env simulations trans_start species_groups_maxes sweep_env = 
    //printfn "Doing Sweep %s" (sweep_env.ToString())
    let envstr = sweep_env |> Map.toList |> List.map (snd >> (sprintf "%f")) |> String.concat "\t"
    //let do_simulation seed i =
    let new_params = Common.update_map env sweep_env
    let new_run_time = (incrn.settings.simulation.final - trans_start) * (float simulations)
    let timer = System.Diagnostics.Stopwatch()
    let crn = 
        incrn 
        |> Common.set_sim_time new_run_time 0  // points not important
        |> Common.update_crn_with_parameters new_params 
        |> Common.update_seed (Some (rng.Next()))
    let runssa = crn.to_ssa () |> Common.ssa_update_skip_time trans_start
    timer.Start()
    let flat_max_list = species_groups_maxes |> Array.collect (fun mxd -> Map.toArray mxd) 
    let grouped_spec_names = species_groups_maxes |> Array.map (fun group -> (Map.toArray group) |> Array.map fst)
    // I want to do this in a functional way. I hate this set_pops_max
    Common.set_populations_maxima crn runssa.simulator.populations (Map.ofArray flat_max_list) 
    let finalssa, species, qp = runssa |> Common.get_quasi_potential grouped_spec_names
    timer.Stop()
    printfn "Doing %i sims took %f minutes Map %A" simulations (timer.Elapsed.TotalMinutes) (sweep_env |> Map.toArray)
        //let durs, peaks = Common.peak_stats sim_data spec env.["base_threshold"]
    let vallist = qp |> Array.mapi (fun r row -> row |> Array.mapi (fun c e -> sprintf "%i\t%i\t%e" r c e))
                     |> Array.collect (id)
    vallist 
    
let do_quasi_potential_headers env species = 
    List.concat [
        (env |> Map.toList |> List.map fst)
        ; species |> Array.toList 
        ; [ "probability"]]
        |> String.concat "\t"
    

//////////////////////////////
// Species Histogram stats. 
//////////////////////////////
let do_histogram (rng:System.Random) (crn:Crn) env simulations droptime spec_max sweep_env = 
    //printfn "Doing Sweep %s" (sweep_env.ToString())
    let envstr = sweep_env |> Map.map (fun k v -> (sprintf "%f" v))
    let plotspecs = spec_max |> Map.toArray |> Array.map fst

    let new_params = Common.update_map env sweep_env
    printfn "Ran Parameters [\n %s \n]" (new_params |> Map.toList |> List.map (fun (k,v) -> sprintf "%s = %f" k v) |> String.concat ";\n")
    let counted_sim_time = ((crn.settings.simulation.final - droptime) * (float simulations))
    let total_time = droptime + counted_sim_time 
    let rcrn = crn  |> Common.update_seed (Some (rng.Next()))
                    |> Common.set_sim_time total_time 1 //(int total_time)
                    |> Common.update_crn_with_parameters new_params
                    |> Common.set_plot_species plotspecs
    let make_result sweep_vals spec count percent = 
        [| ("species", spec)
         ; ("count", sprintf "%i" count)
         ; ("percent", sprintf "%f" percent) |]
          |> Map.ofArray
          |> Common.update_map sweep_vals 

    let ssa = rcrn.to_ssa () 
    let nssa = {ssa with settings = { ssa.settings with stationary_skiptime = Some droptime}}
    Common.set_populations_maxima crn nssa.simulator.populations spec_max 
    let timer = System.Diagnostics.Stopwatch()
    timer.Start()
    let _, _, stationary = Ssa.simulate_with_stationary nssa
    timer.Stop()
    printfn "Doing %i sims took %f minutes Map %A" simulations (timer.Elapsed.TotalMinutes) (sweep_env |> Map.toArray)
    stationary 
        |> Map.toArray
        |> Array.collect (fun (species, values) -> values |> Array.mapi (fun i v -> make_result envstr species i v))

//////////////////////////////
// Quick mean and std
//////////////////////////////
let do_mean_std (rng:System.Random) (crn:Crn) env simulations droptime sweep_env = 
    //printfn "Doing Sweep %s" (sweep_env.ToString())
    let envstr = sweep_env |> Map.map (fun k v -> (sprintf "%f" v))
    let new_params = Common.update_map env sweep_env
    printfn "Ran Parameters [\n %s \n]" (new_params |> Map.toList |> List.map (fun (k,v) -> sprintf "%s = %f" k v) |> String.concat ";\n")
    let counted_sim_time = ((crn.settings.simulation.final - droptime) * (float simulations))
    let total_time = droptime + counted_sim_time 
    let rcrn = crn  |> Common.update_seed (Some (rng.Next()))
                    |> Common.set_sim_time total_time 1 //(int total_time)
                    |> Common.update_crn_with_parameters new_params
    let ssa = rcrn.to_ssa () 
    let nssa = {ssa with settings = { ssa.settings with stationary_skiptime = Some droptime}}

    let make_result sweep_vals mean stdev = 
        [| 
           ("mean", sprintf "%f" mean)
         ; ("std", sprintf "%f" stdev) |]
          |> Map.ofArray
          |> Common.update_map sweep_vals 

    let timer = System.Diagnostics.Stopwatch()
    timer.Start()
    let _, mean, stdev = Common.online_stats nssa
    timer.Stop()
    [| make_result envstr mean stdev |]

[<EntryPoint>]
let main(args) =
    let parser = ArgumentParser.Create<CliArguments>()

    // Parse given input
    if (Array.length args) < 1 then 
      printf "%s" (parser.PrintUsage ()) 
    else 
      ()

    let filename = args.[0]     
    let parser_results = parser.Parse( args.[1..] , raiseOnUsage=true )
    let simulations = parser_results.GetResult( <@ Simulations @>, defaultValue = 1)
    let multicore = parser_results.Contains <@ Multicore @>
    let initseed = parser_results.GetResult( <@  Seed @>, defaultValue = (System.Random()).Next() )  

    let filepre = Path.GetFileNameWithoutExtension(filename)
    let outfile_prefix = parser_results.GetResult(<@ Output_name @>, defaultValue=filepre) 
    let outfilename = sprintf "%s %s.tsv" outfile_prefix

    // Parse the main file. 
    let base_crn = System.IO.File.ReadAllText(filename) |> Common.crn_no_params 
    let crnfile_parameters = Parameter.to_env base_crn.settings.parameters 
    
    //let spec = parser_results.GetResult(<@ Species @>, defaultValue="") 

    // Parse the parameters 
    let parameters_file = parser_results.GetResult(<@ Parameters_file @>)
    let parameter_set =
        match parameters_file with 
        | Some (scrnp) -> System.IO.File.ReadAllText(scrnp)
                                |> Crn.from_string
                                |> (fun x -> x.settings.parameters)
                                |> List.map (fun p -> p.name, (float p.value))
                                |> Map.ofList
        | None _ -> Map.empty
    printfn "Parsed parameters"

    // Get command line parameter overides 
    let parameter_overrides = parser_results.GetResult(<@ Parameter_overrides @>, defaultValue = "") 
                                |> Common.parse_list_of_parameters

    let partial_params = Common.update_map crnfile_parameters parameter_set
    let final_params = Common.update_map partial_params parameter_overrides

    printfn "Parameters to run with %A" (final_params |> Map.toArray)

    // Parse the sweep 
    let sweep_file = parser_results.GetResult(<@ Sweep_file @>, defaultValue = None)
    let sweep_instance =
        match sweep_file with 
        | Some (scrnp) -> 
            let crn = System.IO.File.ReadAllText(scrnp) |> Crn.from_string
            crn.get_instances ()
        | None -> base_crn.get_instances ()
    printfn "Parsed sweep"
    
    let sweep_envs = sweep_instance |> List.map (fun si -> si.environment) 

    let sim_time = final_params.["sim_hour"] * final_params.["sim_duration"]
    let sim_minute = final_params.["sim_minute"]
    let trans_start = final_params.["initial_skip"]
    
    let time_crn =  Common.set_sim_times base_crn sim_time (int sim_time)
                    |> Common.crn_update_skip_time trans_start 

    let seed_generator = MathNet.Numerics.Random.MersenneTwister(initseed, true)
    let thresholds = MathNet.Numerics.Generate.LinearRange(30.0, 30.0, 300.0)
    let time_thresholds = MathNet.Numerics.Generate.LinearRange(30.0*60.0, 30.0*60.0, 120.0*60.0)
    
    let sweep_head = List.head sweep_envs |> Map.toArray |> Array.map fst 

    let analysis_method = parser_results.GetResult(<@ Analysis_method @>) 
    let data_summariser =  
        match analysis_method with 
        | "spore_prob" -> do_percentage_chance_spore
                            sweep_head
                            seed_generator 
                            time_crn
                            final_params 
                            simulations
                            thresholds  
        | "biofilm_sim" -> do_biofilm_sim
                            sweep_head
                            seed_generator 
                            time_crn
                            final_params 
                            simulations
        | "bfsimthresh_prob" -> do_percentage_chance_spore_thresh
                                    sweep_head
                                    seed_generator 
                                    time_crn
                                    final_params 
                                    simulations
                                    time_thresholds  
        | "bfsim_thresh" -> do_biofilm_sim_threshtime
                             (Array.append sweep_head [|"threshold"|]) 
                             seed_generator 
                             time_crn
                             final_params 
                             simulations
        | "deterministic" -> do_determinist_spore sweep_head time_crn final_params thresholds 
        | "histogram" -> do_histogram seed_generator time_crn final_params simulations trans_start (Map.ofArray [|"A", 200|]) 
        | "stats" -> do_mean_std seed_generator time_crn final_params simulations trans_start
        | _ -> (fun env -> [| (Map.ofArray [|" ", ""|]) |])
        //| "quasipotential" -> 
        //                do_quasi_potential
        //                    seed_generator 
        //                    time_crn
        //                    final_params 
        //                    simulations
        //                    trans_start
        //                    [| Map.ofArray [| ("A",1500); ("GbA",2) |] ;
        //                       Map.ofArray [| ("B",1500); ("GaB", 2) |] |]
        //                ,
        //                do_quasi_potential_headers (List.head sweep_envs) [| "A"; "B"|]

    let outfile = parameter_overrides 
                    |> Map.toList 
                    |> List.map (fun (k,v) -> sprintf "%s=%f" k v) 
                    |> String.concat ","
                    |> outfilename 

    let XSeq_iter = 
        match multicore with
        | false -> Seq.iter 
        | true -> PSeq.iter
    
    sweep_envs
        |> List.toSeq
        |> Seq.map (fun x -> printfn "%A" x; x)
        |> XSeq_iter (data_summariser >> (fun dl -> Array.iter ((Common.save_row outfile) >> ignore) dl))

    0 //success code

