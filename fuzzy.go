package main

import (
	"crypto/aes"
	"crypto/cipher"
	"encoding/base64"
	"fmt"
	"io/ioutil"
	"log"
	"strings"
)

func decryptConfigFile(keyPath, configPath string) (map[string]string, error) {
	// Read the encoded key from keys.txt
	keyBytes, err := ioutil.ReadFile(keyPath)
	if err != nil {
		return nil, fmt.Errorf("error reading key from keys.txt: %v", err)
	}

	// Decode the Base64-encoded key
	key, err := base64.StdEncoding.DecodeString(string(keyBytes))
	if err != nil {
		return nil, fmt.Errorf("error decoding key: %v", err)
	}

	// Read the encrypted configuration data from config.txt
	configBytes, err := ioutil.ReadFile(configPath)
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

	// Print the decrypted configuration
	fmt.Println("Decrypted Configuration:")
	for key, value := range configDict {
		fmt.Printf("%s=%s\n", key, value)
	}
}
