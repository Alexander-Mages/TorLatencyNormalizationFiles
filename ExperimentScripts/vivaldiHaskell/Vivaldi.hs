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
    return $ randomRs (1,400) <$> newStdGen
    
initializeCoordinates :: List -> Vector -> Map
initializeCoordinates =
    --equivilent to vector.list, but with the vector.dense type
    --let a = Vector.listVector [Coordinates 0 0 0 0, Coordinates 1 1 1 1]
    Data.Map.fromList [("initialPoint",
        Vector.listVector [(randomNum, x), (randomNum, y), (randomNum, z), (randomNum, w)])]
    --not sure whether it allows IO numbers to be used

addRandomCoordinateToMap :: Map -> Vector -> Map
addRandomCoordinateToMap vivaldi name =
    Data.Map.insert ("Point" ++ show name) (Vector.listVector [(randomNum, x), (randomNum, y), (randomNum, z), (randomNum, w)]) vivaldi
    --in the absence of the naming parameter, the insert function doesn't need "vivaldi" argument at end as haskell infers it's placement

addCoordinateAndMinimizeEnergy :: Map -> Vector -> Map
addCoordinateAndMinimizeEnergy vivaldi name =
    minimizeEnergy (addRandomCoordinateToMap vivaldi name)

minimizeEnergy :: --idk yet
minimizeEnergy vivaldi name rtt =
    --this is far from functional, but I'm half implementing it to help my conceptualization
    --need to add error calculation and it's relavent recursion condition
    Operations.plus (
        (Vector.listVector [(0, x), (0, y), (0, z), (0, w)]), --origin
        Operations.scale(
            (rtt - vectorLength(
        Operations.plus (vivaldi ! "initialPoint") Operations.scale(-1 (vivaldi ! ("Point" ++ show name)))
    )/vectorLength(
        Operations.plus (vivaldi ! "initialPoint") Operations.scale(-1 (vivaldi ! ("Point" ++ show name))))
        )
    )
    rtt - vectorLength(
        Operations.plus (vivaldi ! "initialPoint") Operations.scale(-1 (vivaldi ! ("Point" ++ show name)))
    )
    --no idea what pattern arguments are expected in by Vector.Dense.Operations

main :: IO ()
main = do
    vivaldi <- initializeCoordinates
    vivaldi' <- addCoordinateAndMinimizeEnergy vivaldi "one"
    --this is too imperative like, I should be able to do this in one function call via recursion, where i would be able to specify a number of random coordinates to be added
    