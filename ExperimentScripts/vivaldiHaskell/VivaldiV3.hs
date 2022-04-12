import Data.Map (Map)
import qualified Data.Map as Map
import qualified Data.Vector.Dense as Vector
import qualified Data.Vector.Dense.Operations
import System.Random

data Coordinates = Coordinates {
    x :: Float ,
    y :: Float ,
    z :: Float ,
    w :: Float
}


let a = Data.Vector.fromList []
--vector length
--does this just find the linear distance?
vectorLength :: Coordinates -> Float
vectorLength v =
    sqrt(
    (x v)^2 + (y v)^2 + (z v)^2 + (w v)^2
    )

--vector distance
vectorDist :: Coordinates -> Coordinates -> Float
vectorDist x y =
    --functions not implemented
    addVector(x, scaleVector(-1,))


--work in progress function for initializing random point
--Random generation is horrid in haskell due to functions' requirement to be "pure"
newRand = randomIO :: IO into
