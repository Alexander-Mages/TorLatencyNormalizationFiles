module Vivaldi where
import Data.Map.Strict (Map)
import qualified Data.Map.Strict as Map
import Data.Vector (Vector)
import qualified Data.Vector as Vector
import System.Random
import qualified Data.List
import Control.Monad.IO.Class (MonadIO)

{-# LANGUAGE FlexibleContexts #-}

--Vector operations
{--
--elementwise vector addition
--addvec :: [Double] -> [Double] -> Vector Double
--addvec :: Num a => [a] -> [a] -> Vector a
-- ^ this is result of :t after ghci> addvec a b = [(a !! 0)+(a !! 0), (a !! 1)+(b !! 1), (a !! 2)+(b !! 2), (a !! 3)+(b !! 3)]
addvec2 :: Num a => [a] -> [a] -> [a]
addvec2 a b =
        -- ^ ^ Vector 1, Vector 2
        Vector.fromList [(a !! 0)+(b !! 0), (a !! 1)+(b !! 1), (a !! 2)+(b !! 2), (a !! 3)+(b !! 3)]   ---this syntax need be applied to rest of code 05/16/22
                                                -- ^ ^		 ^
                                                --key, vector, key of new coordinate
--}
addvec :: Num a => [a] -> [a] -> [a]
addvec a b = zipWith (+) a b
{--
--vector scaling
scalevec :: [Double] -> Double -> Vector Double
scalevec a b =
	-- ^ ^ Vector, scale factor
	Vector.fromList [(b * (a !! 0)), (b * (a !! 1)), (b * (a !! 2)), (b * (a !! 3))]
					-- ^ ^ ^ ^
					--scale factor, key, vector, key of new coordinate
--}
--scalevec :: [Double] -> Double -> Vector Double
scalevec :: Num b => [b] -> b -> [b]
scalevec a b = map (b*) a


--vector length
--vectorLength :: [Double] -> Double
vectorLength :: (Num a) => [a] -> a -> a
--vectorLength :: (Floating a, Floating (a -> a)) => [a] -> a -> a
-- ^ this is what GHCI gives me, seems wrong, I don't want to use floating points
vectorLength v = sqrt (sum (map (**) v))
--side note, this is beautiful syntax, only 8 characters in the function body

--vector distance
--vectorDist :: [Double] -> [Double] -> Double
-- vectorDist :: (Floating a, Floating (a -> a)) => [a] -> [a] -> a -> a
-- GHCI RESULT ^
vectorDist :: (Num a) => [a] -> [a] -> a -> a
vectorDist a b = vectorLength(addvec a (map negate b))
                        --scale instead of ^

--random number generator (between 1 and 400)
--randomNum :: IO Double
randomNum :: (Random a, Num a, MonadIO f) => f [a] --note to self: find out what this type constraint means/contains
randomNum = randomRs (1,400) <$> newStdGen
--randomNum :: Double
--randomNum = 244


--initializeCoordinates :: Map Integer (Vector Double)
initializeCoordinates :: (Ord k, Enum k, Num k, Random a, Num a, MonadIO f) => Map k (Vector (f [a]))
--god help me. Again, reminder to look into this type constraint
initializeCoordinates =
        --two maps: one holds hosts, denoted host1 host2 etc... the other holds latencies, denoted latency1-2 latency2-4 etc...
        --returns map of ["host{host#}", (randomly generated 4 way vector)]
        Map.fromList (
                --"zip" combiles elements of two lists into one list of tuples | zip :: [a] -> [b] -> [(a,b)]
                zip 
                        [0..25] --integers as keys
                        -- ^ \/ both must be scaled along with the # of latencies created
                        (replicate 25 (Vector.fromList [randomNum, randomNum, randomNum, randomNum]))
                        -- ^ replicate :: Int -> a -> [a], creates list of length of first argument and value of second
        )
        
--initializeLatencies :: Map Integer Double
--initializeLatencies :: (Ord a1, Enum a1, Num a1, Random a2, Num a2, Ord b, Enum b, Num b, MonadIO f) => Map (a1, b) (f [a2])
initializeLatencies :: (Ord a1, Enum a1, Num a1, Random a2, Num a2, Ord b, Enum b, Num b) => Map (a1, b) ([a2])
--try using a b c instead of a1 a2 and b
--I thought it couldn't get any worse
initializeLatencies =
        Map.fromList (
                zip
                        --fills every combination of items in 2 [1..9] int lists. Scaling requires simply changing the 9 below to desired host quantity
                        (concat $ zipWith (zip . repeat) [1..25] $ Data.List.tails [26..50]) --currently creates some tuples with two identical values
                        (take 325 randomNum) -- [283,13,398]... note: must be scaled according to the keys, "length concat $ zipWith (zip . repeat) [1..25] $ tails [1..25]"
        )
        --should be identical to the above: ghci> let maapp = Data.Map.Strict.fromList $ zip ((concat $ zipWith (zip . repeat) [1..25] $ Data.List.tails [26..50])) (Prelude.take 325 (iterate (+1) 1))
        --ghci> Data.Map.Strict.lookup (23,48) maapp
                --Just 320

--errdist :: (Int, Int) -> Map (a, b) (f [a]) -> Map k (Vector (f [a])) -> [a -> a]
--errdist :: (Num a, Num b, Random a2, Num a2, MonadIO f) => (a, a) -> Map (a, b) (f [a2]) -> Map a (Vector (f [a2])) -> a
--signatures I wrote^
--errdist :: ()
--errdist latencyid latencies hosts = abs ( ((latencies !! latencyid) - (vectorDist (hosts !! fst latencyid) (hosts !! snd latencyid))) ^ 2)

--errdist :: (k, k) -> Map (k, k) a -> Map k b -> Maybe a

fallibleLookup :: (Ord k, Monad m) => k -> Map.Map k a -> m a
fallibleLookup k = maybe (fail "fallibleLookup: Key not found") pure . Map.lookup k
--I know this is bad practice, but it works. https://stackoverflow.com/questions/31898658/the-maybe-result-from-map-lookup-is-not-type-checking-with-my-monad-transformer
--I don't know why or how, but it allows a failure case without a Maybe monad (random numbers didn't play nice for some reason)

