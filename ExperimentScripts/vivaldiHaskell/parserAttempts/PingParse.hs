{-# LANGUAGE OverloadedStrings #-}
{-# OPTIONS_GHC -Wno-unrecognised-pragmas #-}
{-# HLINT ignore "Use newtype instead of data" #-}
import System.Environment ()
import Data.Word
import Data.Attoparsec.Text
import Control.Applicative ( Alternative(many) )
import qualified Data.ByteString as B
data PingLine =
    PingLine {
        destAddr :: IP,
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

data IP = IP Word8 Word8 Word8 Word8 deriving Show

parseIP :: Parser IP
parseIP = do
    x <- decimal
    char '.'
    y <- decimal
    char '.'
    z <- decimal
    char '.'
    IP x y z <$> decimal
--return $ IP x y z w
parseRTT :: Parser Double
parseRTT = do
    double

logParser :: Parser PingFile
logParser = many $ logEntryParser <* endOfLine
--many is essentially a wildcard, the <* states to apply logEntryParser to each line until the EOF is reached

main :: IO ()
main = do
    a <- readFile "C:/Users/amages/Downloads/Archive/FILENEW1"
    x <- parseOnly logParser
    print x

