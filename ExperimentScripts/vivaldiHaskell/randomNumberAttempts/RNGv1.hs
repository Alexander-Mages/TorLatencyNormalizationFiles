import System.Random
import Control.Monad(when)
import Data.Maybe (fromMaybe)

randomNumber :: StdGen -> IO ()
--IO is required due to function's "impurity"
randomNumber gen = do
    --generate double in range 1-400 using generator "gen" of type StdGen
    --returns random double and new generator
    let (randDouble, newGen) = randomR (1,400) gen :: (Double, StdGen)
    putStrLn (show randDouble)
    putStrLn (show newGen)
    randomNumber newGen
    -- ^ recursion :)

main :: IO ()
main = do
    gen <- getStdGen
    randomNumber gen




{-

main = do
    gen <- getStdGen
    randomFourNumbers gen
randomFourNumbers :: StdGen -> IO () 
randomFourNumbers gen = do
    iterator <- 0
    randomNumber gen iterator
-}