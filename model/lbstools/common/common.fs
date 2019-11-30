module Common 

open Microsoft.Research.CRNEngine
open FSharp.Collections.ParallelSeq
open System.IO

let string_of_file s = 
  printfn "Loading file: %s" s
  File.ReadAllText s

let read_single_column_sweep_file path = 
    let file = File.ReadAllLines path
    let title = Array.head file 
    let string_array = Array.tail file
    title, string_array |> Array.map (float) 
    
let write_single_column_sweep_file path var (nums: float []) = 
    let numstr = nums |> Array.map (sprintf "%f") |> Array.toList
    File.WriteAllLines(path,  var::numstr)

let parse_list_of_parameters (string_p:string) = 
    if string_p.Length = 0 
    then Map.empty
    else
        let p_list = string_p.Split [|';'|] |> Array.map (fun (pv:string) ->  (pv.Split [| '=' |]))
        let p_tuples = p_list |> Array.map (fun e -> e.[0], e.[1])
        p_tuples |> Array.map (fun (k, v) -> (k.Trim(), (float v))) |> Map.ofArray
    




let model_of_prog s =
  let possible_model, errors = Parser.from_string_find_errors Model.parse s
    
  if possible_model.IsNone then
    let errors = errors |> Seq.map (fun error -> sprintf "Line %i: %s" error.row error.text) |> (String.concat System.Environment.NewLine)
    failwithf "Failed to parse: %s%s" System.Environment.NewLine errors

  let model = possible_model.Value
  model

let model_of_path path =
  let s = string_of_file path
  model_of_prog s 

let roll a s    =
    let N = (Array.length a) - 1
    if s > 0
        then Array.concat [a.[(N-s+1)..N]; a.[0..(N-s)] ]
        else
            let x = -s
            Array.concat [a.[x..N]; a.[0..x-1]]

let col_slice (aa:float [] []) (c:int) = 
    Array.init (aa.Length) (fun r -> Array.item c (Array.item r aa))

let entry_exit_indexes_species_threshold simdata species threshold =
    //tag rows based on the threshold
    let specdata = (Table.find_column species simdata).values |> List.toArray
    // let debug_all_over_t = specdata |> Array.forall (fun s -> s > threshold)
    // printfn "All over threshodl %b" debug_all_over_t

    let try_spore_mask = specdata |> Array.map (fun x -> x >= threshold)

    // help it detect the entry phase if its the first time step
    let N = try_spore_mask.Length
    try_spore_mask.[N-1] <- false
    // or the exit if it is the last time step.
    // entry to spore_phase is True
    // System.IO.File.AppendAllLines("/tmp/test.tsv", 
    //     [ String.concat "\t" (specdata |> Array.map (fun s -> sprintf "%f" s) )
    //     ; String.concat "\t" (try_spore_mask |> Array.map (fun s -> sprintf "%d" (System.Convert.ToInt32(s)) ))])

    //ingress = simdata.index[try_spore_mask & ~ np.roll(try_spore_mask,1)]
    let ingress =
        Array.zip try_spore_mask (roll try_spore_mask 1)
            |> Array.mapi (fun i x -> i, x )
            |> Array.filter (fun (i, (a,b)) -> a && (not b))
            |> Array.map (fun (i, _) -> i)
    //printfn "Array: %A" ingress
    // exit of spore phase is True
    //egress_mask = try_spore_mask & ~ np.roll(try_spore_mask,-1)
    let egress_mask =
        Array.zip try_spore_mask (roll try_spore_mask -1)
            |> Array.map (fun (a,b) -> a && (not b) )

    if (specdata.[N-1] > threshold ) && egress_mask.[N-2]
        then
            //shift the ending to the true location to compensate for the false ending we put in the second line
            egress_mask.[N-2] <- false
            egress_mask.[N-1] <- true
    //egress = sim.index[egress_mask]
    let egress =
        egress_mask |> Array.mapi (fun i x -> i, x)
                    |> Array.filter (fun (i, x) -> x)
                    |> Array.map (fun (i, _) -> i)

    Array.zip ingress egress
        |> Array.filter ( fun (i,e) -> e > i )

