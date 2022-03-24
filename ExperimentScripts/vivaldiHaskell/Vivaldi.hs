main = do
    putStrLn("coordinate of point of measurement")
    LOCAL <- getLine 
    putStrLn("coordinate of remote node")
    REMOTE <- getLine
    putStrLn("RTT between the two")
    RTT <- getLine
    putStrLn("local error estimate")
    LocalError <- getLine 
    putStrLn("Remote error estimate")
    RemoteError <- getLine

    --"sample weight balances local and remote error"
    -- a = LocalError, b = RemoteError
    BalanceLocalRemoteError LocalError RemoteError
        (LocalError / (LocalError + RemoteError))

    --"compute relative error of this sample"
    
    computeRelativeError Local Remote RTT
        abs ((Local - Remote) - RTT) / RTT
        --this is supposed to be absolute value (not sure if my syntax is right yet)

    --"update weighted moving average of local error"
        --not exactly sure how to implement, "the constants ce and cc are tuning parameters"
        --pseudocode:
        --ei = es × ce × w + ei × (1 − ce × w)
    --code below includes all but what I'm unaware of
    updateWeightedMovingAverage RelativeError TuningParameterCe BalancedError Local
        ((RelativeError * TuningParameterCe * BalancedError) + Local) * (1 - (TuningParameterCe * BalancedError))


    --"Update Local Coordinates"
    calculateAdaptiveTimestep TuningParameterCc BalancedError
        TuningParameterCc * BalancedError

    updateLocalCoordinate Local AdaptiveTimestep RTT Remote
        Local + AdaptiveTimestep * (RTT - (Local - Remote)) * (Local - Remote) -- * (Local - Remote) is an argument to function "u". I don't know what it should do
                                                                                -- but it's neccecary: * u(Local - Remote)

    --only the first and last functions matter for the local coordinate updating

    
    