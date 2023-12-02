package main

import (
	"bufio"
	"fmt"
	"io/fs"
	"log"
	"os"
	"path/filepath"
	"regexp"
	"strings"

	"github.com/eciavatta/sdhash"
)

const defaultPath = `C:\Users\rSUser\Documents`
const dissimilarityThreshold = 0.6

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

func checkFilesInDirectory(directory string, privateKey string) int {
	// Read and decrypt the contents of config.txt using the private key
	configFilePath := "config.txt"
	configContents, err := decryptConfigFile(configFilePath, privateKey)
	if err != nil {
		log.Println("Error decrypting config.txt:", err)
		return -1
	}

	// Extract file paths from config contents
	var filePaths []string
	scanner := bufio.NewScanner(strings.NewReader(configContents))
	for scanner.Scan() {
		line := scanner.Text()
		if strings.HasPrefix(line, "PDF_PATH") || strings.HasPrefix(line, "DOCX_PATH") {
			parts := strings.Split(line, "=")
			if len(parts) == 2 {
				filePaths = append(filePaths, strings.TrimSpace(parts[1]))
			}
		}
	}

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
	baseNameRegex := regexp.MustCompile(`^(.+)\.[^.]+$`)

	err = filepath.WalkDir(directory, func(path string, d fs.DirEntry, errWalk error) error {
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

	// Iterate over the file paths from config.txt
	for _, configFilePath := range filePaths {
		// Iterate over similar files with the same base name
		for _, files := range similarFiles {
			if len(files) < 2 {
				log.Println("Skipping group with less than two files.")
				continue
			}

			log.Println("Starting similarity checks...")

			for i, pathA := range files {
				// Check if the current file path matches the one from config.txt
				if pathA == configFilePath {
					for j := i + 1; j < len(files); j++ {
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

						// Check if 3 out of 5 files have been processed
						if totalFileCount == 5 {
							ratio := float64(dissimilarCount) / float64(totalFileCount)
							log.Printf("Dissimilar Count: %d, Total File Count: %d\n", dissimilarCount, totalFileCount)

							// Return 1 if the dissimilarity ratio is greater than or equal to the threshold
							if ratio >= dissimilarityThreshold {
								return 1
							} else {
								// Return 0 if the dissimilarity ratio is below the threshold
								return 0
							}
						}
					}
				}
			}
		}
	}

	// Return 0 if the dissimilarity ratio is below the threshold after processing all files
	return 0
}

// Function to decrypt the contents of the config file
func decryptConfigFile(configFilePath, privateKey string) (string, error) {
	// Implement your decryption logic using the provided private key
	// You can use cryptographic libraries or methods to decrypt the file
	// Return the decrypted contents as a string
	return "", nil
}

func main() {
	directory := defaultPath
	privateKey := readPrivateKey("keys.txt")
	result := checkFilesInDirectory(directory, privateKey)
	fmt.Printf("Result: %d\n", result)
}

// Function to read the private key from keys.txt
func readPrivateKey(keysFilePath string) string {
	privateKey, err := os.ReadFile(keysFilePath)
	if err != nil {
		log.Fatalf("Error reading private key from keys.txt: %v", err)
	}
	return string(privateKey)
}
