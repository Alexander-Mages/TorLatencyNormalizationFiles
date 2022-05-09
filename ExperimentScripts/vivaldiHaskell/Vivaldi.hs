module Vivaldi where

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
            [0..9] --integers as keys
            (replicate 9 Vector.listVector [(randomNum, x), (randomNum, y), (randomNum, z), (randomNum, w)])
            )-- ^ replicate :: Int -> a -> [a], creates list of length of first argument and value of second
    )

initializeLatencies :: List -> Map
--returns map of ["latency{host#}{dest#}", {randomly generated latency}]
initializeLatencies =
    Data.Map.fromList (
        zip (
            --fills every combination of items in 2 [1..9] int lists. Scaling requires simply changing the 9 below to desired host quantity
            concat $ zipWith (zip . repeat) [1..25] $ tails [1..25] --currently creates some tuples with two identical values
            (replicate 325 randomNum) -- [283,13,398]...
        )
    )

errdist :: Double
    dist latencyid = 
        abs(
            (latencies ! latencyid) - 
            (vectorDist (hosts ! (latencyid ! 0)) (hosts ! (latencyid ! 1))) ^2
        )
error :: Map -> Map -> Double
error latencies hosts =
    sum (map (errdist (concat $ zipWith (zip . repeat) [1..25] $ tails [1..25])))
 -- ^final error value    ^applies the preceding function to all latencies, replacing each item with the result

normalizeMap :: Map -> Map -> Int -> Map
normalizeMap hosts latencies errTarget =
    --this is going to look rough until I get it solved conceptually :/
    --pseudocode is a generous categorization
    until ((((error (latencies hosts)) - 1000) < errTarget)
        (map repositionSingleCoordinate (concat $ zipWith (zip . repeat) [1..25] $ tails [1..25])))
    --THIS SYNTAX IS INCORRECT^
    --mapping cannot be used in an until block

--latencies and hosts Maps are not global variables, depending on how haskell handles functions,
--I may need to pass them as parameters to the "map" function uses (https://stackoverflow.com/questions/51073535/using-map-with-function-that-has-multiple-arguments)

repositionSingleCoordinate :: Int -> Map
repositionSingleCoordinate latencyid =
    --I ask forgiveness from all those who need read this
    Data.Map.insert (latencyid ! 1) (Vector.plus ((hosts ! (latencyid ! 1))) (Vector.scale .002 (
        Vector.plus(
            (Vector.listVector [(randomNum, x), (randomNum, y), (randomNum, z), (randomNum, w)])
            (Vector.scale ((                 
            (latencies ! latencyid)) - 
                vectorLength (
                        Vector.plus(
                    (hosts ! (latencyid ! 1))) Vector.scale(-1 $ hosts ! (latencyid ! 2)))
                        )
                    )
                ) / (
                    vectorLength (
                        Vector.plus(
                            (hosts ! (latencyid ! 1))) Vector.scale(-1 $ hosts ! (latencyid ! 2))
                        )
                    )
                    )
                    Vector.plus(
                            (hosts ! (latencyid ! 1))) Vector.scale(-1 $ hosts ! (latencyid ! 2))
                        )
                    )
                )
            )
        )
    ))) hosts
{-
findClosestNode ::
findClosestNode hosts latencies hostKey =
    --relatively easy implementation, just need a list of host keys to map/fold through
-}

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
