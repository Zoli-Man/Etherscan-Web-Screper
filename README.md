This web scraper interacts with the Etherscan API to retrieve and filter transaction data from the Ethereum blockchain.

It allows users to specify criteria such as the minimum transaction value and currency type (USD or ETH) to filter the transactions.

It utilizes command-line arguments for user input.

$~$
$~$

To use the provided code, follow these steps:

1.Downlode the .env, requirements.txt and the transaction_filter.py files to the same directory.
 
$~$
$~$

2.Edit the .env file by entering your key
'''
API_KEY=your_api_key. 
'''
Make sure to replace "your api key" with your actual API key.

$~$
$~$

4.Open a terminal or command prompt and navigate to the directory where the files are located.

$~$
$~$

5.Install the necessary libraries by running:
```
pip install -r requirements.txt
```
$~$
$~$

6.Run the script with the desired command-line arguments. Here are the available options:

  -h, --help  
  show this help message and exit
  
  -a AMOUNT, --amount AMOUNT   
                        Amount used to filter transactions
                        
  -c {USD,ETH}, --currency {USD,ETH}   
                        currency to filter by(USD or ETH)
                        
  -b BLOCK, --block BLOCK   
                        Last block number to get information
                        
  -n NUM_BLOCKS, --num_blocks NUM_BLOCKS  
                        Number of blocks to retrieve information from
                        
  -o OUTPUT, --output OUTPUT  
                        Output file name

Example usage:
```
python transaction_filter.py -a 1 -c USD -b 1000000 -n 10 -o output_file
python transaction_filter.py
python transaction_filter.py -h
```
$~$
$~$

note:
You don’t have to provide all arguments.

If arguments are not provided, a default argument will be selected.

Running python transaction_filter.py will extract the last block and filter transactions with vale 1 EHT or higher.

$~$
$~$

7.Wait for the run to complete (it took me a bit time because I have a free api key and it has a small limit of api calls per second)

$~$
$~$

8.find your result at the csv file in same directory 

Make sure you have an active internet connection and the necessary API key for the Etherscan API to fetch the required data.
