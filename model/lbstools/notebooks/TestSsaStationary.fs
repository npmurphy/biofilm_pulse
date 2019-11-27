
#I @"../lib/CliCRN"
#I @"../packages/MathNet.Numerics/lib/net40"
#I @"../packages/MathNet.Numerics.FSharp/lib/net40"
#r @"ParserCombinators.dll"
#r @"CRNEngineDotNet.dll"
#r @"MathNet.Numerics.dll"
#r @"MathNet.Numerics.FSharp.dll"

open Microsoft.Research.CRNEngine
open MathNet.Numerics.Distributions

let test_crn frwd back =
    sprintf 
        "
        directive simulation { final=100000.0 }
        directive stochastic { stationary_skiptime=1000.0 }
        directive parameters [ fr = %f; bk = %f ]
        init F 100
        //| init X 50
        | F ->{fr} X 
        | X ->{bk} F 
        " frwd back 

let forward = 2.0
let back = 0.1

let mean = forward/back
printfn "%f" mean

(log 0.1)*(log 2.0)

let dist = MathNet.Numerics.Distributions.Poisson(forward/back)

let P = Array.init 100 id
let poissPDF = P |> Array.map (dist.Probability) 

let parsed = (test_crn forward back) |> Crn.from_string

let add_maxes_to_species (species_maxes:Map<string,int>) (crn:Crn.t) =  
    let my_plotables = 
        species_maxes 
        |> Map.toList
        |> List.map (fun (k, v) -> Expression.Key { (Species.create k) with max = Some (v)})
    
    let newcrn = {crn with settings = { crn.settings with simulation = { crn.settings.simulation with plots = my_plotables }}}
    newcrn

let crn = add_maxes_to_species (Map.ofList [("X",110); ("F",110)]) parsed

//let ssa = Crn.to_ssa crn |> Ssa.set_number_of_points 1

let ssa = Crn.to_ssa crn// |> Ssa.set_number_of_points 1


let short_crn = {crn with settings = {crn.settings with simulation = {crn.settings.simulation with final=1000.0 }}}
let out = Crn.simulate_cme short_crn
out
1+1

let _, tr, stationary = Ssa.simulate_with_stationary ssa

let layout = 
    Layout (
        title = "Example stationary distribution",
        xaxis = Xaxis(title = "X"),
        yaxis = Yaxis(title = "Probability density")
    )
[ Scatter (x=P, y=poissPDF);
  //Scatter (x=P, y=stationary.["X"]);
  Scatter (x=[|0..(Array.length stationary.["X"])|], y=stationary.["X"], name="X");
    Scatter (x=[|0..(Array.length stationary.["F"])|], y=stationary.["F"], name="F")

  ]
|> Chart.Plot
|> Chart.WithLayout layout// |> Chart.Png

let layout = 
    Layout (
        title = "Stochastic trajectory",
        xaxis = Xaxis(title = "X"),
        yaxis = Yaxis(title = "Probability density")
    )
Scatter (x=tr.times, y=tr.columns.Head.values)
|> Chart.Plot
|> Chart.WithLayout layout


