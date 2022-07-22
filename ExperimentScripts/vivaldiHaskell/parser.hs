import Text.ParserCombinators.Parsec

pingFile :: GenParser Char st [[String]]
pingFile = do
    result <- many pingLine
    eof
    return result

pingLine :: GenParser Char st [String]
PingLine = do
    result <- blocks
    eol
    return result

blocks :: GenParser Char st [String]
blocks = do
    

main :: IO ()
main = do
    file <- readFile "C:/Users/amages/Downloads/Archive/FILENEW1"
    lines <- tail . lines file
    pingParser lines