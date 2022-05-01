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
            --zipWith: elementwise string concatenation of lists
            (zipWith (++) (replicate 72 "latency") (map show $ -- \/excludes multiples of 11
            [12..21]++[23..32]++[34..43]++[45..54]++[56..65]++[67..76]++[78..87]++[89..98])) -- ["latency12","latency13",]...
            (replicate 72 randomNum) -- [283,13,398]...
        )
    )

error :: Map -> Map -> Double
error latencies hosts =
    ids = map show $ [12..21]++[23..32]++[34..43]++[45..54]++[56..65]++[67..76]++[78..87]++[89..98]
    dist :: Double
    dist latencyid = 
        abs((latencies ! $ "latency" ++ show latencyid) - 
        (vectorDist (hosts ! $ "host" ++ show head latencyid) (hosts ! $ "host" ++ show last latencyid)) ^2)
    --applies the preceding function to all items in list ids, replacing each item with the result
    sum $ map dist ids
    -- ^final error value

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
    