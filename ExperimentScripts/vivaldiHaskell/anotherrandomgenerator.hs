import System.Random
import Control.Monad

rand :: (Random r) -> (r,r) -> State StdGen r
rand (min,max) = state (RandomR (min,max))