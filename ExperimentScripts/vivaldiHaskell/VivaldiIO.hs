{-# OPTIONS_GHC -Wno-unrecognised-pragmas #-}
{-# LANGUAGE FlexibleInstances #-}
{-# LANGUAGE FlexibleContexts #-}
{-# HLINT ignore "Avoid lambda" #-}
{-# HLINT ignore "Use first" #-}
module Main where
import Data.Map (Map)
import qualified Data.Map as Map
import Data.Vector (Vector)
import qualified Data.Vector as Vector
import System.Random.PCG
import qualified Data.List
import Control.Monad.IO.Class (MonadIO)
import Data.Bifunctor
import Control.Monad.ST
import Control.Monad
import Data.Maybe
import qualified Text.PrettyPrint.Boxes as PB
import Data.List.Split
import Debug.Trace


--NOTE: vec and vector refer to coordinate vectors. These are of datatype list.

--Vector operations
{--
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

--elementwise vector addition
addvec :: Num a => [a] -> [a] -> [a]
addvec = zipWith (+)
{--
ghci> addvec [1.00, 2.00, 3.00, 4.00] [1.5, 2.25, 2.2, 3.1]
[2.5,4.25,5.2,7.1]
--}

{--
--vector scaling
scalevec :: [Double] -> Double -> Vector Double
scalevec a b =
	-- ^ ^ Vector, scale factor
	Vector.fromList [(b * (a !! 0)), (b * (a !! 1)), (b * (a !! 2)), (b * (a !! 3))]
					-- ^ ^ ^ ^
					--scale factor, key, vector, key of new coordinate
--}
--vector multiplication by scalar
scalevec :: Num b => [b] -> b -> [b]
scalevec a b = map (b*) a
{--
ghci> scalevec [1,2,3,4] 2
[2,4,6,8]
ghci> scalevec [1.5,3,4.5,6] 0.33
[0.495,0.99,1.485,1.98]
--}

--inverse of vector
inversevec :: Num b => [b] -> [b]
inversevec = map negate
{--
ghci> inversevec [1,2,3,4]
[-1,-2,-3,-4]
--}

--vector length
vectorLength :: (Num a, Floating a) => [a] -> a
vectorLength v = sqrt (sum (map (^2) v))
{-- Python implementation - input of [1,2,3,4] yields 5.477225575051661 in both implementations:
import math

def vectorLength(x):
    sum = 0
    for i in x:
        sum += i ** 2
    return math.sqrt(sum)

print(vectorLength([1,2,3,4]))
--}
vectorDist :: (Floating a) => [a] -> [a] -> a
vectorDist
--vector distance
vectorDist :: (Floating a) => [a] -> [a] -> a
vectorDist a b = vectorLength(addvec a (inversevec b))


--ALL RANDOM # GENERATION IS DETERMINISTIC AND REFERENTIALLY TRANSPARENT
--uses System.Random.PCG from pcg-random
randVectorsFromSeed :: [[Double]]
randVectorsFromSeed = runST $ do
        g <- initialize 1 2 -- ^ <- is the monadic bind operator. This immediately runs the action, gets its result and binds to g
        replicateM 25 (replicateM 4 (uniformR (0.00, 400.00) g))
        --creates a list containing 25 lists each containing 4 doubles. i.e. a list of 25 4d coordinates
        --replicateM is used to replicate monadic actions, advancing the monadic object (seed in this case) upon each "use"

randLatenciesFromSeed :: [Double]
randLatenciesFromSeed = runST $ do
        g <- initialize 3 4         -- \/ arbitrary
        replicateM 300 (uniformR (0.00, 400.00) g)


initializeRandomCoordinates :: Map Int [Double]--(f a)
initializeRandomCoordinates =
        Map.fromList (
                zip
                        [1..25]
                        randVectorsFromSeed
        )

initializeRandomLatencies :: Map (Int, Int) Double
initializeRandomLatencies =
        Map.fromList (
                zip
                        (filterDuplicateTuples (concat $ zipWith (zip . repeat) [1..25] $ Data.List.tails [1..25]))
                        randLatenciesFromSeed
        )

--parsing
data PingEntry = PingEntry { destHost :: String, rtt :: String } deriving Show
--destHost and rtt

--returns "Just" the two values if present, and Nothing if not
parseLine (_:_:_:destHost:_:_:rtt:_) = Just $ PingEntry destHost rtt
parseLine _ = Nothing


prettyPrint :: PingEntry -> IO ()
prettyPrint (PingEntry destHost rtt) = putStrLn $ rtt ++ "ms to " ++ destHost



tupleSymmetry :: Eq a => (a, a) -> (a, a) -> Bool
tupleSymmetry (x,y) (a,b) =
        x == a && y == b || x == b && y == a || x == y

--https://www.seas.upenn.edu/~cis194/fall16/lectures/04-typeclasses.html - "The Eq type class - CIS194"
filterDuplicateTuples :: Eq a => [(a, a)] -> [(a, a)]
                        --(uncurry (/=)) is the same as (\(x,y) -> x /= y) which is the same as (\(x,y) -> not (x == y))
filterDuplicateTuples = filter (uncurry (/=))--(Data.List.nubBy tupleSymmetry x)
                                                -- ^removes elements according to the tupleSymmetry condition

fallibleLookup :: (Ord k, MonadFail m) => k -> Map.Map k a -> m a
fallibleLookup k = maybe (fail "fallibleLookup: Key not found") pure . Map.lookup k
--I know this is bad practice, but it works. https://stackoverflow.com/questions/31898658/the-maybe-result-from-map-lookup-is-not-type-checking-with-my-monad-transformer
--I don't know why or how, but it allows a failure case without a Maybe monad (random numbers didn't play nice for some reason)

errdist :: () => (Map Int [Double],Map (Int, Int) Double) -> (Int, Int) -> Double
errdist maps latencyid =
                --fallibleLookup returns type (m a). fromJust converts this to a "Just" value to enable arithmetic
                (Data.Maybe.fromJust (fallibleLookup latencyid (snd maps)) -
                vectorDist (Data.Maybe.fromJust (fallibleLookup (fst latencyid) (fst maps))) (Data.Maybe.fromJust (fallibleLookup (snd latencyid) (fst maps)))) **2


err :: (Show Double) => (Map Int [Double], Map (Int, Int) Double) -> Double
err maps =
        --sum (map (`errdist` maps) (filterDuplicateTuples (concat $ zipWith (zip . repeat) [1..25] $ Data.List.tails [1..25])))
        --backticks turn function errdist into an operator, allowing it to be passed the maps. requires switching order of args

        Debug.Trace.traceShow (sum (map (errdist maps) (filterDuplicateTuples (concat $ zipWith (zip . repeat) [1..25] $ Data.List.tails [1..25]))) / 300 ) (sum (map (errdist maps) (filterDuplicateTuples (concat $ zipWith (zip . repeat) [1..25] $ Data.List.tails [1..25]))) / 300 )
                                                                                                                                                 --    ^ #of iterations. is static
        --sum (map (\x -> errdist maps x) (filterDuplicateTuples (concat $ zipWith (zip . repeat) [1..25] $ Data.List.tails [1..25])))
        --lambda that allows maps to be passed into errdist
-- ^final error value	^applies the preceding function to all latencies, replacing each item with the result



groupDuplicates :: [(Int, [Double])] -> [[(Int, [Double])]]
groupDuplicates = Data.List.groupBy (\(a,b) (x,y) -> a == x)

averageChanges :: [(Int, [Double])] -> [(Int, [Double])]
averageChanges xs = zip
                        (map (head . map fst) (groupDuplicates xs)) -- ordered list of keys
                        (map (meanvec . map snd) (groupDuplicates xs)) --ordered list of averaged coordinates

meanvec :: [[Double]] -> [Double]
meanvec xs = map (/ Data.List.genericLength xs) (foldr1 (zipWith (+)) xs)
--maps the function "divide by length" to the "sum of an arbitrary # of vectors of arbitrary but equal length"
-- [(1,[1.00,2.00]),(2,[5.00,6.00]),(1,[4.00,5.00]),(1,[7.00,6.00]),(2,[2.00,4.00]),(2,[5.00,7.00]),(2,[7.00,8.00]),(2,[9.00,10.00]),(3,[1.00,2.00]),(3,[8.00,9.00]),(3,[10.00,11.00]),(3,[3.00,4.00]),(4,[1.00,2.00]),(4,[4.00,5.00]),(4,[6.00,7.00]),(4,[10.00,11.00])]
--(\[(a, b)] -> (a ,average b))

-- maps = (hosts, latencies)
normalizeMap :: (Map Int [Double], Map (Int, Int) Double) -> (Map Int [Double], Map (Int, Int) Double)
normalizeMap maps =
        if err maps - 1500 < 16000 then --This is wrong, > needs to be <, but I want it to run to completion. Error value is increasing
        --arbitrary cutoff^
                maps --concretizes the finished map and returns the tuple
        else
                --maps repositionSingleCoordinate to host-pairs yielding a list of "changes" in key/value tuples, list is converted to an Ordered Map, left-biased union applies the changes to the map
                --map is then recursively normalized until err condition is met
                normalizeMap (Map.union (Map.fromList (averageChanges (map (repositionSingleCoordinate maps) (filterDuplicateTuples (concat $ zipWith (zip . repeat) [1..25] $ Data.List.tails [1..25]))))) (fst maps), snd maps)

repositionSingleCoordinate :: (Map Int [Double], Map (Int, Int) Double) -> (Int, Int) -> (Int, [Double])
repositionSingleCoordinate maps latencyid =
        (fst latencyid,
                addvec
                        (Data.Maybe.fromJust (fallibleLookup (fst latencyid) (fst maps))) --source
                        (scalevec
                                (addvec
                                        [100, 100, 100, 100] --arbitrary, shouldn't matter
                                        (scalevec
                                                (addvec (Data.Maybe.fromJust (fallibleLookup (fst latencyid) (fst maps))) (inversevec (Data.Maybe.fromJust (fallibleLookup (snd latencyid) (fst maps)))))
                                                ((Data.Maybe.fromJust (fallibleLookup latencyid (snd maps)) - vectorLength (addvec (Data.Maybe.fromJust (fallibleLookup (fst latencyid) (fst maps))) (inversevec (Data.Maybe.fromJust (fallibleLookup (snd latencyid) (fst maps)))))) /
                                                        vectorLength (addvec (Data.Maybe.fromJust (fallibleLookup (fst latencyid) (fst maps))) (inversevec (Data.Maybe.fromJust (fallibleLookup (snd latencyid) (fst maps))))))
                                                ))
                                0.002))



class Pretty a where
        ppr :: a -> PB.Box

instance Pretty String where
        ppr = PB.text

instance Pretty Int where
        ppr = PB.text . show

instance Pretty Double where
        ppr = PB.text . show

instance Pretty [Double] where
        ppr = PB.text . show

instance Pretty [(Int, Int)] where
        ppr = PB.text . show

instance Pretty [Int] where
        ppr = PB.text . show

col :: (Pretty a, Pretty t) => (t, [a]) -> PB.Box
col (a, xs) = PB.vcat PB.left $ lab ++ vals
        where
                lab = [ppr a]
                vals = fmap ppr xs

formatCoordinates :: (Map Int [Double], Map (Int, Int) Double) -> String
formatCoordinates maps = PB.render $ PB.hsep 1 PB.left $ fmap col cols
        where
                cols :: [([Int], [[Double]])]
                cols = [
                        (Map.keys (fst maps), Map.elems (fst maps))]

formatLatencies :: (Map Int [Double], Map (Int, Int) Double) -> String
formatLatencies maps = PB.render $ PB.hsep 1 PB.left $ fmap col cols
        where
                cols :: [([(Int, Int)], [Double])]
                cols = [
                        (Map.keys (snd maps), Map.elems (snd maps))]


main :: IO () --(Random a, Num a, Ord a, Floating a) => (Map Int [a], Map (Int, Int) a)
main =
        let
                --based upon pure, seeded, random number generation
                --a = normalizeMap (initializeRandomCoordinates, initializeRandomLatencies)
                --based upon parsed data
                a = normalizeMap (initializeParsedCoordinates, initializeParsedLatencies)
                b = formatCoordinates a
                c = formatLatencies a
        in
                putStrLn b
