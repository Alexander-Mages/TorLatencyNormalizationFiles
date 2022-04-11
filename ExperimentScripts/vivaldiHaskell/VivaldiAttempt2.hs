import Data.Map (Map)
import qualified Data.Map as Map
-- ^ imports the Map type normally, imports the Map methods as qualified names (only avilable using full name/path)
-- ^the tutorial did it like this, so I'm doing the same for now

--type declaration, and data constructor
data Vivaldi = Coordinates {  x :: Float
                            , y :: Float
                            , z :: Float
                            }
            
--Function declaration: function name, argument list, and output
update :: (Vivaldi a) => (Float a, Coordinates a, Coordinates a) -> Vivaldi

--(local - remote) needs to be fixed. can use vector pattern matching as shown in this article: learnyouahaskell.com/syntax-in-functions, 
--Function definition: actually defines the function
--Takes rtt, local, and remote coordinates. Returns updated local coordinates
update rtt local remote = local + ((rtt - abs(local - remote)) * (1 {- < "unit-length vector"-} * (local - remote)))

--function declaration
distEquation :: (Float a) => (Coordinates a, Coordinates a) -> Float
--function definition
--takes local and remote coordinates, returns coordinate distance between the two
distEquation local remote = (z local) + (z remote) + sqrt(  (((x local)-(x remote))^2) + (((y local)-(y remote))^2)  )


--Type declaration, specifies objects to be of type Vivaldi
origin :: Vivaldi
newpoint :: Vivaldi

let initialMap = Data.Map.fromList [("origin", (Coordinates 0 0 0)), ("firstPoint", (Coordinates 1 1 1))]
    threeItemMap = Map.insert "secondPoint" (Coordinates 2 2 2) initialMap
    --maps Coordinates 0 0 0 to key "origin", and inserts it into the map
    rtt = Float 100

map ! "origin" <- update rtt origin newPoint

--calculate and show distance betweeen two nodes
dist = distEquation map ! "origin" map ! "firstPoint"

