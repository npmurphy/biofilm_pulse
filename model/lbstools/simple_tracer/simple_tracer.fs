module custom_sweeper

open Microsoft.Research.CRNEngine
open System.IO
open Argu

type CliArguments =
    | Seed of int 
    | Output_name of string
    | Parameters_file of string option
    | Parameter_overrides of string
with
    interface IArgParserTemplate with
        member s.Usage = 
            match s with
            | Seed _ -> "Initialisation seed"
            | Output_name _ -> "name of output file"
            | Parameters_file _ -> "a path to a directive parameters file"
            | Parameter_overrides _ -> "a semicolon separated list of paramters to override in this run "

let get_chosen_env_entry env_headings env = 
    let env_p = env |> Map.filter (fun k v -> Array.contains k env_headings) |> Map.toArray
    env_p |> Array.map (fun (k,p) -> k , sprintf "%f" p)



let do_stochastic_simulation (incrn:Crn) new_params = 
    //let crn = { incrn with settings = { incrn.settings with simulator = Crn_settings.Oslo } }
    let results = (incrn.substitute new_params).to_ssa().simulate()
    results 


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
    let initseed = parser_results.GetResult( <@  Seed @>, defaultValue = (System.Random()).Next() )  

    let filepre = Path.GetFileNameWithoutExtension(filename)
    let outfile_prefix = parser_results.GetResult(<@ Output_name @>, defaultValue=filepre) 
    let outfilename = sprintf "%s|%s.tsv" outfile_prefix

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

    let sim_time = final_params.["sim_hour"] * final_params.["sim_duration"]
    let sim_minute = final_params.["sim_minute"]
    let trans_start = final_params.["initial_skip"]
    
    let time_crn =  Common.set_sim_times base_crn sim_time (int sim_time)
                    |> Common.crn_update_skip_time trans_start 

    let seed_generator = MathNet.Numerics.Random.MersenneTwister(initseed, true)
    
    let sim_result = do_stochastic_simulation time_crn final_params

    let outfile = parameter_overrides 
                    |> Map.toList 
                    |> List.map (fun (k,v) -> sprintf "%s=%f" k v) 
                    |> String.concat ","
                    |> outfilename 
    
    printfn "Threshold would be %f" (Common.get_threshold_value final_params 0.2)
    let text_conts = sim_result |> Table<float>.to_tab_separated_CSV 
    System.IO.File.WriteAllText(outfile,  text_conts) |> ignore

    0 //success code

