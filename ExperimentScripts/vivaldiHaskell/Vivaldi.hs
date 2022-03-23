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

    --balance local and remote error
    -- a = LocalError, b = RemoteError
    balance a b
        (a / (b + a))

    --compute relative error
    