let peak_stats simdata species threshold =
    let entry_exit = entry_exit_indexes_species_threshold simdata species threshold
    //entry_exit |> Array.iter (fun (a,b) -> printfn "(%i, %i)" a b)
    let durations = entry_exit
                    |> Array.map (fun (i, e) -> simdata.times.[e] - simdata.times.[i])
    let column = (Table.find_column species simdata).values |> List.toArray
    let peaks = entry_exit
                    |> Array.map (fun (i, e) -> Array.max(column.[i..e]))
    durations, peaks

//let do_sweep (rng:System.Random) (crn:Crn.t) (sweep_inst:Instance.t) (measure_spec:string) threshold reps  =
let do_sweep (rng:System.Random) (crn:Crn) env_to_run measure_spec threshold reps  =
    //let threshold = sweep_inst.environment.["A0"] + 2.0
    printfn "Doing Sweep %s" (Environment.to_string env_to_run ) //sweep_inst.environment)
    let do_simulation i =
        let seed = Some(rng.Next())
        let crn = crn.update_settings { crn.settings with stochastic = { crn.settings.stochastic with seed = seed } }
        let ssa = (crn.substitute env_to_run).to_ssa ()
        //printfn "%s" this_env_crn.simulator.settings.
        let sim_data = ssa.simulate ()
        //printfn "Sim done! times %s" (sim_data.times.ToString ())
        let durs, peaks = peak_stats sim_data measure_spec threshold
        let durs = if Array.isEmpty durs then [| 0.0 |] else durs
        let peaks = if Array.isEmpty peaks then [| 0.0 |] else peaks
        //printfn "Summary: durs %A" durs
        let sweep_params = (env_to_run |> Map.toList )
        Array.zip durs peaks
            |> Array.map (fun (d,p) -> sweep_params, i, d, p) // should extract the value from the map? 
            |> Array.toList

    List.concat (PSeq.init reps do_simulation)

let trapz (x:float [] ) (fx:float []) =
  let trapz_areas = Array.init (x.Length-1) (fun i -> 0.5 * (x.[i+1] - x.[i]) * (fx.[i+1] + fx.[i])) 
  (Array.fold (+) 0.0 trapz_areas ) / x.[x.Length-1] 

let rec skip n xs = 
    match (n, xs) with
    | 0, _ -> xs
    | _, [] -> []
    | n, _::xs -> skip (n-1) xs

// For some reason cannot get this function from CRNEngine.Inference
let log_of_normal_density (x,m,s) = 
  let sqrt2pi = sqrt(2.0*System.Math.PI) in
  let h1 = ((x-m)/s) in
  let p1 = -0.5 * h1 * h1 in
  let p2 = s * sqrt2pi in
  p1 - log(p2)

let shuffle array = 
  let rnd = System.Random()
  array |> Array.sortBy (fun _ -> rnd.NextDouble() )

let update_list old_list new_list = 
    let old_map = Map.ofList old_list
    new_list |> List.fold (fun res_list (k, v) -> Map.add k v res_list) old_map
             |> Map.toList

let update_map old_map new_map = 
    new_map |> Map.fold (fun res_list k v -> Map.add k v res_list) old_map

let initials_of_list pair_list = 
    let new_init (k, v) = Initial.create (Expression.Float v, Species.create k, Expression.Float 0.0, None)
    pair_list |> List.map new_init 

let update_initials (crn:Crn) (new_initials:Initial<Species,Value> list) = 
    let old_inits = crn.initials
    let old_init_map = old_inits |> List.map (fun i -> i.species.name, i) |> Map.ofList 
    let new_init_map = new_initials |> List.map (fun i -> i.species.name, i) |> Map.ofList

    let updated_inits = update_map old_init_map new_init_map |> Map.toList |> List.map snd
    { crn with initials = updated_inits}


let set_sim_times (crn:Crn) final points = 
    let new_times = { crn.settings.simulation with final = final; points = points } 
    crn.update_settings { crn.settings with simulation = new_times }

let set_sim_time  final points (crn:Crn) = 
    let new_times = { crn.settings.simulation with final = final; points = points } 
    crn.update_settings { crn.settings with simulation = new_times }


let update_seed nseed (crn:Crn) = crn.update_settings { crn.settings with stochastic = { crn.settings.stochastic with seed = nseed} }
    
