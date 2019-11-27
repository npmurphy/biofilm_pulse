#I "../lib/CliCRN/"
#I "../build/"
#r "CRNEngineDotNet.dll"
#r "CliLibrary.dll"
#r "ParserCombinators.dll"
//#r "Filzbach.FSharp.dll"
//#r "custom_sweeper.exe"

open Microsoft.Research.CRNEngine
open Microsoft.Research.CliLibrary
open System.Diagnostics
open System.IO


Directory.SetCurrentDirectory(__SOURCE_DIRECTORY__)

let string_of_file s =
  Io.println ("Loading file: " + s);
  Io.read_file s
let model_of_file path =
  let s = string_of_file path
  let possible_model, errors = Parser.from_string_find_errors Model.parse s
    
  if possible_model.IsNone then
    let errors = errors |> Seq.map (fun error -> sprintf "Line %i: %s" error.row error.text) |> (String.concat System.Environment.NewLine)
    failwithf "Failed to parse: %s%s%s" path System.Environment.NewLine errors

  let model = possible_model.Value
  model

//let filename = "../../venus/SigB_sweep.crn"
let filename = "../../venus/parameter_sensititivity_tra.crn"
let model = model_of_file filename

let simulator = Crn_settings.SSA //parse_simulator "stochastic"
let model = { model with settings = { model.settings with simulator = simulator } }
    //let base_environment = Parameter.to_env model.settings.parameters
let seed_generator = System.Random()
let settings = model.settings
let sweeps = settings.sweeps.
Sweep.environment sweeps

let systems = model.systems
let crn = List.head systems

let sweep_instances = Crn.get_instances crn 

let ist = List.head sweep_instances
Map.Values ist.environment

Map.toArray sweep_instances.Head.environment |> sprintf (fun -> "

System.IO.File.WriteAllText("/tmp/model.json", model)

let base_environment = Parameters.to_env crn.parameters
let seed_generator = System.Random()

  let programName = Path.GetFileNameWithoutExtension key
  let programDir = Path.GetDirectoryName key
  let outDir = Path.Combine(programDir, programName + "_simulation")
  Directory.CreateDirectory outDir |> ignore
  
  Model.simulate model
  |> Seq.groupBy (fun r -> (r.instance.model, r.instance.sweep))
  |> Seq.iter (fun ((modelname,sweep),rs:Result.t<float> seq) ->
      let simDir = 
        if modelname = "" 
        then if sweep = "" then outDir else Path.Combine (outDir,sweep)
        else if sweep = "" then Path.Combine (outDir, modelname) else Path.Combine (outDir, modelname + "_" + sweep)

      let simulatorStr = Crn_settings.simulator_to_string model.settings.simulator
      let filenames = 
        if (Seq.length rs) = 1
        then seq { yield simDir + ".tsv" }
        else rs |> Seq.map (fun r -> simDir + "_" + env_to_string r.instance.environment + ".tsv") 

      let contents = rs |> Seq.map (fun r -> Table.to_string "\t" string r.table)
      Seq.iter2 Io.write_file filenames contents
