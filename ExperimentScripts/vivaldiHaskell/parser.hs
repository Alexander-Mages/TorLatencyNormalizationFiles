import Data.Attoparsec.Ping.Win32


    
main :: IO ()
main = do
    file <- readFile "C:/Users/amages/Downloads/Archive/FILENEW1"
    lines <- tail . lines file
    pingParser lines