let run_ssa nseed (crn:Crn)  = 
    //let ntcrn = set_sim_times crn 1e6 (int 1e6 )
    let crn = crn.update_settings { crn.settings with stochastic = { crn.settings.stochastic with seed = nseed} }
    let ssa = crn.to_ssa ()
    ssa.simulate ()

let run_with_env seed (crn:Crn) env = 
    let this_env_crn = crn.substitute env
    run_ssa seed this_env_crn


let update_crn_with_parameters p (crn:Crn) = crn.substitute p

let run_with_parameters seed (crn:Crn) p = 
    run_ssa seed <| update_crn_with_parameters p crn 

let rec find_check_time tlist target index = 
    match tlist with
    | head::neck::tail -> if ((head < target) && (neck > target))
                                then target::neck::tail, index 
                          elif (head < target) && (neck = target) 
                                then neck::tail, (index+1)
                          elif (head < target) && (neck < target) 
                                then find_check_time (neck::tail) target (index+1)
                          else failwith (sprintf "head %f is greater than target %f" head target)
    | [ head ] -> if head <= target then [target], index 
                  else failwith "head is bigger than target and I dont know what to do"
    | [ ] -> [], 0

let test_find_check_time() = 
    let x = [ 0.0; 1.0; 2.0; 3.0; 4.0] 
    let target = 1.5
    ([1.5; 2.0; 3.0; 4.0], 1) = (find_check_time x target 0)
    let same_target = 2.0
    ([2.0; 3.0; 4.0], 2) = (find_check_time x same_target 0)
    let bad_list = [ 1.0 ]
    let high_target = 1.5
    ([1.5], 0) = (find_check_time bad_list high_target 0)

