{-# OPTIONS_GHC -Wno-unrecognised-pragmas #-}
{-# LANGUAGE FlexibleInstances #-}
module Main where
import Data.Map.Strict (Map)
import qualified Data.Map.Strict as Map
import Data.Vector (Vector)
import qualified Data.Vector as Vector
import System.Random
import qualified Data.List
import Control.Monad.IO.Class (MonadIO)
import Data.Maybe
import qualified Text.PrettyPrint.Boxes as PB
import GHC.Base (Double)
--import Graphics.Win32 (bLACKONWHITE)
{--
import qualified GHC.Exts.Heap as PB
import qualified Distribution.Compat.CharParsing as PB
import Numeric (showGFloatAlt)
import qualified GHC.Exts.Heap as PB
import Data.Map.Internal.Debug (validsize)
import Data.String (String)
import Text.XHtml (cols)
--}

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
addvec = zipWith (+)
{--
--vector scaling
scalevec :: [Double] -> Double -> Vector Double
scalevec a b =
	-- ^ ^ Vector, scale factor
	Vector.fromList [(b * (a !! 0)), (b * (a !! 1)), (b * (a !! 2)), (b * (a !! 3))]
					-- ^ ^ ^ ^
					--scale factor, key, vector, key of new coordinate
--}
scalevec :: Num b => [b] -> b -> [b]
scalevec a b = map (b*) a

inversevec :: Num b => [b] -> [b]
inversevec = map negate

--vector length
vectorLength :: (Num a, Floating a) => [a] -> a
vectorLength v = sqrt (sum (map (^2) v))

--vector distance
vectorDist :: (Floating a) => [a] -> [a] -> a
vectorDist a b = vectorLength(addvec a (inversevec b))
                        --scale instead of ^

--random number generator (between 1 and 400)
--randomNum :: (Random a, Num a{--, MonadIO f--}, Num b) => b -> a
--randomNum = randomRs (1.00, 400.00) <$> newStdGen
--anothaNum :: Int -> [Float]--(Num a, Random a, MonadIO f) => [b]
--anothaNum quantity = do
        --g <- newStdGen
        --take quantity $ randomRs (1.00, 400.00) g

numm :: IO Double
numm = getStdRandom (randomR (1.00,400.00))

--initializeCoordinates :: Map Integer (Vector Double)
initializeCoordinates :: Map Int [IO Double]
initializeCoordinates =
        --two maps: one holds hosts, denoted host1 host2 etc... the other holds latencies, denoted latency1-2 latency2-4 etc...
        --returns map of ["host{host#}", (randomly generated 4 way vector)]
        Map.fromList (
                --"zip" combiles elements of two lists into one list of tuples | zip :: [a] -> [b] -> [(a,b)]
                zip
                        [0..25] --integers as keys
                        -- ^ \/ both must be scaled along with the # of latencies created
                        (replicate 25 [numm, numm, numm, numm])
                        -- ^ replicate :: Int -> a -> [a], creates list of length of first argument and value of second
        )

tupleSymmetry :: Eq a => (a, a) -> (a, a) -> Bool
tupleSymmetry (x,y) (a,b) =
        (x == a && y == b) || (x == b && y == a) || (x == y)

--https://www.seas.upenn.edu/~cis194/fall16/lectures/04-typeclasses.html - "The Eq type class - CIS194"
filterDuplicateTuples :: Eq a => [(a, a)] -> [(a, a)]
                        --(uncurry (/=)) is the same as (\(x,y) -> x /= y) which is the same as (\(x,y) -> not (x == y))
filterDuplicateTuples x = filter (uncurry (/=)) (Data.List.nubBy tupleSymmetry x)
                --removes elements according to the tupleSymmetry condition

initializeLatencies :: Map (Int, Int) (IO Double)
initializeLatencies =
        Map.fromList (
                zip
                        --fills every combination of items in 2 [1..25] int lists. Scaling requires simply changing the 25 below to desired host quantity
                        (filterDuplicateTuples (concat $ zipWith (zip . repeat) [1..25] $ Data.List.tails [1..25]))
                        (replicate 300 numm) -- [283,13,398]... note: must be scaled according to the keys, "length concat $ zipWith (zip . repeat) [1..25] $ tails [1..25]"
        )
        --should be identical to the above: ghci> let maapp = Data.Map.Strict.fromList $ zip ((concat $ zipWith (zip . repeat) [1..25] $ Data.List.tails [26..50])) (Prelude.take 325 (iterate (+1) 1))
        --ghci> Data.Map.Strict.lookup (23,48) maapp
                --Just 320

fallibleLookup :: (Ord k, MonadFail m) => k -> Map.Map k a -> m a
fallibleLookup k = maybe (fail "fallibleLookup: Key not found") pure . Map.lookup k
--I know this is bad practice, but it works. https://stackoverflow.com/questions/31898658/the-maybe-result-from-map-lookup-is-not-type-checking-with-my-monad-transformer
--I don't know why or how, but it allows a failure case without a Maybe monad (random numbers didn't play nice for some reason)

errdist :: (Map Int [IO Double], Map (Int, Int) (IO Double)) -> (Int, Int) -> IO Double
errdist maps latencyid =
        abs (
                --fallibleLookup returns type (m a). fromJust converts this to a "Just" value to enable arithmetic
                (Data.Maybe.fromJust (fallibleLookup latencyid (snd maps)) -
                vectorDist (Data.Maybe.fromJust (fallibleLookup (fst latencyid) (fst maps))) (Data.Maybe.fromJust (fallibleLookup (snd latencyid) (fst maps)))) **2
        )

err :: (Map Int [IO Double], Map (Int, Int) (IO Double)) -> IO Double
err maps =
        sum (map (errdist maps) (filterDuplicateTuples (concat $ zipWith (zip . repeat) [1..25] $ Data.List.tails [1..25])))
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

-- maps = (hosts, latencies)
normalizeMap :: {--(Num a, Ord a, Floating a, Random a) => --}(Map Int [IO Double], Map (Int, Int) (IO Double)) -> (Map Int [IO Double], Map (Int, Int) (IO Double))
normalizeMap maps =
        if (err maps - 1000) < 100 then
        --arbitrary cutoff^
                maps --concretizes the finished map and returns the tuple
        else
                normalizeMap (Map.unions (reverse (map (repositionSingleCoordinate maps) (filterDuplicateTuples (concat $ zipWith (zip . repeat) [1..25] $ Data.List.tails [1..25])))), snd maps)
                --maps repositionSingleCoordinate to host-pairs, reverses the resulting list of maps, left-bias union consolidates the changes, map is recursively normalized until err condition is met

repositionSingleCoordinate :: (Map Int [IO Double], Map (Int, Int) (IO Double)) -> (Int, Int) -> Map Int [IO Double]
repositionSingleCoordinate maps latencyid =
        Map.insert (fst latencyid) (
                addvec
                        (Data.Maybe.fromJust (fallibleLookup (fst latencyid) (fst maps))) --source
                        (scalevec
                                (addvec
                                        [200.00, 200.00, 200.00, 200.00]
                                        (scalevec
                                                (addvec (Data.Maybe.fromJust (fallibleLookup (fst latencyid) (fst maps))) (inversevec (Data.Maybe.fromJust (fallibleLookup (snd latencyid) (fst maps)))))
                                               ((Data.Maybe.fromJust (fallibleLookup (latencyid) (snd maps)) - vectorLength (addvec (Data.Maybe.fromJust (fallibleLookup (fst latencyid) (fst maps))) (inversevec (Data.Maybe.fromJust (fallibleLookup (snd latencyid) (fst maps)))))) /
                                                        vectorLength (addvec (Data.Maybe.fromJust (fallibleLookup (fst latencyid) (fst maps))) (inversevec (Data.Maybe.fromJust (fallibleLookup (snd latencyid) (fst maps))))))
                                                ))
                                0.002) --scaling factor
        ) (fst maps) --map to insert into



class Pretty a where
        ppr :: a -> PB.Box

instance Pretty String where
        ppr = PB.text

--instance Pretty Int where
    --    ppr = PB.text . show

instance Pretty (IO Double) where
        ppr = PB.text . show

instance Pretty [IO Double] where
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

formatCoordinates :: (Map Int [IO Double], Map (Int, Int) (IO Double)) -> String
formatCoordinates maps = PB.render $ PB.hsep 1 PB.left $ fmap col cols
        where
                cols :: [([Int], [[IO Double]])]
                cols = [
                        (Map.keys (fst maps), Map.elems (fst maps))]

formatLatencies :: (Map Int [IO Double], Map (Int, Int) (IO Double)) -> String
formatLatencies maps = PB.render $ PB.hsep 1 PB.left $ fmap col cols
        where
                cols :: [([(Int, Int)], [IO Double])]
                cols = [
                        (Map.keys (snd maps), Map.elems (snd maps))]


main :: IO () --(Random a, Num a, Ord a, Floating a) => (Map Int [a], Map (Int, Int) a)
main = do
        coords <- initializeCoordinates
        latencies <- initializeLatencies
        yield <- normalizeMap (coords, latencies)
        print (formatLatencies yield ++ formatCoordinates yield)