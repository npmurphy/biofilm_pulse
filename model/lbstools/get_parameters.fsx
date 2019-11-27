#I "build"
#r "ParserCombinators.dll"
#r "CRNEngineDotNet.dll"
#r "common.dll"

open Microsoft.Research.CRNEngine

let model_of_prog s =
  let possible_model, errors = Parser.from_string_find_errors Model.parse s
    
  if possible_model.IsNone then
    let errors = errors |> Seq.map (fun error -> sprintf "Line %i: %s" error.row error.text) |> (String.concat System.Environment.NewLine)
    failwithf "Failed to parse: %s%s" System.Environment.NewLine errors

  let model = possible_model.Value
  model

let rnatra_prog = "
init Gb 1
| Gb ->{b0*(stress*scale_b) + c} Gb + mB
| Gb ->{ma}
| Gb <->{fo}{bac}
| Gb ->[func *[C]]
"

let rate_to_strings (rate:Crn.rate) : string list =
    match rate with
      | Rate.MassAction( mar ) -> Expression.mentions mar                                       
      | Rate.Function e        -> Expression.mentions e 
                                    |> List.map (fun (s:Crn.key) -> 
                                        match s with 
                                          | Key.Parameter(p) -> p 
                                          | _ -> "")  



let params_from_crn (crn:Crn.t) = 
  let reactions: Crn.reaction list = crn.reactions 
  let rates = List.concat [ List.map (fun (r:Crn.reaction) -> r.rate ) reactions
                          ; List.map (fun (r:Crn.reaction) -> r.reverseRate) reactions
                              |> List.choose id
                          ]
  let parm = rates |> List.collect rate_to_strings |> List.distinct |> List.filter ((=) "" >> not) 
  parm  

let tcrn = model_of_prog rnatra_prog |> (fun m -> m.systems) |> List.head 
let expected = ["b0"; "stress"; "scale_b"; "c"; "ma"; "fo"; "bac"; "func" ]
printfn "What I want %A" expected 
printfn "What I get %A" (params_from_crn tcrn)



