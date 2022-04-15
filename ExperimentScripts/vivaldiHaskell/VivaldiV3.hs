import Data.Map (Map)
import qualified Data.Map as Map
import qualified Data.Vector.Dense as Vector
import qualified Data.Vector.Dense.Operations as Operations
import System.Random

data Coordinates = Coordinates {
    x :: Double ,
    y :: Double ,
    z :: Double ,
    w :: Double
}

--vector length
--does this just find the linear distance?
vectorLength :: Vector -> Double
vectorLength v =
    sqrt(
    (x v)^2 + (y v)^2 + (z v)^2 + (w v)^2
    )

--vector distance
vectorDist :: Vector -> Vector -> Double
vectorDist x y =
    --functions not implemented
    vectorLength(Operations.plus(x, Operations.scale(-1, y)))

initialize :: List -> Vector -> Map
initialize =
    --equivilent to vector.list, but with the vector.dense type
    --let a = Vector.listVector [Coordinates 0 0 0 0, Coordinates 1 1 1 1]
    Data.Map.fromList [("initialPoint",
    Vector.listVector [(234, x), (182, y), (321, z), (48, w)])]
    

--work in progress function for initializing random point
--Random generation is horrid in haskell due to functions' requirement to be "pure"
--newRand = randomIO :: IO into