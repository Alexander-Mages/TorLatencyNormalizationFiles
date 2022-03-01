// Dummy no-op pluggable transport client. Works only as a managed proxy.
//
// Usage (in torrc):
// 	UseBridges 1
// 	Bridge dummy X.X.X.X:YYYY
// 	ClientTransportPlugin dummy exec dummy-client
//
// Because this transport doesn't do anything to the traffic, you can use any
// ordinary relay's ORPort in the Bridge line; it doesn't have to declare
// support for the dummy transport.
package main

import (
	"bufio"
	"encoding/csv"
	"fmt"
	"io"
	"log"
	"net"
	"net/http"
	"os"
	"os/signal"
	"sync"
	"syscall"
	"time"
	"strconv"
	"net/textproto"
	"strings"
	"regexp"
)

import "git.torproject.org/pluggable-transports/goptlib.git"

var ptInfo pt.ClientInfo

// When a connection handler starts, +1 is written to this channel; when it
// ends, -1 is written.
var handlerChan = make(chan int)

var LatencyAddition int

type Record struct {
	Date string
	Source string
	Server string
	Low string
	Q1 string
	MD string
	Q3 string
	High string
}

//control port
const SockAddr = "/tmp/control.sock"

type customConn struct {
	net.Conn
}

func newClientConn(conn net.Conn) (c *customConn) {
	c = &customConn{conn}
	return
}

//func (conn *customConn) Read(b []byte) (n int, err error) {
//	_, err = conn.Read(b)
//	return
//
//}
func (conn *customConn) Write(b []byte) (n int, err error) {
	time.Sleep(time.Duration(LatencyAddition) * time.Millisecond)
	n, err = conn.Conn.Write(b)
	return n, err
}

func copyLoop(a, b net.Conn) {
	var wg sync.WaitGroup
	wg.Add(2)

	go func() {
		io.Copy(b, a)
		wg.Done()
	}()
	go func() {
		io.Copy(a, b)
		wg.Done()
	}()

	wg.Wait()
}

func handler(conn *pt.SocksConn) error {
	handlerChan <- 1
	defer func() {
		handlerChan <- -1
	}()

	defer conn.Close()
	FirstRemote, err := net.Dial("tcp", conn.Req.Target)
	if err != nil {
		conn.Reject()
		return err
	}
	remote := newClientConn(FirstRemote)
	defer remote.Close()
	err = conn.Grant(remote.RemoteAddr().(*net.TCPAddr))
	if err != nil {
		return err
	}
	copyLoop(conn, remote)

	return nil
}

func acceptLoop(ln *pt.SocksListener) error {
	defer ln.Close()
	for {
		conn, err := ln.AcceptSocks()
		if err != nil {
			if e, ok := err.(net.Error); ok && !e.Temporary() {
				return err
			}
			continue
		}
		go handler(conn)
	}
}



//COMMANDS: (case insensitive)
//start
//stop
//latency {int}
func controlPortServer(data []Record, c net.Conn) {
	log.Printf("Client Connected [%s]", c.RemoteAddr().Network())
	rdr := bufio.NewReader(c)
	reader := textproto.NewReader(rdr)
	defer c.Close()
	for {
		command, err := reader.ReadLine()
		if err != nil {
			fmt.Println("read machine broke (ง ͠° ͟ل͜ ͡°)ง : ", err)
		}
		if strings.EqualFold(command, "stop") {
			//Stop Transport
		} else if strings.EqualFold(command, "start") {
			//Start Transport
		} else if matchbool, _ := regexp.Match("^latency\\s\\d{2,5}", []byte(command)); matchbool {
			re := regexp.MustCompile("[0-9]+")
			latency := re.FindAllString(command, -1)
			FinalMeasuredLatency, _ := strconv.Atoi(fmt.Sprint(latency))
			LatencyAddition = calculateLatencyAddition(data, FinalMeasuredLatency)
		} else {
			fmt.Println("invalid command")
		}
	}
}

func startControlPort(data []Record) {
	if err := os.RemoveAll(SockAddr); err != nil {
		log.Fatal(err)
	}

	l, err := net.Listen("unix", SockAddr)
	if err != nil {
		log.Fatal("listen error", err)
	}
	defer l.Close()

	for {
		conn, err := l.Accept()
		if err != nil {
			log.Fatal("accept error", err)
		}
		controlPortServer(data, conn)
	}
}


func fetchLatencyMetrics(url string) ([][]string, error) {
	resp, err := http.Get(url)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	reader := csv.NewReader(resp.Body)
	reader.Comment = '#'
	//note^ '' specifies a rune (seems like a char?), but "" specifies a string
	reader.FieldsPerRecord = -1
	rawdata, err := reader.ReadAll()
	if err != nil {
		fmt.Println(err)
	}
	return rawdata, nil
}

func parseLatencyMetrics(rawdata [][]string) ([]Record, error) {
	var data []Record
	for _, line := range rawdata {
		row := Record{
			Date: line[0],
			Source: line[1],
			Server: line[2],
			Low: line[3],
			Q1: line[4],
			MD: line[5],
			Q3: line[6],
			High: line[7],
		}
		data = append(data, row)
	}
	return data, nil
}

