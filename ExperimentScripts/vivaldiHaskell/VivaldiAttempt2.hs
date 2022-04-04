
newtype CoordinateMap = CoordinateMap { 
                                      x :: Int 
                                    , y :: Int 
                                    , z :: Int 
                                    }


--type Vivaldi definition, returns type Vivaldi
--constructors: Coordinates creates custom point (origin), Update takes parameters RTT, and LocalCoordinates + RemoteCoordinates of type Vivaldi

data Vivaldi = Coordinates Int Int Int
            | Update Int Coordinates Coordinates
   
--specifies that map should be of type Vivaldi
map :: Vivaldi
--gives the map a point (origin). i.e. initializes the coordinate system
map = Coordinates 0 0 0



main = do

    Vivaldi :: Coordinates 0 0 0
    Vivaldi :: Update 100 1 0 0
