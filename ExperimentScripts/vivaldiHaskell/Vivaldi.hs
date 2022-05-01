import Data.Map (Map)
import qualified Data.Map as Map
import qualified Data.Vector.Dense as Vector
import qualified Data.Vector.Dense.Operations as Operations
import System.Random
import Control.Monad

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
--returns map of ["host{host#}", (randomly generated 4 way vector)]
initializeCoordinates =
    --two maps: one holds hosts, denoted host1 host2 etc... the other holds latencies, denoted latency1-2 latency2-4 etc...
    Data.Map.fromList (
        --"zip" combiles elements of two lists into one list of tuples | zip :: [a] -> [b] -> [(a,b)]
        zip (
            ["host0","host1","host2","host3","host4","host5","host6","host7","host8","host9"] 
            (replicate 9 Vector.listVector [(randomNum, x), (randomNum, y), (randomNum, z), (randomNum, w)])
            )-- ^ replicate :: Int -> a -> [a], creates list of length of first argument and value of second
    )

initializeLatencies :: 
--returns map of ["latency{host#}{dest#}", {randomly generated latency}]
initializeLatencies =
    Data.Map.fromList (
        zip (
            --this sacrilege avoids using external libraries to iterate
            ["latency1-1","latency1-2","latency1-3","latency1-4","latency1-5","latency1-6","latency1-7","latency1-8","latency1-9",
            "latency2-1","latency2-2","latency2-3","latency2-4","latency2-5","latency2-6","latency2-7","latency2-8","latency2-9",
            "latency3-1","latency3-2","latency3-3","latency3-4","latency3-5","latency3-6","latency3-7","latency3-8","latency3-9",
            "latency4-1","latency4-2","latency4-3","latency4-4","latency4-5","latency4-6","latency4-7","latency4-8","latency4-9",
            "latency5-1","latency5-2","latency5-3","latency5-4","latency5-5","latency5-6","latency5-7","latency5-8","latency5-9",
            "latency6-1","latency6-2","latency6-3","latency6-4","latency6-5","latency6-6","latency6-7","latency6-8","latency6-9",
            "latency7-1","latency7-2","latency7-3","latency7-4","latency7-5","latency7-6","latency7-7","latency7-8","latency7-9",
            "latency8-1","latency8-2","latency8-3","latency8-4","latency8-5","latency8-6","latency8-7","latency8-8","latency8-9",
            "latency9-1","latency9-2","latency9-3","latency9-4","latency9-5","latency9-6","latency9-7","latency9-8","latency9-9"]
            (replicate 81 randomNum)
        )
    )

zipWith (++) [1..81]
zipWith (++) (replicate 81 "latency") [1..81]

error ::
error latencies hosts=

    2 * ((latencies ! "latency1-2") - (vectorDist (hosts ! "host1", hosts ! "host2")))


normalizeCoordinates ::
normalizeCoordinates hosts latencies =

--pretending this is not here for now
{-
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
-}
main :: IO ()
main = do
    hosts <- initializeCoordinates
    latencies <- initializeLatencies
    vivaldi' <- addCoordinateAndMinimizeEnergy vivaldi "one"
    --this is too imperative like, I should be able to do this in one function call via recursion, where i would be able to specify a number of random coordinates to be added
    