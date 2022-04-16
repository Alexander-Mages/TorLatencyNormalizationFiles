import System.Random (newStdGen, randomRs, Random, RandomGen)

main :: IO ()
main = do
  gen <- newStdGen
  print $ randomList 4 0 400 gen

randomList :: (Random a, RandomGen g) => Int -> a -> a -> g -> [a]
randomList len lo hi gen = take len $ randomRs (lo, hi) gen