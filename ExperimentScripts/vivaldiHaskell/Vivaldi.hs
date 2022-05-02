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

initializeLatencies :: List -> Map
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
    let ids = map show $ [12..21]++[23..32]++[34..43]++[45..54]++[56..65]++[67..76]++[78..87]++[89..98]
    dist :: Double
    dist latencyid = 
        abs(
            (latencies ! $ "latency" ++ show latencyid) - 
            (vectorDist (hosts ! $ "host" ++ show head latencyid) (hosts ! $ "host" ++ show last latencyid)) ^2
        )
    --applies the preceding function to all items in list ids, replacing each item with the result
    sum $ map dist ids
    -- ^final error value

normalizeMap :: Map -> Map -> Int -> Map
normalizeMap hosts latencies errTarget =
    --this is going to look rough until I get it solved conceptually :/
    --pseudocode is a generous categorization
    let ids = map show $ [12..21]++[23..32]++[34..43]++[45..54]++[56..65]++[67..76]++[78..87]++[89..98]
    until ((((error (latencies hosts)) - 1000) < errTarget)
        (map repositionSingleCoordinate ids)
    --THIS SYNTAX IS INCORRECT^
    --mapping cannot be used in an until block

--latencies and hosts Maps are not global variables, depending on how haskell handles functions,
--I may need to pass them as parameters to the "map" function uses (https://stackoverflow.com/questions/51073535/using-map-with-function-that-has-multiple-arguments)

repositionSingleCoordinate :: Int -> Map
repositionSingleCoordinate latencyid =
    --I ask forgiveness from all those who need read this
    Data.Map.insert ("host" ++ show head latencyid) (Vector.plus ((hosts ! $ "host" ++ show head latencyid) (Vector.scale .002 (
        Vector.plus(
            (Vector.listVector [(randomNum, x), (randomNum, y), (randomNum, z), (randomNum, w)])
            (Vector.scale ((                 
            (latencies ! $ "latency" ++ show latencyid) - 
                vectorLength (
                        Vector.plus(
                    (hosts ! $ "host" ++ show head latencyid) Vector.scale(-1 $ hosts ! $ "host" ++ show last latencyid)
                        )
                    )
                ) / (
                    vectorLength (
                        Vector.plus(
                            (hosts ! $ "host" ++ show head latencyid) Vector.scale(-1 $ hosts ! $ "host" ++ show last latencyid)
                        )
                    )
                    )
                    Vector.plus(
                            (hosts ! $ "host" ++ show head latencyid) Vector.scale(-1 $ hosts ! $ "host" ++ show last latencyid)
                        )
                    )
                )
            )
        )
    ))) hosts


findClosestNode ::
findClosestNode hosts latencies hostKey =
    --relatively easy implementation, just need a list of host keys to map/fold through


main :: IO ()
main = do
    hosts <- initializeCoordinates
    latencies <- initializeLatencies
    vivaldi <- normalizeMap hosts latencies errTarget
   -- ^ the finished system (i think)       -- ^ arbitrary error cutoff
                            




{-
--pretending this is not here for now
addRandomCoordinateToMap :: Map -> Vector -> Map
addRandomCoordinateToMap vivaldi name =
    Data.Map.insert ("Point" ++ show name) (Vector.listVector [
        (randomNum, x), (randomNum, y), (randomNum, z), (randomNum, w)]) vivaldi
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
