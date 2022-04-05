
newtype CoordinateMap = CoordinateMap { 
                                      x :: Int 
                                    , y :: Int 
                                    , z :: Int 
                                    }


--type Vivaldi definition, returns type Vivaldi
--constructors: Coordinates creates custom point (origin), Update takes parameters RTT, and LocalCoordinates + RemoteCoordinates of type Vivaldi

data Vivaldi = Coordinates Int Int Int
            
--a is every type, i.e., avoids specifying type
--at least I think
Update :: (Vivaldi a) => (Int a, Coordinates a, Coordinates a) -> Vivaldi
--(local - remote) needs to be fixed. can use vector pattern matching as shown in this article: learnyouahaskell.com/syntax-in-functions, 
--math derived from figure 2 in vivaldi paper: "the simple vivaldi algorithm with a constant timestep"
--tuning parameter?
Update rtt local remote = local + (a * (local - remote))
   
--specifies that map should be of type Vivaldi
origin :: Vivaldi
--gives the map a point (origin). i.e. initializes the coordinate system
let origin = Coordinates 0 0 0
let newPoint = Coordinates 1 1 1
--100 is RTT
firstPoint <- Update 100 origin newPoint




main = do

    Vivaldi :: Coordinates 0 0 0
    Vivaldi :: Update 100 1 0 0