errdist :: (k, k) -> Map (k, k) a -> Map k a -> a -> a
errdist latencyid latencies hosts =
        abs (
                ((fallibleLookup latencyid latencies) -
                (vectorDist (fallibleLookup (fst latencyid) hosts) (fallibleLookup (snd latencyid) hosts))) ^ 2
        )

--err :: Map Integer Double -> Map Integer (Vector Double) -> Double
err :: (Num k, Enum k) => p1 -> p2 -> Map (k, k) a -> Map k a -> a -> a
err latencies hosts =
        sum (map errdist (concat $ zipWith (zip . repeat) [1..25] $ Data.List.tails [26..50]))
-- ^final error value	^applies the preceding function to all latencies, replacing each item with the result
{--
--normalizeMap :: Map Integer (Vector Double) -> Map Integer Double -> Integer -> Map Integer (Vector Double)
normalizeMap latencies hosts errTarget =
        until (
                (((err latencies hosts) - 1000) < errTarget)                            --first arg
                (map repositionSingleCoordinate)                                   --second arg
                (concat $ zipWith (zip . repeat) [1..25] $ Data.List.tails [26..50])    --third arg
        )
        --mapping cannot be used in an until block
--}

normalizeMap maps =
        if (((err maps) - 1000) < 100) then
                maps
        else
                normalizeMap (map (repositionSingleCoordinate maps) (concat $ zipWith (zip . repeat) [1..25] $ Data.List.tails [26..50]))

--latencies and hosts Maps are not global variables, depending on how haskell handles functions,
--I may need to pass them as parameters to the "map" function uses (https://stackoverflow.com/questions/51073535/using-map-with-function-that-has-multiple-arguments)

maps = (hosts, latencies)
--repositionSingleCoordinate :: [Integer] -> Map Integer Double -> Map Integer (Vector Double) -> Map Integer (Vector Double)
repositionSingleCoordinate maps latencyid =
        Map.insert (head latencyid) (
                addvec(
                        (fst maps) !! head latencyid, --source
                        scalevec(
                                addvec(
                                        Vector.fromList[randomNum, randomNum, randomNum, randomNum],
                                        scalevec (
                                                (((snd maps) !! latencyid) - vectorLength(addvec((fst maps) !! head latencyid, scalevec((fst maps) !! tail latencyid, -1)))) /
                                                                vectorLength(addvec((fst maps) !! head latencyid, scalevec((fst maps) !! tail latencyid, -1))),
                                                addvec((fst maps) !! head latencyid, scalevec((fst maps) !! tail latencyid, -1))
                                        )
                                ),
                                0.002 --scaling factor
                        )
                )
        ) (fst maps) --map to insert into


{-
findClosestNode ::
findClosestNode hosts latencies hostKey =
	--relatively easy implementation, just need a list of host keys to map/fold through
-}

--main :: Map Integer (Vector Double)
main =
        normalizeMap (initializeCoordinates, initializeLatencies)
        -- ^ the finished system (i think)					-- ^ arbitrary error cutoff                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         