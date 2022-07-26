import System.IO (readFile)
import Control.Applicative (<$>)
import Data.Maybe (isJust, fromJust)
import Data.List (sortBy)
import Data.Function (on)
import Data.Maybe (catMaybes)
--import Control.Monad.IO.Class (liftIO)

data PingEntry = PingEntry { destHost :: String, rtt :: String } deriving Show
--destHost and rtt

--returns "Just" the two values if present, and Nothing if not
parseLine (_:_:_:destHost:_:_:rtt:_) = Just $ PingEntry destHost rtt
parseLine _ = Nothing


prettyPrint :: PingEntry -> IO ()
prettyPrint (PingEntry destHost rtt) = putStrLn $ rtt ++ "ms to " ++ destHost


--formatData :: PingEntry -> String
--still in format of time=
--formatData (PingEntry destHost rtt) sourceHost = ((sourceHost, destHost), rtt)

main = do
    --lines <$> readFile "/home/alex/ExperimentData/FILENEW1"
        --Reads the file into a single string, then seperates into a list of strings delimited by newlines
    --tail .
        --the first line is the source host, tail returns the list without it's first item
    --map (parseLine . words) .
        --this maps the function "words" to each line, seperating the string into a list of strings, delimited by whitespace
        --next, parseLine is mapped to each list (line), using pattern matching to extract the time=***ms and dest IP addr
    --map fromJust . filter isJust .
        --filter isJust filters  out any Maybe values from the list, returning only the filled, Just values
        --map fromJust, then evaluates the Just value into it's non-monadic value, removing the maybe monad.
        --this can also accomplished with "catMaybes" - which "creates a list of Just values from a Maybe list"
            --http://zvon.org/other/haskell/Outputmaybe/catMaybes_f.html
    --non-fancy, readable version
    --justPings <- map fromJust . filter isJust . map (parseLine . words) . tail . lines <$> readFile "/home/alex/ExperimentData/FILENEW1"
    --sugary version
    justPings <- catMaybes . map (parseLine . words) . tail . lines <$> readFile "/home/alex/ExperimentData/FILENEW1"

    --note, tail raises exception if input is empty, drop 1 is a suitable alternative
        
    sourceHost <- head . lines <$> readFile "/home/alex/ExperimentData/FILENEW1"
    mapM_ prettyPrint justPings
    --return $ ((mapM prettyPrint justPings), sourceHost)
    --putStrLn sourceHost

--System.Directory