import System.Random
import Control.Monad.State.Lazy

randomnum :: Random r => (r,r) -> State StdGen r
randomnum (min,max) = state (randomR (min,max))

randCoord :: State StdGen (Float, Float)
randCoord = do
    x <- random (0, 400)
    y <- random (0, 400)
    print (read x, read y)

main = do
    randCoord