func calculateLatencyAddition(data []Record, MeasuredLatency int) (latencyAddition int) {
	//convert strings to integers, has to be done seperately due to two return values
	High, _ := strconv.Atoi(data[5].High)
	Q3, _ := strconv.Atoi(data[5].Q3)
	MD, _ := strconv.Atoi(data[5].MD)
	Q1, _ := strconv.Atoi(data[5].Q1)
	Low, _ := strconv.Atoi(data[5].Low)


	//IMPORTANT NOTE
	//make sure the thing doesnt break if an invalid measurement is passed (negative number, 0, float, etc..)
	//brackets are hard coded right now for simplicity
	if MeasuredLatency > 1500{
		//fmt.Println("nothing we can do, latency higher than highest outlier bracket")
	} else if MeasuredLatency > High {
		//fmt.Printf("latency higher than collected outlier, normalizing to artificial highest bracket of 1500ms")
		latencyAddition = 1500 - MeasuredLatency
	} else if MeasuredLatency > Q3 {
		//fmt.Printf("latency above 75th percentile and below highest outlier, normalizing to high outlier of %s", data[5].High)
		latencyAddition = High - MeasuredLatency
	} else if MeasuredLatency > MD {
		//fmt.Printf("latency is above median and below 75th percentile, normalizing to 75th percentile of %s", data[5].Q3)
		latencyAddition = Q3 - MeasuredLatency
	} else if MeasuredLatency > Q1 {
		//fmt.Printf("Latency is above 25th percentile and below median, normalizing latency to median of %s", data[5].MD)
		latencyAddition = MD - MeasuredLatency
	} else if MeasuredLatency > Low {
		//fmt.Printf("Latency is above lowest outlier but below 25th percentile, normalizing to 25th percentile of %s", data[5].Q1)
		latencyAddition = Q1 - MeasuredLatency
	} else if MeasuredLatency < Low {
		//fmt.Printf("latency lower than lowest outlier, normalizing to low outlier of %s", data[5].Low)
		latencyAddition = Low - MeasuredLatency
	}
	//in case this hellish piece of code doesn't print it
	//fmt.Printf("adding %i of latency to measured latency of %i to normalize it to target latency of %i", latencyAddition, MeasuredLatency, LatencyAddition + MeasuredLatency)
	//etc....
	return latencyAddition
}

func main() {
	var err error
	LatencyAddition = 0
	time.Sleep(7 * time.Second)

	//using the US data for now
	now := time.Now()
	SubtractedTime := now.Add(-time.Hour * 48)

	//this confused me, Jan 2 2006 is the formatting date for Go. This date is formatted in the desired way in the layout param
	FinalDate := SubtractedTime.Format("2006-01-02")
	url := fmt.Sprintf("https://metrics.torproject.org/onionperf-latencies.csv?start=%s&end=%s&server=public", FinalDate, now.Format("2006-01-02"))

	rawdata, err := fetchLatencyMetrics(url)
	if err != nil {
		fmt.Println(err)
	}
	data, _ := parseLatencyMetrics(rawdata)
	/*
	for _, row := range data {
		fmt.Println(row.Date + "\t\t " + row.Source + " \t\t " + row.Server + " \t\t " + row.Low + " \t\t " + row.Q1+ " \t\t " + row.MD + " \t\t " + row.Q3 + " \t\t " + row.High)
	}
	fmt.Printf("using latency data from region: %s", data[5].Source)
	fmt.Printf("Average user latencies are as follows:\n25th percentile:%s\nmedian:%s\n75th percentile:%s\n", data[5].Q1, data[5].MD, data[5].Q3)
	fmt.Printf("latency range including outliers: %s - %s", data[5].Low, data[5].High)
	*/
	go startControlPort(data)

	ptInfo, err = pt.ClientSetup([]string{"dummy"})
	if err != nil {
		os.Exit(1)
	}

	listeners := make([]net.Listener, 0)
	for _, methodName := range ptInfo.MethodNames {
		switch methodName {
		case "dummy":
			ln, err := pt.ListenSocks("tcp", "127.0.0.1:0")
			if err != nil {
				pt.CmethodError(methodName, err.Error())
				break
			}
			go acceptLoop(ln)
			pt.Cmethod(methodName, ln.Version(), ln.Addr())
			listeners = append(listeners, ln)
		default:
			pt.CmethodError(methodName, "no such method")
		}
	}
	pt.CmethodsDone()

	var numHandlers int = 0
	var sig os.Signal
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)

	// wait for first signal
	sig = nil
	for sig == nil {
		select {
		case n := <-handlerChan:
			numHandlers += n
		case sig = <-sigChan:
		}
	}
	for _, ln := range listeners {
		ln.Close()
	}

	if sig == syscall.SIGTERM {
		return
	}

	// wait for second signal or no more handlers
	sig = nil
	for sig == nil && numHandlers != 0 {
		select {
		case n := <-handlerChan:
			numHandlers += n
		case sig = <-sigChan:
		}
	}
}
