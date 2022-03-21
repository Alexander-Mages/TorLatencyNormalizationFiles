package main

import (
	"fmt"
	"github.com/eugene-eeo/vivaldi-go"
)

func main() {
	local := vivaldi.NewContext()
	//instantiates a coordinate map
	//i.e. creates point at origin
	//calls NewContextFromValues(NewHVector(0,0,0), InitialError)


	remote := vivaldi.NewHVector(
		5.0, // x
		5.0, // y
		5.0, // height
	)
	//sets the location of the remote server in respect to the origin
	//just instantiates the object w/ it's location attributes


	rtt := 5.0


	local.Update(rtt, vivaldi.NewContextFromValues(
		remote,
		5.0, // error estimate
	))
	//adds remote vector to map according to it's coordinates, along with it's rtt to the origin

	secondrtt := 20.0

	remotetwo := vivaldi.NewHVector(
		5,5,5)
	local.Update(secondrtt, vivaldi.NewContextFromValues(
		remotetwo,
		5.0))


	newrtt, err := local.EstimateRTT(remotetwo)
	fmt.Println(newrtt)
	fmt.Println(err)
}
