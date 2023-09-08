# Candy Machine v1 Minting CLI

## Overview

This command-line application, developed in Python, empowers users to effortlessly mint NFTs from a Candy Machine v1 program on the Solana blockchain. By using this tool, you can expedite the minting process by directly interacting with the blockchain, eliminating the need for a frontend interface.

**Note:** Please be aware that this code is currently outdated as of September 2023. Some libraries have changed, and it will not work unless you update specific libraries and parts of the code.

## Features

- **Efficient Minting:** Mint NFTs quickly and efficiently, significantly reducing wait times compared to using a frontend.
- **Configuration File:** Customize your minting experience by providing your wallet's private keys, specifying the Candy Machine v1 address, defining the number of NFTs to mint, selecting a Solana API endpoint to avoid rate limits, and setting a maximum price threshold.

## Configuration

To configure the application, follow these steps:

1. Edit the `config.json` file:
   - Provide your wallet's private keys.
   - Specify the Candy Machine v1 address you want to mint from.
   - Set the number of NFTs you want to mint.
   - Optionally, define a Solana API endpoint to avoid rate limits.
   - Set a maximum price threshold to prevent minting if the price exceeds this limit.

## Contribution

Contributions are highly encouraged! If you have any suggestions or improvements, please don't hesitate to open an issue or create a pull request on this GitHub repository.

## License

This project is licensed under the MIT License. For more details, please refer to the [LICENSE](LICENSE) file.

**Note:** Always exercise caution when handling private keys and sensitive information. Keep your private keys secure and avoid sharing them publicly.