import System.Random.PCG
import Control.Monad.ST
import Control.Monad

randVectorFromSeed :: [[Double]]
randVectorFromSeed = runST $ do
    g <- initialize 1 2
    replicateM 25 (replicateM 4 (uniformR (0.00, 400.00) g))

randDoubleFromSeed :: [Double]
randDoubleFromSeed = runST $ do
    g <- initialize 3 4
    replicateM 300 (uniformR (0.00, 400.00) g)

main :: IO ()
main = do
    putStrLn (show (replicate 3 randVectorFromSeed))
    putStrLn (show (replicate 2 randDoubleFromSeed))