package main

import (
	"fmt"
	"io/fs"
	"log"
	"os"
	"path/filepath"
	"regexp"

	"github.com/eciavatta/sdhash"
)

const defaultPath = `C:\Users\rSUser\Documents`

func calculateSimilarity(filename1, filename2 string) (int, error) {
	factoryA, err := sdhash.CreateSdbfFromFilename(filename1)
	if err != nil {
		return 0, err
	}
	sdbfA := factoryA.Compute()

	factoryB, err := sdhash.CreateSdbfFromFilename(filename2)
	if err != nil {
		return 0, err
	}
	sdbfB := factoryB.Compute()

	return sdbfA.Compare(sdbfB), nil
}

func checkFilesInDirectory(directory string) int {
	// Check if the directory exists
	if _, err := os.Stat(directory); os.IsNotExist(err) {
		log.Printf("Error: Directory %s does not exist.\n", directory)
		os.Exit(1)
	}
	dissimilarCount := 0
	totalFileCount := 0
	// Create a map to store similar file names
	similarFiles := make(map[string][]string)

	// Define a regular expression to extract base name
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

					similarity, errSimilarity := calculateSimilarity(pathA, files[j])
					if errSimilarity != nil {
						log.Println("Error calculating similarity:", errSimilarity)
						continue
					}

					totalFileCount++

					if similarity >= 0 && similarity <= 2 {
						log.Printf("Dissimilarity between %s and %s: %d\n", pathA, files[j], similarity)
						dissimilarCount++
					}

					// Check if 200 files have been processed
					if totalFileCount == 200 {
						dissimilarityThreshold := 0.6
						ratio := float64(dissimilarCount) / float64(totalFileCount)
						log.Printf("Dissimilar Count: %d, Total File Count: %d\n", dissimilarCount, totalFileCount)

						// Return 1 if the dissimilarity ratio is greater than or equal to the threshold
						if ratio >= dissimilarityThreshold {
							return 1
						}
					}
				}
			}
		}
	}

	// Check if the ratio is greater than or equal to the threshold for less than 200 files
	if totalFileCount > 0 {
		dissimilarityThreshold := 0.6
		ratio := float64(dissimilarCount) / float64(totalFileCount)
		log.Printf("Dissimilar Count: %d, Total File Count: %d\n", dissimilarCount, totalFileCount)

		// Return 1 if the dissimilarity ratio is greater than or equal to the threshold
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
