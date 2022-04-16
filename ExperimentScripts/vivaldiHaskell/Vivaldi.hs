{-# OPTIONS_GHC -Wno-unrecognised-pragmas #-}
{-# HLINT ignore "Use <$>" #-}
import Data.Map (Map)
import qualified Data.Map as Map
import qualified Data.Vector.Dense as Vector
import qualified Data.Vector.Dense.Operations as Operations
import System.Random

--vector length
--does this just find the linear distance?
vectorLength :: Vector -> Double
vectorLength v =
    sqrt(
    x v ^ 2  +  y v ^ 2  +  z v ^ 2  +  w v ^ 2
    )

--vector distance
vectorDist :: Vector -> Vector -> Double
vectorDist x y =
    --functions not implemented
    vectorLength(Operations.plus(x, Operations.scale(-1, y)))

--random number generator (between 1 and 400)
randomNum :: IO [Double]
randomNum = do
    gen <- newStdGen
    return $ randomRs (1,400) gen
    
initializeCoordinates :: List -> Vector -> Map
initializeCoordinates =
    --equivilent to vector.list, but with the vector.dense type
    --let a = Vector.listVector [Coordinates 0 0 0 0, Coordinates 1 1 1 1]
    Data.Map.fromList [("initialPoint",
    --not sure whether it allows IO numbers to be used
    Vector.listVector [(randomNum, x), (randomNum, y), (randomNum, z), (randomNum, w)])]

main = do
    initializeCoordinates


