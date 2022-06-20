{-# OPTIONS_GHC -Wno-unrecognised-pragmas #-}
{-# LANGUAGE FlexibleInstances #-}
{-# HLINT ignore "Avoid lambda" #-}
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
import Data.List.Split
import Debug.Trace
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


--initializeCoordinates :: Map Integer (Vector Double)
initializeCoordinates :: (Ord k, Enum k, Num k, Fractional a, Random a, Num a{--, MonadIO f--}) => Map k [a]--(f a)
initializeCoordinates =
        --two maps: one holds hosts, denoted host1 host2 etc... the other holds latencies, denoted latency1-2 latency2-4 etc...
        --returns map of ["host{host#}", (randomly generated 4 way vector)]
        Map.fromList (
                --"zip" combiles elements of two lists into one list of tuples | zip :: [a] -> [b] -> [(a,b)]
                zip
                        [1..25] --integers as keys
                        -- ^ \/ both must be scaled along with the # of latencies created
                        (Data.List.Split.chunksOf 4 [104.77894154,238.33919377,252.45367644,278.37766934,384.71008782,269.40096048,248.05884127,
                            161.15176188,245.72143539,312.64660111,160.61983815,271.1297967,176.35900936,350.77958234,361.36508799,173.0858584,
                            228.59745757,321.19260165,56.0556473,2.82798332,1.30090254,112.70626275,358.65075476,273.9610812,144.84056226,309.80333946,
                            216.50744441,342.16845113,191.19273557,288.66819552,342.69499616,228.3911599,12.57762972,125.98387394,211.63432099,
                            176.85088916,158.81017924,201.53078909,229.10849974,13.75018585,392.10543235,166.84778414,224.18459433,277.55757048,
                            172.52586474,393.06766417,318.21495336,195.58883417,199.73977603,365.6681926,99.20370618,230.24473535,196.77579436,
                            158.70892277,343.45702303,174.835945,62.41553314,285.14466611,202.11891177,37.23203508,215.40781024,171.73905528,
                            323.77695632,32.05122653,121.73805558,244.13938714,251.20858054,322.35691518,128.09502196,107.06840815,156.13090515,
                            277.43176905,179.32310697,35.33917395,321.10550677,18.71193606,172.64559037,332.46979165,307.96874894,340.15933101,
                            177.860077,232.55026,237.43416997,289.00827598,318.16097787,137.80225252,21.93683246,241.33252292,250.69224404,385.22814389
                            ,307.61169575,372.21634081,79.26690967,308.79284303,123.76160817,258.29228242,250.6541118,188.73274221,306.41515299,334.53449052])
                        -- ^ externally generated random numbers, breaks into lists of 4
        )

tupleSymmetry :: Eq a => (a, a) -> (a, a) -> Bool
tupleSymmetry (x,y) (a,b) =
        x == a && y == b || x == b && y == a || x == y

--https://www.seas.upenn.edu/~cis194/fall16/lectures/04-typeclasses.html - "The Eq type class - CIS194"
filterDuplicateTuples :: Eq a => [(a, a)] -> [(a, a)]
                        --(uncurry (/=)) is the same as (\(x,y) -> x /= y) which is the same as (\(x,y) -> not (x == y))
filterDuplicateTuples x = filter (uncurry (/=)) (Data.List.nubBy tupleSymmetry x)
                --removes elements according to the tupleSymmetry condition

initializeLatencies :: (Ord a, Enum a, Num a, Random b, Num b, Fractional b) => Map (a, a) b
initializeLatencies =
        Map.fromList (
                zip
                        --fills every combination of items in 2 [1..25] int lists. Scaling requires simply changing the 25 below to desired host quantity
                        (filterDuplicateTuples (concat $ zipWith (zip . repeat) [1..25] $ Data.List.tails [1..25]))
                        [149.41354194,243.59380329,177.24150784,186.36276263,333.03393327,200.85748563,67.98841369,309.44333857,348.66974922,129.45020183,
                        183.02087111,228.59545225,23.59666652,375.3592921,49.3705436,9.85847,240.40850286,201.26488938,221.61149351,295.35901272,314.63764057,
                        30.72348358,361.28646832,248.11809401,364.76924684,94.75664369,43.62376443,248.15889674,150.58125689,74.28759738,129.03095266,199.34170366,
                        291.75999045,44.31665462,146.74875086,212.84553908,376.26495041,384.62490536,208.92816645,226.85071108,399.49227936,20.20105293,
                        286.35881647,152.8455184,197.16706575,87.51467611,244.96845135,360.72735572,290.08972007,33.30094473,91.81191041,319.58396521,
                        234.30689619,371.65890374,347.18590105,282.25297766,287.4830073,183.87246121,396.01590515,47.15859617,127.41029002,286.07162161,
                        221.12610366,208.99238503,176.45246581,163.56743329,132.57034669,369.22793421,119.59828468,288.44322525,303.45981877,310.43373323,
                        247.18843291,70.21674003,91.35978023,225.06660119,267.27969887,265.22815066,32.2100996,307.8604453,267.26455645,78.91428425,11.46858911,
                        230.55934762,388.01850674,57.31062621,251.79254894,14.07520731,72.60881871,309.38639103,48.63289075,267.21357975,370.47123994,
                        295.62724737,107.58287533,113.09450654,46.39006002,293.92559649,390.6414875,186.00227458,100.01431592,17.90687409,41.08124832,
                        399.97320781,140.46343055,168.31591392,278.46684145,395.46674375,114.66318193,146.17844239,382.37861264,67.55045513,146.18924028,
                        9.37457435,325.27248975,367.39984832,148.07775854,181.62553064,24.06283789,28.16359844,158.74142679,371.57829045,150.40785955,98.81893459,
                        95.03032354,275.39649942,294.6389606,337.39739557,313.80413484,356.81344118,350.73864361,198.60406381,173.56597639,91.86295344,
                        20.25959388,41.57343878,218.06293996,179.24810889,16.66060747,139.91837141,386.28176255,354.87278516,315.74232624,108.63234158,
                        184.24423728,396.84515776,40.75499,209.26660278,200.67382049,226.28412119,18.45618301,220.40031147,205.21609394,399.62961537,
                        275.13438666,140.75586272,137.16557262,225.71931312,182.91563223,269.83014989,91.52902459,307.87906365,390.63130424,149.95139394,
                        8.51592576,33.49622323,357.51788917,280.41815137,7.99004532,61.33473248,194.30470676,195.86507768,308.83316027,288.31514314,
                        304.20391438,262.6141137,52.60168451,172.40510682,358.32386825,198.49464705,66.15373548,227.05801058,387.21612994,234.2850834,327.89736863
                        ,199.55650813,388.54967074,13.38240296,352.02174931,371.06946338,281.60065517,380.50164902,181.45530563,181.02264977,309.35020968
                        ,53.11249015,115.79773234,276.69993505,125.80994057,368.47559544,57.88799782,191.15869703,1.23774301,8.75514958,264.42254578,152.02821042
                        ,235.84081697,225.22728858,122.75403771,100.1080245,375.65151803,62.33752011,276.10424831,43.52658475,399.54667105,379.10169944,
                        185.95764105,371.54470879,35.67250787,161.87778502,144.87275544,316.752431,33.11338116,22.92051197,212.31914528,288.4181006,152.14700036,
                        88.73306455,311.10047297,345.21986305,30.81842029,202.2776702,265.38272304,215.45769909,113.27907076,192.9488753,102.27205367,250.9069872,
                        394.62476559,60.00611906,321.42281126,376.08474038,1.98763369,265.89319703,173.22924477,82.17838625,153.4459287,211.39983392,23.27697506,
                        359.11263455,265.53913372,375.12072842,126.5848316,204.90510121,194.61802476,252.05432002,388.66144082,260.09133984,301.00543134,109.99826861,
                        28.52107766,378.73786032,146.73785487,61.46690309,240.22446891,202.00092894,269.33675936,369.70750279,264.75744394,318.22099145,241.85353858,
                        258.27141275,374.93885903,139.26236118,340.63224298,108.47619065,252.3721375,184.76765866,216.76468794,376.99863571,279.47495222,356.66137244,
                        275.53241722,359.49060962,393.14102146,195.78354654,141.29436353,208.97605573,162.90234679,58.4245851,87.87878223,310.39452893,238.52648905,
                        173.1783277,139.01944014,289.39347918,372.44136198,115.05629031,286.41297442,228.90367749]
        )

fallibleLookup :: (Ord k, MonadFail m) => k -> Map.Map k a -> m a
fallibleLookup k = maybe (fail "fallibleLookup: Key not found") pure . Map.lookup k
--I know this is bad practice, but it works. https://stackoverflow.com/questions/31898658/the-maybe-result-from-map-lookup-is-not-type-checking-with-my-monad-transformer
--I don't know why or how, but it allows a failure case without a Maybe monad (random numbers didn't play nice for some reason)

errdist :: ({--Show a is for debug--}Show a, Num a, Floating a, Ord k) => (Map k [a],Map (k, k) a) -> (k, k) -> a
errdist maps latencyid =
        Debug.Trace.traceShow (abs (
                --fallibleLookup returns type (m a). fromJust converts this to a "Just" value to enable arithmetic
                (Data.Maybe.fromJust (fallibleLookup latencyid (snd maps)) -
                vectorDist (Data.Maybe.fromJust (fallibleLookup (fst latencyid) (fst maps))) (Data.Maybe.fromJust (fallibleLookup (snd latencyid) (fst maps)))) **2
        )) (abs (
                --fallibleLookup returns type (m a). fromJust converts this to a "Just" value to enable arithmetic
                (Data.Maybe.fromJust (fallibleLookup latencyid (snd maps)) -
                vectorDist (Data.Maybe.fromJust (fallibleLookup (fst latencyid) (fst maps))) (Data.Maybe.fromJust (fallibleLookup (snd latencyid) (fst maps)))) **2
        ))


err :: (Num a, Floating a, Num k, Enum k, Ord k,{--show is for debug.Trace.traceShow--} Show a, Show k) => (Map k [a], Map (k, k) a) -> a
err maps =
        --sum (map (`errdist` maps) (filterDuplicateTuples (concat $ zipWith (zip . repeat) [1..25] $ Data.List.tails [1..25])))
        --backticks turn function errdist into an operator, allowing it to be passed the maps. requires switching order of args

        Debug.Trace.traceShow ((Data.Maybe.fromJust (fallibleLookup (1,22) (snd maps))), vectorDist (Data.Maybe.fromJust (fallibleLookup (fst (1,22)) (fst maps))) (Data.Maybe.fromJust (fallibleLookup (snd (1,22)) (fst maps)))) (sum (map (errdist maps) (filterDuplicateTuples (concat $ zipWith (zip . repeat) [1..25] $ Data.List.tails [1..25]))))
        --sum (map (\x -> errdist maps x) (filterDuplicateTuples (concat $ zipWith (zip . repeat) [1..25] $ Data.List.tails [1..25])))
        --lambda that allows maps to be passed into errdist
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
normalizeMap :: (Num a, {--show is for debug.Trace.traceShow--}Show a, Ord a, Floating a) => (Map Int [a], Map (Int, Int) a) -> (Map Int [a], Map (Int, Int) a)
normalizeMap maps =
        if err maps - 1000 < -1000 then
        --arbitrary cutoff^
                maps --concretizes the finished map and returns the tuple
        else
                --Debug.Trace.trace "normalizationLoop" (normalizeMap (Map.unions (reverse (map (repositionSingleCoordinate maps) (filterDuplicateTuples (concat $ zipWith (zip . repeat) [1..25] $ Data.List.tails [1..25])))), snd maps))
                --maps repositionSingleCoordinate to host-pairs, reverses the resulting list of maps, left-bias union consolidates the changes, map is recursively normalized until err condition is met
                Debug.Trace.trace "normalizationLoop" (normalizeMap (Map.unions (reverse (map (repositionSingleCoordinate maps) (filterDuplicateTuples (concat $ zipWith (zip . repeat) [1..25] $ Data.List.tails [1..25])))), snd maps))


repositionSingleCoordinate :: (Num a, Floating a, Show a) => (Map Int [a], Map (Int, Int) a) -> (Int, Int) -> Map Int [a]
repositionSingleCoordinate maps latencyid =
        Debug.Trace.trace "doin stuff" ( Map.insert (fst latencyid) (
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
                                0.002) --scaling factor
        ) (fst maps) --map to insert into
        )


class Pretty a where
        ppr :: a -> PB.Box

instance Pretty String where
        ppr = PB.text

instance Pretty Int where
        ppr = PB.text . show

instance Pretty Float where
        ppr = PB.text . show

instance Pretty [Float] where
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

formatCoordinates :: (Map Int [Float], Map (Int, Int) Float) -> String
formatCoordinates maps = PB.render $ PB.hsep 1 PB.left $ fmap col cols
        where
                cols :: [([Int], [[Float]])]
                cols = [
                        (Map.keys (fst maps), Map.elems (fst maps))]

formatLatencies :: (Map Int [Float], Map (Int, Int) Float) -> String
formatLatencies maps = PB.render $ PB.hsep 1 PB.left $ fmap col cols
        where
                cols :: [([(Int, Int)], [Float])]
                cols = [
                        (Map.keys (snd maps), Map.elems (snd maps))]


main :: IO () --(Random a, Num a, Ord a, Floating a) => (Map Int [a], Map (Int, Int) a)
main =
        let
                a = normalizeMap (initializeCoordinates, initializeLatencies)
                b = formatLatencies a
                c = formatCoordinates a
        in
                putStrLn (b ++ c)