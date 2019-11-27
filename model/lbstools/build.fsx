// include Fake libs
#r "./packages/FAKE/tools/FakeLib.dll"

open Fake
open System
open System.IO
// Directories
let homeDir = System.Environment.GetFolderPath(System.Environment.SpecialFolder.UserProfile)
(*let homeDir = if (Environment.OSVersion.Platform == PlatformID.Unix || Environment.OSVersion.Platform == PlatformID.MacOSX)*)
              (*then Environment.GetEnvironmentVariable("HOME")*)
              (*else Environment.ExpandEnvironmentVariables("%HOMEDRIVE%%HOMEPATH%")*)
let buildDir  = "./build/"
let deployDir = "./deploy/"
let libDir = "./lib/"


// Filesets
let appReferences  =
    !! "/**/*.csproj"
      ++ "/**/*.fsproj"

// version info
let version = "0.1"  // or retrieve from CI server

// Targets
Target "Clean" (fun _ ->
    CleanDirs [buildDir; deployDir]
)

Target "Build" (fun _ ->
    // compile all projects below src/app/
    MSBuildRelease buildDir "Build" appReferences
        |> Log "AppBuild-Output: "
)

Target "Debug" (fun _ ->
    // compile all projects below src/app/
    MSBuildDebug buildDir "Build" appReferences
        |> Log "AppBuild-Output: "
)


Target "Deploy" (fun _ ->
    !! (buildDir + "/**/*.*")
        -- "*.zip"
        |> Zip buildDir (deployDir + "ApplicationName." + version + ".zip")
)

// Build order
"Clean"
  //==> "MakeDeps"
  ==> "Build"
  ==> "Deploy"

// Build order
"Clean"
  //==> "MakeDeps"
  ==> "Debug"
  ==> "Deploy"

// start build
RunTargetOrDefault "Build"
