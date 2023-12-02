package main

import (
	"fmt"
	"log"
	"math/rand"
	"os"
	"regexp"
	"runtime"
	"sync"
	"sync/atomic"
	"time"

	"github.com/eciavatta/sdhash"
)

const defaultPath = `C:\Users\rSUser\Documents`
const sampleSize = 100    // Adjust the sample size as needed
const maxTotalFiles = 200 // Maximum total files to check

func calculateSimilarity(filename1, filename2 string, wg *sync.WaitGroup, resultChan chan<- int) {
	defer wg.Done()

	factoryA, err := sdhash.CreateSdbfFromFilename(filename1)
	if err != nil {
		log.Printf("Error creating Sdbf for %s: %v\n", filename1, err)
		resultChan <- 0 // Signal that an error occurred
		return
	}
	sdbfA := factoryA.Compute()

	factoryB, err := sdhash.CreateSdbfFromFilename(filename2)
	if err != nil {
		log.Printf("Error creating Sdbf for %s: %v\n", filename2, err)
		resultChan <- 0 // Signal that an error occurred
		return
	}
	sdbfB := factoryB.Compute()

	similarity := sdbfA.Compare(sdbfB)

	if similarity >= 0 && similarity <= 2 {
		resultChan <- 1 // Signal that a dissimilar pair is found
	} else {
		resultChan <- 0 // Signal that the pair is not dissimilar
	}
}

func checkFilesInDirectory(directory string) int {
	// Check if the directory exists
	if _, err := os.Stat(directory); os.IsNotExist(err) {
		log.Printf("Error: Directory %s does not exist.\n", directory)
		os.Exit(1)
	}

	// Create a map to store similar file names
	similarFiles := make(map[string][]string)

	// Define a regular expression to extract base name
	baseNameRegex := regexp.MustCompile(`^(.+?)\..+?$`)

	var wg sync.WaitGroup
	resultChan := make(chan int)

	// Randomly sample files for comparison
	rand.Seed(time.Now().UnixNano())
	totalFiles := 0 // Counter for the total number of files checked

	for _, files := range similarFiles {
		if len(files) >= 2 {
			sample := make([]string, sampleSize)
			for i := 0; i < sampleSize; i++ {
				sample[i] = files[rand.Intn(len(files))]
			}

			for i, pathA := range sample {
				for j := i + 1; j < len(sample); j++ {
					// Increment the total files counter
					atomic.AddInt32(&totalFiles, 1)

					wg.Add(1)
					go func(pathA, pathB string) {
						defer wg.Done()

						similarity, err := calculateSimilarity(pathA, pathB)
						if err != nil {
							log.Println("Error calculating similarity:", err)
							return
						}

						if similarity >= 0 && similarity <= 2 {
							resultChan <- 1 // Signal that a dissimilar pair is found
						} else {
							resultChan <- 0 // Signal that the pair is not dissimilar
						}
					}(pathA, sample[j])

					// Check if the maximum total files is reached
					if atomic.LoadInt32(&totalFiles) >= maxTotalFiles {
						break
					}
				}

				// Check if the maximum total files is reached
				if atomic.LoadInt32(&totalFiles) >= maxTotalFiles {
					break
				}
			}

			// Check if the maximum total files is reached
			if atomic.LoadInt32(&totalFiles) >= maxTotalFiles {
				break
			}
		}
	}

	go func() {
		wg.Wait()
		close(resultChan)
	}()

	dissimilarCount := 0
	for result := range resultChan {
		if result == 1 {
			dissimilarCount++
		}
	}

	dissimilarityThreshold := 0.6
	log.Printf("Dissimilar Count: %d, Sample Size: %d\n", dissimilarCount, sampleSize)
	if float64(dissimilarCount)/float64(sampleSize) >= dissimilarityThreshold {
		return 1
	}
	return 0
}

func main() {
	runtime.GOMAXPROCS(runtime.NumCPU()) // Utilize all available CPU cores

	// Use the default path if no command-line argument is provided
	directory := defaultPath

	// Alternatively, you can check if a command-line argument is provided and use it if available
	// if len(os.Args) == 2 {
	// 	directory = os.Args[1]
	// }

	result := checkFilesInDirectory(directory)

	// Print the result instead of using os.Exit
	fmt.Printf("Result: %d\n", result)
}
