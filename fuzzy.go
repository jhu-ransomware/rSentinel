package main

import (
	"crypto/aes"
	"crypto/cipher"
	"encoding/base64"
	"fmt"
	"log"
	"os"
	"path/filepath"
	"strings"

	"github.com/eciavatta/sdhash"
)

func calculateFuzzyHashSimilarity(filename1, filename2 string) (float64, error) {
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

	// Convert the integer similarity score to float64
	return float64(sdbfA.Compare(sdbfB)), nil
}

func checkSimilarFiles(filePath string, processedPairs map[string]bool) int {
	baseName := filepath.Base(filePath)
	fmt.Printf("Processing file with base name: %s\n", baseName)

	// Get the directory of the file
	dir := filepath.Dir(filePath)

	// List all files in the same directory
	files, err := os.ReadDir(dir)
	if err != nil {
		log.Printf("Error reading directory: %v", err)
		return 0
	}

	// Print the list of files in the directory
	fmt.Println("Files in the directory:")
	for _, file := range files {
		fmt.Println(file.Name())
	}

	// Filter files with the same base name (ignoring extensions)
	sameBaseNameFiles := make([]string, 0)
	for _, file := range files {
		if file.IsDir() {
			continue
		}
		fileBaseName := strings.TrimSuffix(file.Name(), filepath.Ext(file.Name()))
		if fileBaseName == baseName && file.Name() != filepath.Base(filePath) {
			sameBaseNameFiles = append(sameBaseNameFiles, filepath.Join(dir, file.Name()))
		}
	}

	// Check fuzzy hash similarity for each file
	for _, otherFilePath := range sameBaseNameFiles {
		// Check if the pair has already been processed
		pairKey := fmt.Sprintf("%s-%s", filePath, otherFilePath)
		if processedPairs[pairKey] {
			continue
		}

		log.Printf("Checking fuzzy hash similarity between %s and %s\n", filePath, otherFilePath)

		// Calculate fuzzy hash similarity
		score, err := calculateFuzzyHashSimilarity(filePath, otherFilePath)
		if err != nil {
			log.Printf("Error calculating fuzzy hash similarity: %v", err)
			continue
		}

		log.Printf("Fuzzy hash similarity score between %s and %s: %f\n", filePath, otherFilePath, score)

		// Print the result for each file
		if score <= 3 && score >= 0 {
			fmt.Printf("Result: Dissimilar files found - %s and %s\n", filePath, otherFilePath)
			// Mark the pair as processed
			processedPairs[pairKey] = true
			return 1
		} else {
			fmt.Printf("Result: Similar files found between %s and %s\n", filePath, otherFilePath)
		}
	}

	// Print the result if no matching files with similar fuzzy hash are found
	fmt.Println("Result: No similar files found")
	return 0
}

func decryptConfigFile(keyPath, configPath string) (map[string]string, error) {
	// Read the encoded key from keys.txt
	keyBytes, err := os.ReadFile(keyPath)
	if err != nil {
		return nil, fmt.Errorf("error reading key from keys.txt: %v", err)
	}

	// Decode the Base64-encoded key
	key, err := base64.StdEncoding.DecodeString(string(keyBytes))
	if err != nil {
		return nil, fmt.Errorf("error decoding key: %v", err)
	}

	// Read the encrypted configuration data from config.txt
	configBytes, err := os.ReadFile(configPath)
	if err != nil {
		return nil, fmt.Errorf("error reading config.txt: %v", err)
	}

	// Extract IV and ciphertext
	iv := configBytes[:aes.BlockSize]
	ciphertext := configBytes[aes.BlockSize:]

	// Create a new AES cipher block with the key
	block, err := aes.NewCipher(key)
	if err != nil {
		return nil, fmt.Errorf("error creating AES cipher: %v", err)
	}

	// Create a cipher.NewCBCDecrypter with the AES block and IV
	mode := cipher.NewCBCDecrypter(block, iv)

	// Decrypt the ciphertext
	mode.CryptBlocks(ciphertext, ciphertext)

	// Unpad the decrypted data
	unpaddedData, err := unpad(ciphertext)
	if err != nil {
		return nil, fmt.Errorf("error unpadding data: %v", err)
	}

	// Convert the decrypted data to a string
	configStr := string(unpaddedData)

	// Parse the configuration string into a map
	configDict := make(map[string]string)
	lines := strings.Split(configStr, "\n")
	for _, line := range lines {
		if strings.Contains(line, "=") {
			parts := strings.Split(line, "=")
			key := strings.TrimSpace(parts[0])
			value := strings.TrimSpace(parts[1])
			configDict[key] = value
		}
	}

	return configDict, nil
}

func unpad(data []byte) ([]byte, error) {
	padding := int(data[len(data)-1])
	if padding > aes.BlockSize || padding == 0 {
		return nil, fmt.Errorf("invalid padding")
	}
	return data[:len(data)-padding], nil
}

func main() {
	keyPath := "keys.txt"
	configPath := "config.txt"

	configDict, err := decryptConfigFile(keyPath, configPath)
	if err != nil {
		log.Fatalf("Error decrypting config.txt: %v", err)
	}

	// Get the file paths from config
	pdfPaths := make([]string, 3)
	pdfPaths[0] = strings.TrimSpace(configDict["PDF_PATH_0"])
	pdfPaths[1] = strings.TrimSpace(configDict["PDF_PATH_1"])
	pdfPaths[2] = strings.TrimSpace(configDict["PDF_PATH_2"])

	docxPaths := make([]string, 2)
	docxPaths[0] = strings.TrimSpace(configDict["DOCX_PATH_1"])
	docxPaths[1] = strings.TrimSpace(configDict["DOCX_PATH_2"])

	// Check for encrypted files for each PDF path
	processedPairs := make(map[string]bool)
	totalResult := 0
	for _, pdfPath := range pdfPaths {
		result := checkSimilarFiles(pdfPath, processedPairs)
		totalResult += result
	}

	// Check for encrypted files for each DOCX path
	for _, docxPath := range docxPaths {
		result := checkSimilarFiles(docxPath, processedPairs)
		totalResult += result
	}

	// Check if 4 out of 5 files have disimilar fuzzy hash
	if totalResult >= 4 {
		fmt.Println("Final Result: 1")
	} else {
		fmt.Println("Final Result: 0")
	}
}
