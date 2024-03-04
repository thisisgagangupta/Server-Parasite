package main

import (
	"bufio"
	"flag"
	"fmt"
	"log"
	"net/http"
	"os"
	"strings"
	"sync"
)

const (
	userAgent   = "Mozilla/5.0 (iPhone; CPU iPhone OS 7_0_1 like Mac OS X) AppleWebKit/537.51.1 (KHTML, like Gecko) Version/7.0 Mobile/11A470a Safari/9537.53"
	pathF       = "files"
	extensions  = "extensions.txt"
	files       = "files.txt"
	folders     = "folders.txt"
	concurrency = 10 // Number of concurrent HTTP requests
)

var foundedFolders []string

func getStatusCode(url string) (string, error) {
	resp, err := http.Get(url)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()
	return resp.Status, nil
}

func scanFilesWorker(fndPTHS string, wg *sync.WaitGroup) {
	defer wg.Done()
	fileslist, err := os.Open(pathF + "/files.txt")
	if err != nil {
		log.Printf("Error opening files list: %s\n", err)
		return
	}
	defer fileslist.Close()

	scanner := bufio.NewScanner(fileslist)
	for scanner.Scan() {
		extensionss, err := os.Open(pathF + "/extensions.txt")
		if err != nil {
			log.Printf("Error opening extensions list: %s\n", err)
			return
		}
		defer extensionss.Close()

		extScanner := bufio.NewScanner(extensionss)
		for extScanner.Scan() {
			url := fmt.Sprintf("%s/%s%s", fndPTHS, scanner.Text(), extScanner.Text())
			status, err := getStatusCode(url)
			if err != nil {
				log.Printf("Error checking URL %s: %s\n", url, err)
				continue
			}
			if status == "200" || status == "301" || status == "302" || status == "304" || status == "307" || status == "403" {
				fmt.Printf("* Founded: %s | Response Code: %s\n", url, status)
				foundedFolders = append(foundedFolders, url)
			} else {
				fmt.Printf("Checking: %s | Response Code: %s\n", url, status)
			}
		}
	}
}

func scanFiles(fndPTHS string) {
	var wg sync.WaitGroup
	wg.Add(concurrency)
	for i := 0; i < concurrency; i++ {
		go func() {
			defer wg.Done()
			scanFilesWorker(fndPTHS, &wg)
		}()
	}
	wg.Wait()
}

func scanPath(filename string, hostname string) {
	file, err := os.Open(pathF + "/" + filename)
	if err != nil {
		log.Fatalf("Error opening file %s: %s\n", filename, err)
	}
	defer file.Close()

	scanner := bufio.NewScanner(file)
	fmt.Println("\n************* Starting Scan Backups PATHS *************\n")
	for scanner.Scan() {
		url := fmt.Sprintf("%s/%s", hostname, scanner.Text())
		status, err := getStatusCode(url)
		if err != nil {
			log.Printf("Error checking URL %s: %s\n", url, err)
			continue
		}
		if status == "200" || status == "301" || status == "302" || status == "304" || status == "307" || status == "403" {
			fmt.Printf("* Founded: %s | Response Code: %s\n", url, status)
			foundedFolders = append(foundedFolders, url)
			scanFiles(url)
		} else {
			fmt.Printf("Checking: %s | Response Code: %s\n", url, status)
		}
	}
	fmt.Println("\nPath Scanning Ended.\n")
}

func main() {
	hostname := flag.String("hostname", "", "Please input hostname")
	flag.Parse()

	if *hostname == "" {
		log.Fatalln("Hostname is required. Please provide a hostname using the -hostname flag.")
	}

	// Add protocol scheme if not provided
	if !strings.HasPrefix(*hostname, "http://") && !strings.HasPrefix(*hostname, "https://") {
		*hostname = "http://" + *hostname
	}

	fmt.Println(`
	Backup Directories & Backup Files Scanner.
	Host: ` + *hostname + `
	`)

	scanPath(folders, *hostname)
}
