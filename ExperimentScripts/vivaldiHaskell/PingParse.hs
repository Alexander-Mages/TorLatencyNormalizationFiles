import System.Environment
import Data.Word
import Data.ByteString
import Control.Applicative

data PingLine =
    PingLine {
        destAddr :: String,
        rtt :: Double
    } deriving Show

type PingFile = [PingLine]

logEntryParser :: Parser PingLine
logEntryParser = do
    string "64 bytes from "
    destAddr <- parseIP
    string ": icmp_sec=0 ttl=50 time="
    rtt <- parseRTT
    string " ms"
    return $ PingLine destAddr rtt

parseIP :: Parser String
parseIP = do
    x <- string
    return String x

parseRTT :: Parser Double
parseRTT = do
    x <- double
    return Double x

logParser :: Parser PingFile
logParser = many $ logEntryParser <* endOfLine
--many is essentially a wildcard, the <* states to apply logEntryParser to each line until the EOF is reached

main :: IO ()
main = do
    Data.ByteString.readFile "C:/Users/amages/Downloads/Archive/FILENEW1" >>= print . parseOnly logParser

