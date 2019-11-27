#I "../lib/CliCRN/"
#I "../build/"
#r "CRNEngineDotNet.dll"
#r "CliLibrary.dll"
#r "ParserCombinators.dll"
#r "Filzbach.FSharp.dll"
#r "custom_sweeper.exe"

open Microsoft.Research.CRNEngine
open Microsoft.Research.CliLibrary
open System.Diagnostics
open System.IO


let roll a s    =
    let N = (Array.length a) - 1
    if s > 0
        then Array.concat [a.[(N-s+1)..N]; a.[0..(N-s)] ]
        else
            let x = -s
            Array.concat [a.[x..N]; a.[0..x-1]]



let entry_exit_indexes_species_threshold (simdata:Table.t<float>) species threshold =
    //tag rows based on the threshold
    let times, specdata = simdata.time, simdata.data

    let try_spore_mask = specdata.[species] |> Array.map (fun x -> x > threshold)

    // help it detect the entry phase if its the first time step
    let N = try_spore_mask.Length
    try_spore_mask.[N-1] <- false
    // or the exit if it is the last time step.
    // entry to spore_phase is True

    //ingress = simdata.index[try_spore_mask & ~ np.roll(try_spore_mask,1)]
    let ingress =
        Array.zip try_spore_mask (roll try_spore_mask 1)
            |> Array.mapi (fun i x -> i, x )
            |> Array.filter (fun (i, (a,b)) -> a && (not b))
            |> Array.map (fun (i, _) -> i)

    // exit of spore phase is True
    //egress_mask = try_spore_mask & ~ np.roll(try_spore_mask,-1)
    let egress_mask =
        Array.zip try_spore_mask (roll try_spore_mask -1)
            |> Array.map (fun (a,b) -> a && (not b) )

    if (specdata.[species].[N-1] > threshold ) && egress_mask.[N-2]
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



let peak_stats (simdata:Table.t<float>) species  threshold =
    let entry_exit = entry_exit_indexes_species_threshold simdata species threshold
    entry_exit |> Array.iter (fun (a,b) -> printfn "(%i, %i)" a b)
    let durations = entry_exit
                    |> Array.map (fun (i, e) -> simdata.time.[e] - simdata.time.[i])
    let peaks = entry_exit
                    |> Array.map (fun (i, e) -> Array.max(simdata.data.[species].[i..e]))
    durations, peaks

Directory.SetCurrentDirectory(__SOURCE_DIRECTORY__)
let filename = "../../venus/SigB_sweep.crn"
//let filename = "/tmp/test.crn"
let simulations = 1
let crn = custom_sweeper.crn_of_file filename
let simulator = Crn.simulator_of_string "stochastic"
let crn = { crn with settings = { crn.settings with simulator = simulator } }
let outfilename = sprintf "%s_%s.tsv" (Path.GetFileNameWithoutExtension(filename))
let base_environment = Parameters.to_env crn.parameters
let seed_generator = System.Random()

//let ssa = Crn.to_ssa_env crn base_environment
// TODO Determine whether there are sweeps
let sweep_envs = Sweep.to_environments base_environment crn.settings.sim.sweeps

let do_sweep (sweep_inst:Sweep.instance) reps  =
    let threshold = sweep_inst.environment.["A0"] + 2.0
    let do_simulation i =
        let seed = Some(seed_generator.Next())
        let crn =  { crn with settings = { crn.settings with ssa = { crn.settings.ssa with seed = seed } } }
        let ssa, sim_data = Crn.simulate_ssa_env sweep_inst.environment crn
        let durs, peaks = peak_stats sim_data "A" threshold
        Array.zip durs peaks
            |> Array.map (fun (d,p) -> sweep_inst.sweep_pairs, i, d, p)
            |> Array.toList

    List.concat (Seq.init reps do_simulation)

let repeats = 100
let results = sweep_envs
                |> List.map (fun (si:Sweep.instance) -> (si.key.Split [|'|'|]).[0], do_sweep si repeats)

let get_data_string_list datalist =
    datalist |> List.map (fun (pairs, r, d, p) ->
                    let pst = List.map (snd >> sprintf "%f" ) pairs
                                |> String.concat "\t"
                    let line = sprintf "%s\t%i\t%f\t%f" pst r d p
                    line)



let write_data name datalist =
    File.WriteAllLines((outfilename name), (get_data_string_list datalist))

results |> List.map (fun (n,v) -> write_data n v)
