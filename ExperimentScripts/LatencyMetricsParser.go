package main

import (
	"encoding/csv"
	"fmt"
	"net/http"
	"time"
)

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
			q1: line[4],
			md: line[5],
			q3: line[6],
			high: line[7],
		}
		data = append(data, row)
	}
	return data, nil
}

func main() {
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

	for _, row := range data {
		fmt.Println(row.Date + "\t\t " + row.Source + " \t\t " + row.Server + " \t\t " + row.Low + " \t\t " + row.Q1+ " \t\t " + row.MD + " \t\t " + row.Q3 + " \t\t " + row.High)
	}
	fmt.Printf("using latency data from region: %s", data[5].Source)
}
