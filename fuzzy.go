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
	dissimilarCount := 0
	totalFileCount := 0

	// Create a map to store similar file names
	similarFiles := make(map[string][]string)

	// Define a regular expression to extract base name
	baseNameRegex := regexp.MustCompile(`^(.+?)\..+?$`)

	err := filepath.WalkDir(directory, func(path string, d fs.DirEntry, errWalk error) error {
		if errWalk != nil {
			log.Printf("Error accessing %s: %v\n", path, errWalk)
			return nil
		}
		if !d.IsDir() {
			// Get the base name without considering multiple extensions
			baseName := baseNameRegex.ReplaceAllString(d.Name(), "$1")

			// Log the base name and extension for debugging
			log.Printf("File: %s, Base Name: %s\n", d.Name(), baseName)

			// Add the file to the similarFiles map
			similarFiles[baseName] = append(similarFiles[baseName], path)

			// Get the file info
			fileInfo, errFileInfo := d.Info()
			if errFileInfo != nil {
				log.Printf("Error getting file info for %s: %v\n", path, errFileInfo)
				return nil
			}

			// Skip files smaller than 20 KB or larger than 200 MB
			if fileInfo.Size() < 20*1024 || fileInfo.Size() > 200*1024*1024 {
				log.Printf("Skipping file %s due to size restrictions (size: %d bytes)\n", path, fileInfo.Size())
				return nil
			}
		}
		return nil
	})

	if err != nil {
		log.Printf("Error walking the directory: %v\n", err)
		return -1
	}

	// Processed pairs map for tracking
	processedPairs := make(map[string]bool)

	// Iterate over the similarFiles map
	for _, files := range similarFiles {
		if len(files) < 2 {
			// Skip groups with only one file
			log.Println("Skipping group with less than two files.")
			continue
		}

		log.Println("Starting similarity checks...")

		for i, pathA := range files {
			for j := i + 1; j < len(files); j++ {
				// Generate a unique key for the pair
				pairKey := fmt.Sprintf("%s|%s", pathA, files[j])

				// Check if the pair has already been processed
				if _, processed := processedPairs[pairKey]; !processed {
					processedPairs[pairKey] = true

					// Log the files being checked
					log.Printf("Checking similarity between %s and %s\n", pathA, files[j])

					// Compare a and b file names
					similarity, errSimilarity := calculateSimilarity(pathA, files[j])
					if errSimilarity != nil {
						log.Println("Error calculating similarity:", errSimilarity)
						// Handle the error as needed (e.g., return, continue with the next pair, etc.)
						continue
					}

					// log.Printf("Similarity between %s and %s: %d\n", pathA, files[j], similarity)
					totalFileCount++ // Increment totalFileCount for every pair of files compared

					if similarity >= 0 && similarity <= 2 {
						log.Printf("Dissimilarity between %s and %s: %d\n", pathA, files[j], similarity)
						dissimilarCount++
					}
				}
			}
		}
	}

	dissimilarityThreshold := 0.4
	log.Printf("Dissimilar Count: %d, Total File Count: %d\n", dissimilarCount, totalFileCount)
	if float64(dissimilarCount)/float64(totalFileCount) >= dissimilarityThreshold {
		return 1
	}
	return 0
}

func main() {
	if len(os.Args) != 2 {
		log.Println("Usage: go run main.go /path/to/check")
		return
	}

	directory := os.Args[1]
	result := checkFilesInDirectory(directory)

	// Print the result instead of using os.Exit
	fmt.Print(result)
}
