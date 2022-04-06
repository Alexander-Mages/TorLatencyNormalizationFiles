--make integers Float
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

let origin = Coordinates 0 0 0
    newpoint = Coordinates 1 1 1
    --initializes list of coordinates
    map = [origin, newpoint]
    rtt = Float 100
newlocal <- update rtt origin newPoint
--replaces first element in "map" list with the new local coordinate
map & element 0 .~ newlocal
--"show" map
putStrLn show(map)
--calculate and show distance betweeen two nodes
dist = distEquation (map ^? element 0) (map ^? element 1)
--don't think I need to use show here, but it's here in this glorified pseudocode
putStrLn show(dist)