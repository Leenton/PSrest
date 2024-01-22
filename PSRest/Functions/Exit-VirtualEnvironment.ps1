function Exit-PSRestVirtualEnvironment{
    try{
        deactivate
    }catch{
        throw "Failed to deactivate the virtual environment."
    }
}