let drop_transience (table:Table<'v>) first_time =
    let new_times, discard_num = find_check_time table.times first_time 0
    let new_table:Table<'v> = 
        { times = new_times
          columns = table.columns |> List.map (fun (c:Column<'v>) -> 
                                                    {name = c.name;
                                                     values = (skip discard_num c.values)})
        }
    new_table
        
let set_plot_species (spec: string []) (crn:Crn) = 
     let speclist = spec |> Array.map (fun s -> Expression.Key (Key.Species (Species.create s))) |> Array.toList
     { crn with settings = {crn.settings with simulation = { crn.settings.simulation with plots = speclist}}}

// Here is a natsty imperitive function Neil wrote 
// I am not sure how it is setting the maxima so I am 
//leaving it here. attempts to replace it are above. 
let set_populations_maxima (crn:Crn) (populations:Populations<Species,float>) (maxima:Map<string,int>) = 
  crn.settings.simulation.plots 
    |> List.iter (fun x -> 
        let sp = match x with Expression.Key (Key.Species k) -> k | _ -> failwith "Can't handle arbitrary expressions"
        populations.set_max populations.species_to_index.[sp] (Map.tryFind sp.name maxima)
    )
    // let plots_need_max = 
    //     crn.settings.simulation.plots 
    //     |> List.map (fun p -> 
    //     match p with 
    //     | Expression.Key x -> Expression.Key {x with max = Some (species_maxes.[x.name])}
    //     | _ -> p)

// given a target float and a list of  sorted floats 
// this function finds the index of the first float
// in the list that is less than the target float
// it also returns the list and index so that you
// can use it to search for more targets without 
// going through the list again.
let rec get_index_of_sample target (index, s_list) =
    let retail = List.tail s_list 
    match s_list with 
        | head::shoulder::torso -> 
            if target >= head && target < shoulder 
                then index, s_list
                else get_index_of_sample target (index + 1, retail)
        | [head] -> index, []
        | _ -> index, [] // should never be matched 

// let get_index_of_sample_test() = 
//     let data_times = List.concat [[ 0.0 ]; List.init 20 (fun i -> 0.5 + (float i))]
//     let target = 0.1
//     let found, leftover = get_index_of_sample target (0, data_times)
//     let value = List.item found data_times
//     ()

let rate_to_strings rate : string list =
    match rate with
      | Rate.MassAction( mar ) -> Expression.mentions mar                                       
      | Rate.Function e        -> Expression.mentions e 
                                    |> List.map (fun s -> 
                                        match s with 
                                          | Key.Parameter(p) -> p 
                                          | _ -> "")  


// given a CRN, this extracts the parameters in the reactions so you dont need to specify them 
// in the parameters section.
let params_from_crn (crn:Crn) = 
  let rates = List.concat [ List.map (fun r -> r.rate ) crn.reactions
                          ; List.map (fun r -> r.reverse) crn.reactions |> List.choose id
                          ]
  rates |> List.collect rate_to_strings |> List.distinct |> List.filter ((=) "" >> not) 
  
let crn_no_params prog_text = 
    let crn = prog_text 
                |> model_of_prog
                |> (fun m -> m.top :: m.systems) 
                |> List.head 
    let prams = crn |> params_from_crn
                    |> List.map (fun i -> (i, 0.0) )
                    |> Map.ofList
    let orig_params = Parameter.to_env crn.settings.parameters
    let new_params = update_map prams orig_params 
    let new_plist = new_params |> Map.toList |> List.map (fun (k, v) -> Parameter.create (k, v, None) )
    let new_settings = { crn.settings with parameters = new_plist } 
    crn.update_settings new_settings
    

let get_rows (samples: float list) (data:float list) = 
    let value_list_pairs = samples |> List.scan (fun (si, sl) t -> get_index_of_sample t (si, sl)) (0, data) 
    value_list_pairs |> List.tail |> List.map fst

let test_get_rows () = 
    let random_sample_of_times = List.init 10 (fun i -> 2.0 * (float i))
    let data_times = List.concat [[ 0.0 ]; List.init 20 (fun i -> 0.5 + (float i))]
    let rows_sampled = get_rows random_sample_of_times data_times
    [0; 2; 4; 6; 8; 10; 12; 14; 16; 18] |> List.map2 (fun a b -> a = b) rows_sampled 

    // test that it works if there is a long sparse zone in the search list
    let regular_times = List.init 24 float 
    let low_sampled_data = [ 0.0; 1.0; 20.0; 21.0; 22.5] 
    let rows_sampled = get_rows regular_times low_sampled_data
    List.concat [ [ 0 ];  List.init 19 (fun _ -> 1) ; [ 2; 3; 3; 4]] 
        |> List.map2 (fun a b -> a = b) rows_sampled 
    ()


let resample new_points column = 
    let acol = column |> List.toArray
    new_points |> List.map (fun i -> Array.item i acol)

let resample_column times column new_time = 
    let new_index = get_rows new_time times
    resample new_index column

let read_in_2darray sep path =  
    let str_array = System.IO.File.ReadAllLines(path)
    let sigbdata = str_array |> Array.map (fun (l:string) -> (l.Split [| sep |]) |> Array.map float) 
    sigbdata

let array_add (array:uint64 []) pos (v:uint64) = 
    array.[pos] <- array.[pos] + v 
    ()


let simulate_stationary ssa = 
    Ssa.simulate_with_stationary (Ssa.set_number_of_points 1 ssa)

let get_plot_indices_max pops (plots:Expression.t<Inlined<int>> list) = 
  plots 
  |> List.map (fun p -> 
    match p with 
    | Expression.Key (Inlined.Species index) -> 
      match pops.index_to_species.[index].max with
        | Some max -> index, max 
        | None -> failwithf "No maximum specified for plot species %s" pops.index_to_species.[index].species.name
    | _ -> failwithf "Currently do not support expressions"
  )

let get_plot_indices plots = 
  plots
  |>  List.map (fun p -> 
    match p with 
    | Expression.Key (Inlined.Species index) -> index
    | _ -> failwithf "Currently do not support expressions"
  )

let get_threshold_value (env:Map<string,float>) percentile = 
    let transrate = ((Map.find "stress" env) * (Map.find "pscale_a" env) * (Map.find "a0" env)) + (Map.find "ascale_a" env)
    printf "%A" [| (Map.find "stress" env) ; (Map.find "pscale_a" env) ; (Map.find "a0" env) ; (Map.find "ascale_a" env) |]
    let translation = Map.find "trA" env
    let rna_deg = Map.find "dm" env
    let prot_deg = Map.find "dp" env

     //printfn "about to do gamma %g %g" (transrate/prot_deg)  (translation/rna_deg)
    //printfn "about to do gamma %g %g" (max 0.0 (transrate/5e-3)) (min 0.0  (0.005/0.05))
    let threshold = MathNet.Numerics.Distributions.Gamma.InvCDF(transrate/prot_deg, rna_deg/translation, percentile)
    //let threshold = 0.0
    let realthresh = if threshold = infinity 
                     then 0.0
                     else threshold
    realthresh

let save_row file_path (row:Map<string,string>) = 
    //printfn "%A" row
    if not (System.IO.File.Exists file_path) then 
        System.IO.File.WriteAllLines(file_path, [ row |> Map.toArray |> Array.map fst |> String.concat "\t" ] ) |> ignore
        System.IO.File.AppendAllLines(file_path, [ row |> Map.toArray |> Array.map snd |> String.concat "\t" ]) |> ignore
    else 
        System.IO.File.AppendAllLines(file_path, [ row |> Map.toArray |> Array.map snd |> String.concat "\t" ]) |> ignore
    row

let array2d_to_string array = 
    array |> Array.map (fun row -> row |> Array.map (fun e -> sprintf "%e" e)
                                       |> String.concat "\t") 
          |> String.concat "\n"

// let get_id_max_of_spec_name spec_name pops = 
//      Populations.tryFind_species pops spec_name 
let get_list_ind_max species_groups (pops:Populations<Species, float>)  (plots:Expression.t<Inlined<int>> list) =
    let plot_reps_spec_name spec_list plot =
        match plot with 
        | Expression.Key (Inlined.Species index) -> Array.contains pops.index_to_species.[index].species.name spec_list
        | _ -> false
        
    let plots_groups = species_groups 
                        |> Array.map (fun spec_list -> plots |> List.toArray |> Array.filter (plot_reps_spec_name spec_list))

    plots_groups |> Array.map (fun plot_group -> get_plot_indices_max pops (plot_group |> Array.toList) |> List.toArray) 

let species_names_to_pop_index species_list  (pops:Populations<Species, float>) =
    species_list |> Array.map (fun name -> pops.species_to_index.[Species.create name])



let ssa_update_skip_time (skip_time:float) (ssa:Ssa) =
     { ssa with settings = {ssa.settings with stationary_skiptime = Some skip_time} }

let crn_update_skip_time (skip_time:float) (crn:Crn) =
    let nsettings = { crn.settings with stochastic = { crn.settings.stochastic with stationary_skiptime = Some skip_time}}
    crn.update_settings nsettings

/// Get the A vs B probability distribution (for quasi potential)
let get_quasi_potential  (species_groups:string [][]) (ssa:Ssa)=
  let cancel = ref false 
  if (species_groups.Length > 2) || (species_groups.Length < 2)
  then failwith "Only doing 2x2 quasi potentials"
  // Prepare for outputting the stationary distribution
  let skip_time = match ssa.settings.stationary_skiptime with Some v -> v | None -> ssa.simulator.settings.initial
  let pops = ssa.simulator.populations 

  let spec_list_ind_max = get_list_ind_max species_groups pops (ssa.plots |> Array.toList)
  let Ainds, Amaxs = Array.item 0 spec_list_ind_max |> Array.unzip
  let Binds, Bmaxs = Array.item 1 spec_list_ind_max |> Array.unzip
  let Amax = Array.sum Amaxs
  let Bmax = Array.sum Bmaxs
  //printfn "A %i %i" Aind Amax
  //printfn "B %i %i" Bind Bmax
  let mutable distribution_2d = Array.init (Amax + 1) (fun _ -> Array.zeroCreate<double> (Bmax + 1))
  let mutable total_time = 0.0
  let mutable prev_pops = ssa.simulator.populations
  let update_distribution t dt (pops:Populations<Species, float>) = 
    if (t > skip_time)
    then
      total_time <- total_time + dt;
      let vA = Ainds |> Array.map (fun i -> prev_pops.index_to_species.[i].value) |> Array.sum |> int
      let vB = Binds |> Array.map (fun i -> prev_pops.index_to_species.[i].value) |> Array.sum |> int
      if vA <= Amax && vB <= Bmax then
          distribution_2d.[vA].[vB] <- distribution_2d.[vA].[vB] + dt
    prev_pops <- pops

  let final_sim = ssa.simulate_callback cancel (ignore) ignore (Some update_distribution)

  let final_distribution = distribution_2d |> Array.map (fun row -> row |> Array.map (fun e -> e/total_time))
  printfn "total %f " (final_distribution |> Array.map (fun row -> row |> Array.sum ) |> Array.sum)
  final_sim, species_groups, final_distribution

let biofilm_simulation compute_residency (ssa:Ssa): (Ssa * int * int * float list * float list) =
  let cancel = ref false 
  let skip_time = match ssa.settings.stationary_skiptime with Some v -> v | None -> ssa.simulator.settings.initial
  let species = [| "A"; "B"|]

  let Aind = ssa.simulator.populations.species_to_index.[Species.create species.[0]]
  let Bind = ssa.simulator.populations.species_to_index.[Species.create species.[1]]
  
  let mutable total_time = 0.0
  //let mutable sigB = 0 
  let mutable maxA = 0
  let residencyA = ref []
  let residencyB = ref []
  let mutable Aresident = false
  let mutable Bresident = false
  let mutable residency_timer = 0.0
  let update_distribution t dt (pops:Populations<Species, float>) = 
    if (t > skip_time)
    then
      let vA = int (pops.index_to_species.[Aind].value)
      if vA > maxA then 
        maxA <- vA  // get the max spo0A value 
      if compute_residency then 
        let vB = int (pops.index_to_species.[Bind].value)
        residency_timer <- residency_timer + dt;
        if (vA > vB) then 
            if Bresident then 
                residencyB := residency_timer::!residencyB
            residency_timer <- 0.0
            Aresident <- true
            Bresident <- false
        elif (vB > vA) then 
            if Aresident then 
                residencyA := residency_timer::!residencyA
            residency_timer <- 0.0
            Aresident <- false
            Bresident <- true

  let final_sim = ssa.simulate_callback cancel ignore ignore (Some update_distribution)
  let sigB = int (final_sim.simulator.populations.index_to_species.[Bind].value)
  final_sim, sigB, maxA, !residencyA, !residencyB


let biofilm_simulation_thresh_time threshold (ssa:Ssa) =
  let cancel = ref false 
  let skip_time = match ssa.settings.stationary_skiptime with Some v -> v | None -> ssa.simulator.settings.initial
  let species = [| "A"; "B"|]

  let Aind = ssa.simulator.populations.species_to_index.[Species.create species.[0]]
  let Bind = ssa.simulator.populations.species_to_index.[Species.create species.[1]]
  
  let mutable total_time = 0.0
  let mutable temp_maxA = 0 
  let mutable maxA = 0 
  let mutable sigB = 0 
  let mutable residencyA = 0.0
  let mutable residency_timer = 0.0
  let update_distribution t dt (pops:Populations<Species, float>) = 
    if (t > skip_time)
    then
      let vA = int (pops.index_to_species.[Aind].value)
      if vA > threshold then 
            residency_timer <- residency_timer + dt 
            if vA > temp_maxA then 
                temp_maxA <- vA  
      elif vA <= threshold then  
            if residency_timer > residencyA then 
                residencyA <- residency_timer
                maxA <- temp_maxA
            residency_timer <- 0.0
            temp_maxA <- 0

  let final_sim = ssa.simulate_callback cancel ignore ignore (Some update_distribution)
  let sigB = int (final_sim.simulator.populations.index_to_species.[Bind].value)
  final_sim, sigB, maxA, residencyA

let online_stats (ssa:Ssa) =
  let cancel = ref false 
  let skip_time = match ssa.settings.stationary_skiptime with Some v -> v | None -> ssa.simulator.settings.initial
  let species = "A"

  let Aind = ssa.simulator.populations.species_to_index.[Species.create species]
  // Running STD method
  // http://www.johndcook.com/standard_deviation.html
  
  let mutable num = 0
  let mutable rmean = 0.0
  let mutable rstd = 0.0
  let update_stats t _ pops =
    if (t > skip_time)
    then
      num <- num + 1
      let vA = pops.index_to_species.[Aind].value
      let dif = vA - rmean 
      rmean <- rmean + dif/(float num)
      rstd <- (rstd + dif*(vA - rmean))

  let final_sim = ssa.simulate_callback cancel ignore ignore (Some update_stats)
  final_sim, rmean, sqrt(rstd/(float (num - 1)))
