import System.Random.PCG
import Control.Monad.ST

randVectorFromSeed :: [[m a]]
randVectorFromSeed = runST $ do
    g <- initialize 1 2
    return (replicate 25 (replicate 4 (uniformR (0.00,400.00) (g))))

randDoubleFromSeed :: [m a]
randDoubleFromSeed = runST $ do             
    g <- initialize 3 4
    return (replicate 300 (uniformR (0.00,400.00) g))
