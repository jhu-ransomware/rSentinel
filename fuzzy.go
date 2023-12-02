package main

import (
	"fmt"
	"io/fs"
	"log"
	"os"
	"path/filepath"
	"regexp"
	"sync"

	"github.com/eciavatta/sdhash"
)

const defaultPath = `C:\Users\rSUser\Documents`

var mu sync.Mutex

func calculateSimilarity(filename1, filename2 string, wg *sync.WaitGroup, ch chan int) {
	defer wg.Done()

	factoryA, err := sdhash.CreateSdbfFromFilename(filename1)
	if err != nil {
		log.Printf("Error creating sdbf for %s: %v\n", filename1, err)
		ch <- 0
		return
	}
	sdbfA := factoryA.Compute()

	factoryB, err := sdhash.CreateSdbfFromFilename(filename2)
	if err != nil {
		log.Printf("Error creating sdbf for %s: %v\n", filename2, err)
		ch <- 0
		return
	}
	sdbfB := factoryB.Compute()

	result, err := sdbfA.Compare(sdbfB)
	if err != nil {
		log.Printf("Error comparing %s and %s: %v\n", filename1, filename2, err)
		ch <- 0
		return
	}

	mu.Lock()
	defer mu.Unlock()

	if result >= 0 && result <= 2 {
		log.Printf("Dissimilarity between %s and %s: %d\n", filename1, filename2, result)
		ch <- 1
	} else {
		ch <- 0
	}
}

func checkFilesInDirectory(directory string) int {
	if _, err := os.Stat(directory); os.IsNotExist(err) {
		log.Printf("Error: Directory %s does not exist.\n", directory)
		os.Exit(1)
	}

	dissimilarCount := 0
	totalFileCount := 0
	similarFiles := make(map[string][]string)
	baseNameRegex := regexp.MustCompile(`^(.+?)\..+?$`)

	err := filepath.WalkDir(directory, func(path string, d fs.DirEntry, errWalk error) error {
		if errWalk != nil {
			return nil
		}
		if !d.IsDir() {
			baseName := baseNameRegex.ReplaceAllString(d.Name(), "$1")

			similarFiles[baseName] = append(similarFiles[baseName], path)

			fileInfo, errFileInfo := d.Info()
			if errFileInfo != nil {
				return nil
			}

			if fileInfo.Size() < 20*1024 || fileInfo.Size() > 200*1024*1024 {
				return nil
			}
		}
		return nil
	})

	if err != nil {
		return -1
	}

	processedPairs := make(map[string]bool)

	var wg sync.WaitGroup
	ch := make(chan int, 200)

	for _, files := range similarFiles {
		if len(files) < 2 {
			log.Println("Skipping group with less than two files.")
			continue
		}

		log.Println("Starting similarity checks...")

		for i, pathA := range files {
			for j := i + 1; j < len(files); j++ {
				pairKey := fmt.Sprintf("%s|%s", pathA, files[j])

				if _, processed := processedPairs[pairKey]; !processed {
					processedPairs[pairKey] = true

					log.Printf("Checking similarity between %s and %s\n", pathA, files[j])

					wg.Add(1)
					go calculateSimilarity(pathA, files[j], &wg, ch)
				}
			}
		}
	}

	go func() {
		wg.Wait()
		close(ch)
	}()

	for result := range ch {
		totalFileCount++
		dissimilarCount += result

		if totalFileCount == 200 {
			dissimilarityThreshold := 0.6
			ratio := float64(dissimilarCount) / float64(totalFileCount)
			log.Printf("Dissimilar Count: %d, Total File Count: %d\n", dissimilarCount, totalFileCount)

			if ratio >= dissimilarityThreshold {
				return 1
			}
		}
	}

	if totalFileCount > 0 {
		dissimilarityThreshold := 0.6
		ratio := float64(dissimilarCount) / float64(totalFileCount)
		log.Printf("Dissimilar Count: %d, Total File Count: %d\n", dissimilarCount, totalFileCount)

		if ratio >= dissimilarityThreshold {
			return 1
		}
	}

	return 0
}

func main() {
	directory := defaultPath
	result := checkFilesInDirectory(directory)
	fmt.Printf("Result: %d\n", result)
}
