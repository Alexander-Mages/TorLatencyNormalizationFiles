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
	q1 string
	md string
	q3 string
	high string
}

func fetchMetrics(url string) ([]Record, error) {
	resp, err := http.Get(url)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	reader := csv.NewReader(resp.Body)
	reader.Comment = '#'
	//note^ '' specifies a rune (basically a char), but "" specifies a string
	reader.FieldsPerRecord = -1
	csvLines, err := reader.ReadAll()
	if err != nil {
		fmt.Println(err)
	}

	var data []Record
	for _, line := range csvLines {
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
	FinalDate := SubtractedTime.Format("2006-01-02")
	url := fmt.Sprintf("https://metrics.torproject.org/onionperf-latencies.csv?start=%s&end=%s&server=public", FinalDate, now.Format("2006-01-02"))
	data, err := fetchMetrics(url)
	if err != nil {
		panic(err)
	}
	for _, row := range data {
		fmt.Println(row.Date + "\t\t " + row.Source + " \t\t " + row.Server + " \t\t " + row.Low + " \t\t " + row.q1+ " \t\t " + row.md + " \t\t " + row.q3 + " \t\t " + row.high)
	}
	fmt.Println("using latency data from region: %s", data[5].Source)
}
