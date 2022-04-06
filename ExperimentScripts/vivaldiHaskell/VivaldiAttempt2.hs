--type Vivaldi definition, returns type Vivaldi
--constructors: Coordinates creates custom point (origin), Update takes parameters RTT, and LocalCoordinates + RemoteCoordinates of type Vivaldi
--comment ^ irrelavent as of commit 7b3e2435b382c9a38624b58ee8dd0716f1658de7, Apr 5
--make integers Float
data Vivaldi = Coordinates Int Int Int
            
--a is every type, i.e., avoids specifying type
--at least I think
Update :: (Vivaldi a) => (Int a, Coordinates a, Coordinates a) -> Vivaldi
--(local - remote) needs to be fixed. can use vector pattern matching as shown in this article: learnyouahaskell.com/syntax-in-functions, 
--math derived from figure 2 in vivaldi paper: "the simple vivaldi algorithm with a constant timestep"
--tuning parameter?
Update rtt local remote = local + (u * (local - remote))
   
--specifies that map should be of type Vivaldi
origin :: Vivaldi
--gives the map a point (origin). i.e. initializes the coordinate system
let origin = Coordinates 0 0 0
let newPoint = Coordinates 1 1 1
--100 is RTT
map <- Update 100 origin newPoint

