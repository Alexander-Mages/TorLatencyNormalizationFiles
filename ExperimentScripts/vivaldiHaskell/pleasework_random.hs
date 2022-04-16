import System.Random
import Control.Monad

num :: IO [Double]
num = do
    gen <- newStdGen
    return $ randomRs (1,400) gen

main = do
    num >>= \x -> print $ take 4 $ x